import abc
import typing

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
        self, users: typing.List[User], feed: Feed, network: Network
    ) -> typing.Dict[typing.Tuple[User, Post], float]:
        # retrieve global score for each post
        global_scores: typing.Dict[str, float] = {
            post.id: self.get_network_score(post) for post in feed
        }

        # retrieve indivual score for visible (if is neighbor) post for each user
        return {
            (user, post): (
                self.args.noise()
                * (self.get_invidual_score(user, post) + global_scores.get(post.id))
            )
            for user in users
            for post in self.get_individual_posts(user, feed, network)
        }

    def get_individual_posts(self, user: User, feed: Feed, network: Network):
        return [
            post
            for neighbor in network.get_neighbors(user)
            for post in feed.get_unread_items_by_user(user).get_items_by_user(neighbor)
        ]

    def get_network_score(self, post: Post) -> float:
        return self.args.weights.network * self._compute_network(post)

    def get_invidual_score(self, user: User, post: Post) -> float:
        return self.args.weights.indivdual * self._compute_invidual(user, post)

    @abc.abstractmethod
    def _compute_network(self, post: Post) -> float:
        pass

    @abc.abstractmethod
    def _compute_invidual(self, user: User, post: Post) -> float:
        pass
