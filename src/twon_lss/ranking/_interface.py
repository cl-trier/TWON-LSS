import abc
import typing
import itertools

import pydantic

from twon_lss.utility import Noise
from twon_lss.schemas import User, Post, Feed, Network


class RankingInterfaceWeights(pydantic.BaseModel):
    network: float = 1.0
    indivdual: float = 1.0


class RankingArgsInterface(abc.ABC, pydantic.BaseModel):
    weights: RankingInterfaceWeights = RankingInterfaceWeights()
    noise: Noise = Noise()
    module_args: typing.List[object] = []


class RankingInterface(abc.ABC, pydantic.BaseModel):
    args: RankingArgsInterface = RankingArgsInterface()

    def __call__(
        self, users: typing.List["User"], feed: Feed, network: Network
    ) -> typing.Dict[typing.Tuple["User", "Post"], float]:
        # retrieve global score for each post
        global_scores: typing.Dict[str, float] = {
            post.id: self._network_score(post) for post in feed
        }

        # retrieve indivual score for visible (if is neighbor) post for each user
        return {
            (user, post): (
                self.args.noise()
                * (self._invidual_score(user, post) + global_scores.get(post.id))
            )
            for post in self._individual_posts(users, feed, network)
            for user in users
        }

    def _individual_posts(
        self, users: typing.List["User"], feed: Feed, network: Network
    ):
        # TODO remove post a user has already seen
        return list(
            itertools.chain(
                *[
                    feed.get_items_by_user(neighbor)
                    for neighbor in [network.get_neighbors(user) for user in users]
                ]
            )
        )

    def _network_score(self, post: "Post") -> float:
        return self.args.weights.network * self._compute_network(post)

    def _invidual_score(self, user: "User", post: "Post") -> float:
        return self.args.weights.indivdual * self._compute_invidual(user, post)

    @abc.abstractmethod
    def _compute_network(self, post: "Post") -> float:
        pass

    @abc.abstractmethod
    def _compute_invidual(self, user: "User", post: "Post") -> float:
        pass
