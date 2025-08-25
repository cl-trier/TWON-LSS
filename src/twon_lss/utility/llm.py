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
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to query LLM: {e}")
            if max_retries > 0:
                time.sleep(5)
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
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to extract embeddings: {e}")
            if max_retries > 0:
                time.sleep(5)
                return self.extract(text, max_retries - 1)
            raise RuntimeError("Failed to extract embeddings after retries") from e


    @staticmethod
    def generate_username(llm, history):
        """Generate a username based on user's posting history"""
        
        # Create a sample of recent posts for context
        recent_posts = history[-5:] if len(history) >= 5 else history
        posts_text = " ".join([msg.get("content", "") for msg in recent_posts if msg.get("role") == "assistant"])

        # Truncate if too long
        if len(posts_text) > 500:
            posts_text = posts_text[:500] + "..."

        # Create chat messages for username generation
        chat_messages = [
            {"role": "system", "content": "Generate a creative username based on the user's posting style and interests. Keep it under 20 characters and make it appropriate for social media."},
            {"role": "user", "content": f"Based on these posts, generate a username: {posts_text}. Generate only the username!"}
        ]

        # Query the LLM
        response = llm._query({
            "messages": chat_messages,
            "model": llm.model,
        })

        return response["choices"][0]["message"]["content"].strip().replace("@", "").replace(" ", "_").replace("\"", "").replace("#", "").split("\n")[-1][:15]
