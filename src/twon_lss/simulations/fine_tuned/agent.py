import typing
import re
import enum

import pydantic

from twon_lss.interfaces import AgentInterface

from twon_lss.schemas import Post
from twon_lss.utility import LLM, Chat, Message


__all__ = ["Agent", "AgentActions", "AgentInstructions"]


class AgentActions(enum.Enum):
    """
    TODO
    """

    like = "like"
    comment = "comment"


class AgentInstructions(pydantic.BaseModel):
    """
    TODO
    """

    persona: str
    select_actions: str
    comment: str
    post: str


class Agent(AgentInterface):
    """
    TODO
    """

    llm: LLM
    instructions: AgentInstructions

    memory: typing.List[Message] = pydantic.Field(default_factory=list)
    memory_length: int = pydantic.Field(default=4, ge=0, le=20)

    def _append_to_memory(self, content: str, role="assistant") -> None:
        self.memory.append(Message(role=role, content=content))

    def _inference(self, prompt: str) -> Chat:
        """
        TODO
        """
        return self.llm.generate(
            Chat(
                [
                    Message(role="system", content=self.instructions.persona),
                    *self.memory[-self.memory_length * 2 :],
                    Message(role="user", content=prompt),
                ]
            )
        )

    def select_actions(self, post: Post) -> typing.Set[AgentActions]:
        """
        TODO
        """
        instruction: str = self.instructions.select_actions + str(
            list(AgentActions._member_names_)
        )
        prompt = instruction + post.model_dump()["content"]
        response: str = self._inference(prompt)
        matches: typing.List[str] = re.findall(
            "|".join(list(AgentActions._member_names_)), response
        )

        return {AgentActions(item) for item in matches}

    def comment(self, post: Post) -> str:
        """
        TODO NILS:
            - Change so post includes it's replies...
        """
        prompt = self.instructions.comment + post.model_dump()["content"]
        response: str = self._inference(prompt)
        self._append_to_memory(prompt, role="user")
        self._append_to_memory(response)

        return response

    def post(self) -> str:
        """
        TODO
        """
        prompt = self.instructions.post
        response: str = self._inference(prompt)
        self._append_to_memory(prompt, role="user")
        self._append_to_memory(response)

        return response
