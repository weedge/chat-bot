from abc import abstractmethod
import logging
from typing import AsyncGenerator

from apipeline.pipeline.pipeline import FrameDirection

from src.processors.ai_processor import AIProcessor
from types.frames.data_frames import Frame, TextFrame


class ImageGenProcessor(AIProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Renders the image. Returns an Image object.
    @abstractmethod
    async def run_image_gen(self, prompt: str) -> AsyncGenerator[Frame, None]:
        pass

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TextFrame):
            await self.push_frame(frame, direction)
            await self.start_processing_metrics()
            await self.process_generator(self.run_image_gen(frame.text))
            await self.stop_processing_metrics()
        else:
            await self.push_frame(frame, direction)

