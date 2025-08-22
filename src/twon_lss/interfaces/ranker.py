import abc
import typing
import logging

import pydantic

from twon_lss.utility import Noise
from twon_lss.schemas import User, Post, Feed, Network


class RankerInterfaceWeights(pydantic.BaseModel):
    network: float = 1.0
    individual: float = 1.0


class RankerArgsInterface(abc.ABC, pydantic.BaseModel):
    weights: RankerInterfaceWeights = pydantic.Field(
        default_factory=RankerInterfaceWeights
    )
    noise: Noise = pydantic.Field(default_factory=Noise)
    persistence: int = 1


class RankerInterface(abc.ABC, pydantic.BaseModel):
    args: RankerArgsInterface = pydantic.Field(default_factory=RankerArgsInterface)

    def __call__(
        self, users: typing.List[User], feed: Feed, network: Network
    ) -> typing.Dict[typing.Tuple[User, Post], float]:
        logging.debug(f"{len(feed)=}")

        # retrieve global score for each post
        # TODO parallelize on post level
        global_scores: typing.Dict[str, float] = {}
        for post in feed:
            global_scores[post.id] = self._compute_network(post)

        # retrieve indivual score for visible (if is neighbor) post for each user
        # TODO parallelize on user level
        final_scores: typing.Dict[typing.Tuple[User, Post], float] = {}
        for user in users:
            for post in self.get_individual_posts(user, feed, network):
                individual_score = self._compute_individual(user, post, feed)
                global_score = global_scores[post.id]

                combined_score = (
                    self.args.weights.individual * individual_score
                    + self.args.weights.network * global_score
                )

                final_scores[(user, post)] = self.args.noise() * combined_score

        return final_scores

    def get_individual_posts(self, user: User, feed: Feed, network: Network):

        latest_timestamp = max(post.timestamp for post in feed.get_items_by_user(user))

        return [
            post
            for neighbor in network.get_neighbors(user)
            for post in feed.get_unread_items_by_user(user).get_items_by_user(neighbor).filter_by_timestamp(latest_timestamp, self.args.persistence)
        ]

    @abc.abstractmethod
    def _compute_network(self, post: Post) -> float:
        pass

    @abc.abstractmethod
    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:
        pass
