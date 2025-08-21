import typing

import pydantic

from twon_lss.interfaces import AgentInterface, AgentActions

from twon_lss.schemas import Post

__all__ = ["Agent", "AgentActions", "AgentInstructions"]



class Agent(AgentInterface):
    eps: float = 0.2
    delta: float = 0.05

    memory: typing.List[float] = pydantic.Field(default_factory=list)
    memory_length: int = pydantic.Field(default=4, ge=0, le=20)

    def select_actions(self, post: Post) -> typing.Set[AgentActions]:
        self.memory.append(self._bcm(self.memory[-1], float(post.content)))
        return {AgentActions.post}

    def post(self, _: Post) -> str:
        return str(self.memory[-1])

    def _bcm(self, xi: float, xj: float) -> float:
        if abs(xi - xj) < self.eps:
            return xi + self.delta * (xj - xi)
        else:
            return xi