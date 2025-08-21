import os
import requests
import typing

import pydantic


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

    model: str = "Qwen/Qwen3-4B-Instruct-2507:nscale"
    url: str = "https://router.huggingface.co/v1/chat/completions"
    api_key: str = os.environ["HF_TOKEN"]

    def _query(self, payload):
        headers: dict = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.url, headers=headers, json=payload)
        return response.json()

    def generate(self, chat: Chat) -> str:
        return (
            self._query(
                {
                    "messages": chat.model_dump(),
                    "model": self.model,
                }
            )
        )["choices"][0]["message"]["content"]

    def similarity(self, text: str, references: typing.List[str]) -> typing.List[float]:
        if self.url == "https://router.huggingface.co/v1/chat/completions":
            raise ValueError(
                "Similarity endpoint not supported for chat completions API. Use HF-Inference URL that includs endpoint and model for similarity"
            )

        return self._query(
            {
                "inputs": {"source_sentence": text, "sentences": references},
            }
        )
