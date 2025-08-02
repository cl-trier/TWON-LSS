import typing

import pydantic
import numpy

import huggingface_hub


class Message(pydantic.BaseModel):
    role: typing.Literal["system", "user", "assistant"]
    content: str


class Chat(pydantic.RootModel):
    root: typing.List[Message]


class LLM(pydantic.BaseModel):
    """
    The `LLM` class provides a unified interface for interacting with language models through the Hugging Face Hub API.
    It supports text generation, embedding creation, similarity computation, and text classification tasks. The class wraps
    the Hugging Face InferenceClient to provide convenient methods for common language model operations.

    Attributes:
        client (huggingface_hub.InferenceClient): The Hugging Face inference client for API interactions.
        model (str): The model identifier/name to use for inference operations.

    """

    client: huggingface_hub.InferenceClient
    model: str

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def generate(self, chat: "Chat") -> str:
        return (
            self.client.chat.completions.create(
                model=self.model, messages=chat.model_dump()
            )
            .choices[0]
            .message.content
        )

    def embed(self, text: str) -> numpy.ndarray:
        return self.client.feature_extraction(text)

    def similarity(self, text: str, references: typing.List[str]) -> typing.List[float]:
        return self.client.sentence_similarity(text, references)

    def classification(
        self, text: str
    ) -> typing.List[huggingface_hub.TextClassificationOutputElement]:
        return self.client.text_classification(text)
