import typing
import re

import pydantic

from twon_lss.agent._interface import AgentInterface, AgentActions

from twon_lss.schemas import Post
from twon_lss.utility import LLM, Chat, Message


__all__ = ["Agent", "AgentActions", "AgentInstructions"]


class AgentInstructions(pydantic.BaseModel):
    persona: str
    select_actions: str
    comment: str
    post: str


class Agent(AgentInterface):
    llm: LLM
    instructions: AgentInstructions

    action_likelihoods: typing.Dict[AgentActions, float] = {
        item: 1.0 for item in AgentActions
    }

    memory: typing.List[Message] = pydantic.Field(default_factory=list)
    memory_length: int = pydantic.Field(default=4, ge=0, le=20)

    def _append_to_memory(self, content: str) -> None:
        self.memory.append(Message(role="system", content=content))

    def _inference(self, instruction: str, post: "Post") -> "Chat":
        return self.llm.generate(
            Chat(
                [
                    Message(role="system", content=self.instructions.persona),
                    *self.memory[-self.memory_length :],
                    Message(role="user", content=instruction),
                    Message(
                        role="user",
                        content=post.model_dump_json(
                            exclude=["id", "user", "timestamp", "interactions"]
                        ),
                    ),
                ]
            )
        )

    def select_actions(self, post: Post) -> typing.Set[AgentActions]:
        instruction: str = self.instructions.select_actions + str(
            list(AgentActions._member_names_)
        )
        response: str = self._inference(instruction, post)
        matches: typing.List[str] = re.findall(
            "|".join(list(AgentActions._member_names_)), response
        )

        return {AgentActions(item) for item in matches}

    def comment(self, post: Post) -> str:
        response: str = self._inference(self.instructions.comment, post)
        self._append_to_memory(response)

        return response

    def post(self, post: Post) -> str:
        response: str = self._inference(self.instructions.post, post)
        self._append_to_memory(response)

        return response
