import typing
import abc
import enum

import pydantic

from twon_lss.schemas import Post


class AgentActions(enum.Enum):
    read = "read"
    like = "like"
    post = "post"


class AgentInterface(abc.ABC, pydantic.BaseModel):
    @abc.abstractmethod
    def select_actions(self, post: Post) -> typing.Set[AgentActions]:
        pass

    @abc.abstractmethod
    def post(self, post: Post) -> str:
        pass
