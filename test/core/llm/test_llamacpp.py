import os
import logging

import unittest

from src.common.factory import EngineFactory, EngineClass
from src.core.llm.llamacpp import LLamacppLLM
from src.common.logger import Logger
from src.common.session import Session
from src.common.types import SessionCtx, MODELS_DIR
from src.cmd.init import PromptInit
import src.core.llm

from dotenv import load_dotenv
load_dotenv(override=True)


r"""
python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_have_special_char

MODEL_TYPE=generate  python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_generate
MODEL_TYPE=generate STREAM=1 python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_generate

MODEL_TYPE=chat CHAT_FORMAT=chatml python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_chat_completion
MODEL_TYPE=chat CHAT_FORMAT=chatml STREAM=1 python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_chat_completion

MODEL_TYPE=chat-func \
    MODEL_NAME="functionary" \
    MODEL_PATH="./models/meetkai/functionary-small-v2.4-GGUF/functionary-small-v2.4.Q4_0.gguf" \
    TOKENIZER_PATH="./models/meetkai/functionary-small-v2.4-GGUF" \
    CHAT_FORMAT=functionary-v2 \
    python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_chat_completion

MODEL_TYPE=chat-func STREAM=1 \
    MODEL_NAME="functionary" \
    MODEL_PATH="./models/meetkai/functionary-small-v2.4-GGUF/functionary-small-v2.4.Q4_0.gguf" \
    TOKENIZER_PATH="./models/meetkai/functionary-small-v2.4-GGUF" \
    CHAT_FORMAT=functionary-v2 \
    python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_chat_completion

MODEL_TYPE=chat-func \
    MODEL_NAME="functionary" \
    MODEL_PATH="./models/meetkai/functionary-small-v2.4-GGUF/functionary-small-v2.4.Q4_0.gguf" \
    TOKENIZER_PATH="./models/meetkai/functionary-small-v2.4-GGUF" \
    CHAT_FORMAT=functionary-v2 \
    LLM_TOOL_CHOICE=auto \
    python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_chat_completion

MODEL_TYPE=chat-func PROMPT="查询下今日美股股价行情" \
    MODEL_NAME="functionary" \
    MODEL_PATH="./models/meetkai/functionary-small-v2.4-GGUF/functionary-small-v2.4.Q4_0.gguf" \
    TOKENIZER_PATH="./models/meetkai/functionary-small-v2.4-GGUF" \
    CHAT_FORMAT=functionary-v2 \
    LLM_TOOL_CHOICE=auto \
    python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_chat_completion

MODEL_TYPE=chat-func STREAM=1 PROMPT="查询下今日美股股价行情" \
    MODEL_NAME="functionary" \
    MODEL_PATH="./models/meetkai/functionary-small-v2.4-GGUF/functionary-small-v2.4.Q4_0.gguf" \
    TOKENIZER_PATH="./models/meetkai/functionary-small-v2.4-GGUF" \
    CHAT_FORMAT=functionary-v2 \
    LLM_TOOL_CHOICE=auto \
    python -m unittest test.core.llm.test_llamacpp.TestLLamacppLLM.test_chat_completion
"""


class TestLLamacppLLM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.llm_tag = os.getenv('LLM_TAG', "llm_llamacpp")
        cls.prompt = os.getenv('PROMPT', "你好")
        cls.stream = os.getenv('STREAM', "")
        cls.model_type = os.getenv('MODEL_TYPE', "generate")
        cls.chat_format = os.getenv('CHAT_FORMAT', None)
        cls.llm_tool_choice = os.getenv('LLM_TOOL_CHOICE', None)
        cls.model_name = os.getenv('MODEL_NAME', "qwen-2")
        cls.model_path = os.getenv('MODEL_PATH', os.path.join(
            MODELS_DIR, "qwen2-1_5b-instruct-q8_0.gguf"))
        cls.tokenizer_path = os.getenv('TOKENIZER_PATH', None)
        Logger.init(logging.DEBUG, is_file=False)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        kwargs = {}
        kwargs["verbose"] = True
        kwargs["model_name"] = self.model_name
        kwargs["model_path"] = self.model_path
        kwargs["tokenizer_path"] = self.tokenizer_path
        kwargs["model_type"] = self.model_type
        kwargs["chat_format"] = self.chat_format
        kwargs["llm_tool_choice"] = self.llm_tool_choice
        kwargs["n_threads"] = os.cpu_count()
        kwargs["n_gpu_layers"] = int(os.getenv('N_GPU_LAYERS', "0"))
        kwargs["flash_attn"] = bool(os.getenv('FLASH_ATTN', ""))
        kwargs["llm_stop"] = ["<|end|>", "<|im_end|>", "<s>", "</s>"]
        self.llm: LLamacppLLM = EngineFactory.get_engine_by_tag(
            EngineClass, self.llm_tag, **kwargs)
        self.session = Session(**SessionCtx("test_client_id").__dict__)

    def tearDown(self):
        pass

    def test_generate(self):
        self.llm.args.llm_stream = bool(self.stream)
        logging.debug(self.llm.args)
        self.assertEqual(self.llm.model_name(), self.llm.args.model_name)
        self.session.ctx.state["prompt"] = self.prompt
        logging.debug(self.session.ctx.state)
        iter = self.llm.generate(self.session)
        for item in iter:
            print(f"item--> {item}")
            self.assertGreater(len(item), 0)

    def test_have_special_char(self):
        index = self.llm._have_special_char("""'你好',中国""")
        print(index)
        self.assertGreater(index, -1)

    def test_generate_with_system(self):
        self.llm.args.llm_stream = bool(self.stream)
        logging.debug(self.llm.args)
        self.assertEqual(self.llm.model_name(), self.llm.args.model_name)
        history = []
        history.append(PromptInit.get_user_prompt(
            self.llm.model_name(), self.prompt))
        self.session.ctx.state["prompt"] = PromptInit.create_prompt(
            self.llm.model_name(), history, system_prompt="你是一个智能助手，回答请限制在1-5句话内。")
        logging.debug(self.session.ctx.state)
        iter = self.llm.generate(self.session)
        for item in iter:
            print(item)
            self.assertGreater(len(item), 0)

    def test_chat_completion(self):
        self.llm.args.llm_stream = bool(self.stream)
        self.llm.args.llm_chat_system = "你是一个中国人,请用中文回答。回答限制在1-5句话内。要友好、乐于助人且简明扼要。保持对话简短而甜蜜。只用纯文本回答，不要包含链接或其他附加内容。不要回复计算机代码以及数学公式。"
        self.session.ctx.state["prompt"] = self.prompt
        logging.debug(self.session.ctx)
        iter = self.llm.chat_completion(self.session)
        for item in iter:
            print(item)
            self.assertGreater(len(item), 0)
