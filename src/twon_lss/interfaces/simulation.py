import abc
import typing

import pydantic

from rich.progress import track

from twon_lss.interfaces import AgentInterface, RankerInterface
from twon_lss.schemas import User, Network, Feed


class SimulationInterfaceArgs(pydantic.BaseModel):
    """
    TODO
    """

    num_steps: int = 100
    num_posts_to_interact_with: int = 5


class SimulationInterface(abc.ABC, pydantic.BaseModel):
    """
    TODO
    """

    args: SimulationInterfaceArgs = pydantic.Field(
        default_factory=SimulationInterfaceArgs
    )

    ranker: RankerInterface
    individuals: typing.Dict[User, AgentInterface]

    network: Network
    feed: Feed

    def __call__(self) -> None:
        """
        TODO
        """
        for _ in track(range(self.args.num_steps)):
            self._step()

    @abc.abstractmethod
    def _step(self) -> None:
        """
        TODO
        """
        pass

    @abc.abstractmethod
    def _step_agent(self, user: User, agent: AgentInterface, feed: Feed):
        """
        TODO
        """
        pass
