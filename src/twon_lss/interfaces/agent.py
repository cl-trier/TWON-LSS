import typing
import abc
import enum

import pydantic

from twon_lss.schemas import Post


class AgentActions(enum.Enum):
    """
    TODO
    """

    read = "read"
    like = "like"
    post = "post"


class AgentInterface(abc.ABC, pydantic.BaseModel):
    """
    Abstract base class for user behavior agents in the social media simulation.

    The AgentInterface class defines the core framework for implementing
    user behavior agents that control how users interact within the social
    media simulation. Agents determine user actions such as posting content,
    engaging with posts, sharing information, and responding to other users.

    This interface supports different agent types including influencers,
    bystanders, and other behavioral archetypes by providing a consistent
    framework for defining action probabilities and decision-making logic.
    """

    pass

    @abc.abstractmethod
    def select_actions(self, post: Post) -> typing.Set[AgentActions]:
        """
        TODO
        """
        pass

    @abc.abstractmethod
    def post(self, post: Post) -> str:
        """
        TODO
        """
        pass
