import typing
import re
import enum
import logging

import pydantic

from twon_lss.interfaces import AgentInterface

from twon_lss.schemas import Post
from twon_lss.utility import LLM, Chat, Message


__all__ = ["Agent", "AgentInstructions"]


class AgentInstructions(pydantic.BaseModel):
    cognition: str
    read_prompt: str
    post_prompt: str
    feed_placeholder: str
    cognition_update: str


class WP3Agent(AgentInterface):
    llm: LLM
    instructions: AgentInstructions

    memory: typing.List[Message] = pydantic.Field(default_factory=list)
    memory_length: int = pydantic.Field(default=4, ge=0, le=50)

    theta: float = pydantic.Field(default=0.5, ge=0.0, le=1.0)
    cognition: str = pydantic.Field(default="")

    
    def select_actions(self, post: Post):
        pass

    def _append_to_memory(self, content: str, role="assistant") -> None:
        self.memory.append(Message(role=role, content=content))

    def _inference(self, prompt: str) -> Chat:
        return self.llm.generate(
            Chat(
                [
                    Message(role="system", content=self.cognition),
                    *self.memory[-self.memory_length * 2 :],
                    Message(role="user", content=prompt),
                ]
            )
        )

    # Actions
    def cognition_update(self) -> None:
        response: str = self._inference(self.instructions.cognition_update)
        logging.debug(f"Agent response: {response}")
        self.cognition = response


    def read(self, posts: list[Post]) -> str:
        """
        MISSING:
        - Likes???
        """

        feed_str = "\n".join(
            [f">{post.user.id}: {post.model_dump()['content']}" for post in posts]
        )
        response: str = self._inference(self.instructions.read_prompt + feed_str)
        logging.debug(f"Agent response: {response}")

        self._append_to_memory(self.instructions.feed_placeholder, role="user")
        self._append_to_memory(response)
        return response
        
    def post(self) -> str:     
        prompt = self.instructions.post_prompt
        response: str = self._inference(prompt)
        self._append_to_memory(prompt, role="user")
        self._append_to_memory(response)
        logging.debug(f"Agent response: {response}")

        return response
