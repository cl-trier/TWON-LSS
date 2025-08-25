import logging
import requests
import typing

import pydantic


class Message(pydantic.BaseModel):
    role: typing.Literal["system", "user", "assistant"]
    content: str


class Chat(pydantic.RootModel):
    root: typing.List[Message]


class LLM(pydantic.BaseModel):
    api_key: str

    model: str = "Qwen/Qwen3-4B-Instruct-2507:nscale"
    url: str = "https://router.huggingface.co/v1/chat/completions"

    def _query(self, payload):
        headers: dict = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.url, headers=headers, json=payload)
        return response.json()

    def generate(self, chat: Chat, max_retries: int = 1) -> str:
        try:
            response: str = self._query(
                {
                    "messages": chat.model_dump(),
                    "model": self.model,
                }
            )["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to query LLM: {e}")
            if max_retries > 0:
                return self.generate(chat, max_retries - 1)
            raise RuntimeError("Failed to generate response from LLM after retries") from e
        
        return response

    def similarity(self, text: str, references: typing.List[str]) -> typing.List[float]:
        if self.url == "https://router.huggingface.co/v1/chat/completions":
            raise ValueError("Similarity endpoint not supported for chat completions API. Use HF-Inference URL that includs endpoint and model for similarity")
        
        return self._query(
            {
                "inputs": {"source_sentence": text, "sentences": references},
            }
        )
