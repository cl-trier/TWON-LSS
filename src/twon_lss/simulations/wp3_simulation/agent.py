import typing
import re
import enum
import logging

import pydantic

from twon_lss.interfaces import AgentInterface

from twon_lss.schemas import Post
from twon_lss.utility import LLM, Chat, Message
from twon_lss.schemas import Feed, User, Post

import numpy as np


__all__ = ["Agent", "AgentInstructions"]


class AgentInstructions(pydantic.BaseModel):
    read_prompt: str
    post_prompt: str
    feed_placeholder: str
    cognition_update: str
    profile_format: str


class WP3Agent(AgentInterface):
    
    llm: LLM
    instructions: AgentInstructions

    memory: typing.List[Message] = pydantic.Field(default_factory=list)
    memory_length: int = pydantic.Field(default=4, ge=0, le=50)

    theta: float = pydantic.Field(default=0.5, ge=0.0, le=1.0)
    activations: int = 0

    bio: str = pydantic.Field(default="")
    cognition: str = pydantic.Field(default="")

    posts: typing.List[Post] = pydantic.Field(default_factory=list)
    
    
    def select_actions(self, post: Post):
        pass

    def _append_to_memory(self, content: str, role="assistant") -> None:
        self.memory.append(Message(role=role, content=content))

    def _inference(self, prompt: str) -> Chat:
        return self.llm.generate(
            Chat(
                [
                    Message(role="system", content=self._profile()),
                    *self.memory[-self.memory_length * 2:],
                    Message(role="user", content=prompt),
                ]
            )
        )
    
    
    # Actions
    def _profile(self) -> str:
        return self.instructions.profile_format.format(bio=self.bio, cognition=self.cognition)
    
    def cognition_update(self) -> None:
        response: str = self._inference(self.instructions.cognition_update)
        logging.debug(f"Agent response: {response}")
        self.cognition = response

    def _like(self, post: Post, user: User) -> None:
        if np.random.rand() < 0.75:
            post.likes.append(user)
            return True
        return False
    
    def _read(self, feed_str) -> str:
        response: str = self._inference(self.instructions.read_prompt.format(feed=feed_str))
        logging.debug(f"Agent response: {response}")

        self._append_to_memory(self.instructions.feed_placeholder, role="user")
        self._append_to_memory(response)

    
    def consume_feed(self, posts: list[Post], user:User) -> str:
        feed_str = ""
        for post in posts:
            post.reads.append(user)
            if self._like(post, user):
                feed_str += f">{post.user.id}: {post.model_dump()['content']} (You like this post)\n"    
            else:
                feed_str += f">{post.user.id}: {post.model_dump()['content']}\n"
        self._read(feed_str)
        
    def post(self) -> str:     
        prompt = self.instructions.post_prompt
        response: str = self._inference(prompt)
        self._append_to_memory(prompt, role="user")
        self._append_to_memory(response)
        logging.debug(f"Agent response: {response}")

        return response
