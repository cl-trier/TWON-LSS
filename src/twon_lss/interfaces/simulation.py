import abc
import typing
import logging

import pydantic

from rich.progress import track

from twon_lss.interfaces import AgentInterface, RankerInterface
from twon_lss.schemas import User, Network, Feed, Post


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

    def _step(self) -> None:
        """
        TODO
        """
        post_scores: typing.Dict[(User, Post), float] = self.ranker(
            users=self.individuals.keys(), feed=self.feed, network=self.network
        )
        logging.debug(f">o global post scores | {post_scores}")

        for i_user, i_agent in self.individuals.items():
            # get user's post scores, sort by score, limit to top N
            user_feed: typing.List[(Post, float)] = [
                (post, score)
                for (user, post), score in post_scores.items()
                if user == i_user
            ]
            user_feed.sort(key=lambda x: x[1], reverse=True)
            user_feed_top = user_feed[: self.args.num_posts_to_interact_with]

            self._step_agent(i_user, i_agent, Feed([post for post, _ in user_feed_top]))

    @abc.abstractmethod
    def _step_agent(self, user: User, agent: AgentInterface, feed: Feed):
        """
        TODO
        """
        pass
