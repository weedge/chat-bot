import base64
import json
import os
import logging
from typing import List


try:
    from openai import AsyncOpenAI, AsyncStream, DefaultAsyncHttpxClient
    from openai.types.chat import (
        ChatCompletionChunk,
        ChatCompletionFunctionMessageParam,
        ChatCompletionMessageParam,
        ChatCompletionToolParam
    )
except ModuleNotFoundError as e:
    logging.error(f"Exception: {e}")
    logging.error(
        "In order to use OpenAI, you need to `pip install openai`. Also, set `OPENAI_API_KEY` environment variable.")
    raise Exception(f"Missing module: {e}")
import httpx
from apipeline.frames.data_frames import TextFrame, Frame
from apipeline.pipeline.pipeline import FrameDirection

from src.processors.aggregators.openai_llm_context import OpenAILLMContext, OpenAILLMContextFrame
from src.processors.llm.base import LLMProcessor
from src.types.frames.control_frames import LLMFullResponseEndFrame, LLMFullResponseStartFrame, LLMModelUpdateFrame
from src.types.frames.data_frames import LLMMessagesFrame, VisionImageRawFrame


class OpenAIUnhandledFunctionException(Exception):
    pass


class BaseOpenAILLMProcessor(LLMProcessor):
    """This is the base for all processors that use the AsyncOpenAI client.

    This processor consumes OpenAILLMContextFrame frames, which contain a reference
    to an OpenAILLMContext frame. The OpenAILLMContext object defines the context
    sent to the LLM for a completion. This includes user, assistant and system messages
    as well as tool choices and the tool, which is used if requesting function
    calls from the LLM.
    """

    def __init__(self, *, model: str, api_key="", base_url="", **kwargs):
        super().__init__(**kwargs)
        api_key = os.environ.get("OPENAI_API_KEY", api_key)
        self._model: str = model
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=DefaultAsyncHttpxClient(
                limits=httpx.Limits(
                    max_keepalive_connections=100,
                    max_connections=1000,
                    keepalive_expiry=None,
                )
            )
        )

    def can_generate_metrics(self) -> bool:
        return True

    async def get_chat_completions(
            self,
            context: OpenAILLMContext,
            messages: List[ChatCompletionMessageParam]) -> AsyncStream[ChatCompletionChunk]:
        chunks = await self._client.chat.completions.create(
            model=self._model,
            stream=True,
            messages=messages,
            tools=context.tools,
            tool_choice=context.tool_choice,
        )
        return chunks

    async def _stream_chat_completions(
            self, context: OpenAILLMContext) -> AsyncStream[ChatCompletionChunk]:
        logging.debug(f"Generating chat: {context.get_messages_json()}")

        messages: List[ChatCompletionMessageParam] = context.get_messages()

        # base64 encode any images
        for message in messages:
            if message.get("mime_type") == "image/jpeg":
                encoded_image = base64.b64encode(message["data"].getvalue()).decode("utf-8")
                text = message["content"]
                message["content"] = [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
                del message["data"]
                del message["mime_type"]

        chunks = await self.get_chat_completions(context, messages)

        return chunks

    async def _process_context(self, context: OpenAILLMContext):
        function_name = ""
        arguments = ""
        tool_call_id = ""

        await self.start_ttfb_metrics()

        chunk_stream: AsyncStream[ChatCompletionChunk] = (
            await self._stream_chat_completions(context)
        )

        async for chunk in chunk_stream:
            if len(chunk.choices) == 0:
                continue

            await self.stop_ttfb_metrics()

            if chunk.choices[0].delta.tool_calls:
                # We're streaming the LLM response to enable the fastest response times.
                # For text, we just yield each chunk as we receive it and count on consumers
                # to do whatever coalescing they need (eg. to pass full sentences to TTS)
                #
                # If the LLM is a function call, we'll do some coalescing here.
                # If the response contains a function name, we'll yield a frame to tell consumers
                # that they can start preparing to call the function with that name.
                # We accumulate all the arguments for the rest of the streamed response, then when
                # the response is done, we package up all the arguments and the function name and
                # yield a frame containing the function name and the arguments.

                tool_call = chunk.choices[0].delta.tool_calls[0]
                if tool_call.function and tool_call.function.name:
                    function_name += tool_call.function.name
                    tool_call_id = tool_call.id
                    await self.call_start_function(function_name)
                if tool_call.function and tool_call.function.arguments:
                    # Keep iterating through the response to collect all the argument fragments
                    arguments += tool_call.function.arguments
            elif chunk.choices[0].delta.content:
                await self.push_frame(TextFrame(chunk.choices[0].delta.content))

        # if we got a function name and arguments, check to see if it's a function with
        # a registered handler. If so, run the registered callback, save the result to
        # the context, and re-prompt to get a chat answer. If we don't have a registered
        # handler, raise an exception.
        if function_name and arguments:
            if self.has_function(function_name):
                await self._handle_function_call(context, tool_call_id, function_name, arguments)
            else:
                raise OpenAIUnhandledFunctionException(
                    f"The LLM tried to call a function named '{function_name}', but there isn't a callback registered for that function.")

    async def _handle_function_call(
            self,
            context: OpenAILLMContext,
            tool_call_id: str,
            function_name: str,
            arguments: str
    ):
        arguments = json.loads(arguments)
        result = await self.call_function(function_name, arguments)
        arguments = json.dumps(arguments)
        if isinstance(result, (str, dict)):
            # Handle it in "full magic mode"
            tool_call = ChatCompletionFunctionMessageParam({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call_id,
                        "function": {
                            "arguments": arguments,
                            "name": function_name
                        },
                        "type": "function"
                    }
                ]
            })
            context.add_message(tool_call)
            if isinstance(result, dict):
                result = json.dumps(result)
            tool_result = ChatCompletionToolParam({
                "tool_call_id": tool_call_id,
                "role": "tool",
                "content": result
            })
            context.add_message(tool_result)
            # re-prompt to get a human answer
            await self._process_context(context)
        elif isinstance(result, list):
            # reduced magic
            for msg in result:
                context.add_message(msg)
            await self._process_context(context)
        elif isinstance(result, type(None)):
            pass
        else:
            raise TypeError(f"Unknown return type from function callback: {type(result)}")

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        context = None
        if isinstance(frame, OpenAILLMContextFrame):
            context: OpenAILLMContext = frame.context
        elif isinstance(frame, LLMMessagesFrame):
            context = OpenAILLMContext.from_messages(frame.messages)
        elif isinstance(frame, VisionImageRawFrame):
            context = OpenAILLMContext.from_image_frame(frame)
        elif isinstance(frame, LLMModelUpdateFrame):
            logging.debug(f"Switching LLM model to: [{frame.model}]")
            self._model = frame.model
        else:
            await self.push_frame(frame, direction)

        if context:
            await self.push_frame(LLMFullResponseStartFrame())
            await self.start_processing_metrics()
            await self._process_context(context)
            await self.stop_processing_metrics()
            await self.push_frame(LLMFullResponseEndFrame())


class OpenAILLMProcessor(BaseOpenAILLMProcessor):
    TAG = "openai_llm_processor"

    def __init__(self, model: str = "gpt-4o", **kwargs):
        super().__init__(model=model, **kwargs)
