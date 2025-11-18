import logging
import requests
import typing
import time

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
    

    def generate(self, chat: Chat, max_retries: int = 3) -> str:
        try:
            response: str = self._query(
                {
                    "messages": chat.model_dump(),
                    "model": self.model,
                }
            )["choices"][0]["message"]["content"]
        
        except Exception as e:
            logging.error(f"Failed to query LLM: {e}")
            if max_retries > 0:
                time.sleep(60)
                return self.generate(chat, max_retries - 1)
            raise RuntimeError("Failed to generate response from LLM after retries") from e
        
        return response

    def extract(self, text: typing.Optional[typing.Union[str, list]], max_retries: int = 3):
        """
        Returns embeddings for either text or list of texts.
        """

        if self.url == "https://router.huggingface.co/v1/chat/completions":
            raise ValueError("Extract endpoint not supported for chat completions API. Use HF-Inference URL that includs endpoint and model for extract")
        
        try:
            return self._query({
                "inputs": text,
            })
        except Exception as e:
            logging.error(f"Failed to extract embeddings: {e}")
            if max_retries > 0:
                time.sleep(5)
                return self.extract(text, max_retries - 1)
            raise RuntimeError("Failed to extract embeddings after retries") from e
