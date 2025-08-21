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
    persona: str
    read_and_like_prompt: str
    post_prompt: str
    read_confirmation: str
    read_and_like_confirmation: str


class Agent(AgentInterface):
    llm: LLM
    instructions: AgentInstructions

    memory: typing.List[Message] = pydantic.Field(default_factory=list)
    memory_length: int = pydantic.Field(default=4, ge=0, le=50)

    def select_actions(self, post: Post):
        pass

    def _append_to_memory(self, content: str, role="assistant") -> None:
        self.memory.append(Message(role=role, content=content))

    def _inference(self, prompt: str) -> Chat:
        return self.llm.generate(
            Chat(
                [
                    Message(role="system", content=self.instructions.persona),
                    *self.memory[-self.memory_length * 2 :],
                    Message(role="user", content=prompt),
                ]
            )
        )


    def consume_and_rate(self, post: Post) -> bool:
        """
        Analyze the post and decide whether to like it or just read it
        """
        prompt = f"{self.instructions.read_and_like_prompt} '>{post.user.id}: {post.model_dump()['content']}'\nReply either with '{self.instructions.read_confirmation}' or '{self.instructions.read_and_like_confirmation}'"
        response: str = self._inference(prompt)
        logging.debug(f"Agent response: {response}")


        self._append_to_memory(prompt, role="user")
        if self.instructions.read_and_like_confirmation.lower() in response.lower():
            self.memory.append(Message(role="assistant", content=self.instructions.read_and_like_confirmation))
            return True
        else:
            self.memory.append(Message(role="assistant", content=self.instructions.read_confirmation))
            return False

        
    def post(self) -> str:     
        prompt = self.instructions.post_prompt
        response: str = self._inference(prompt)
        self._append_to_memory(prompt, role="user")
        self._append_to_memory(response)
        logging.debug(f"Agent response: {response}")

        return response
