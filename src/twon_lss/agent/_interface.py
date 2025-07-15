import abc
import typing
import enum

import pydantic


class AgentArgsInterface(abc.ABC, pydantic.BaseModel):
    """
    Abstract base class for agent configuration parameters.

    The AgentArgsInterface class provides a standardized configuration
    interface for agent implementations, ensuring consistent parameter
    handling across different agent types. This base class can be extended
    to include specific configuration options for different agent behaviors.

    This interface serves as a foundation for configuring agent behavior
    parameters such as action probabilities, response patterns, engagement
    thresholds, and other behavioral characteristics that define how agents
    interact within the social media simulation.
    """

    initial_action_likelihoods: typing.Dict[
        typing.Union[enum.Enum, typing.Literal["post", "reply"]], float
    ] = pydantic.Field(default_factory=dict)


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

    Attributes:
        args (AgentArgsInterface): Configuration object containing agent-specific parameters (default: AgentArgsInterface()).
    """

    args: AgentArgsInterface = AgentArgsInterface()


# NOTE attribute initial_action_likelihoods to map influencer and bystander agents
