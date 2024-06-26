
from abc import ABC, abstractmethod
from typing import Iterator, AsyncGenerator, Generator


class IModel(ABC):
    @abstractmethod
    def load_model(self, **kwargs):
        raise NotImplemented("must be implemented in the child class")


class IRecorder(ABC):
    @abstractmethod
    def record_audio(self, session) -> list[bytes]:
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def close(self):
        raise NotImplemented("must be implemented in the child class")


class IBuffering(ABC):
    @abstractmethod
    def process_audio(self, session):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def is_voice_active(self, session):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def insert(self, audio_data):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def clear(self):
        raise NotImplemented("must be implemented in the child class")


class IDetector(ABC):
    @abstractmethod
    async def detect(self, session):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def set_audio_data(self, audio_data):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def get_sample_info(self):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def close(self):
        raise NotImplemented("must be implemented in the child class")


class IAsr(ABC):
    @abstractmethod
    async def transcribe(self, session) -> dict:
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def set_audio_data(self, audio_data):
        raise NotImplemented("must be implemented in the child class")


class IHallucination(ABC):
    @abstractmethod
    def check(self, session) -> bool:
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def filter(self, session) -> str:
        raise NotImplemented("must be implemented in the child class")


class ILlm(ABC):
    @abstractmethod
    def generate(self, session) -> Iterator[str]:
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def chat_completion(self, session) -> Iterator[str]:
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def count_tokens(self, text: str | bytes):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def model_name(self):
        raise NotImplemented("must be implemented in the child class")


class IFunction(ABC):
    @abstractmethod
    def excute(self, session):
        raise NotImplemented("must be implemented in the child class")


class ITts(ABC):
    @abstractmethod
    def synthesize_sync(self, session) -> Generator[bytes, None, None]:
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    async def synthesize(self, session) -> AsyncGenerator[bytes, None]:
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def get_stream_info(self) -> dict:
        raise NotImplemented("must be implemented in the child class")


class IPlayer(ABC):
    @abstractmethod
    def start(self, session):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def play_audio(self, session):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def pause(self):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def resume(self):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def stop(self, session):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def close(self):
        raise NotImplemented("must be implemented in the child class")


class IConnector(ABC):
    @abstractmethod
    def send(self, data, at: str):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def recv(self, at: str):
        raise NotImplemented("must be implemented in the child class")

    @abstractmethod
    def close(self):
        raise NotImplemented("must be implemented in the child class")
