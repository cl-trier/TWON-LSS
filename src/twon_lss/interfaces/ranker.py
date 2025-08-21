import abc
import typing
import logging
import json

import pydantic

from twon_lss.utility import Noise
from twon_lss.schemas import User, Post, Feed, Network, UserID, PostID


class RankerScores(pydantic.RootModel):
    root: typing.Dict[typing.Tuple[UserID, PostID], float] = pydantic.Field(default_factory=dict)

    def to_json(self, path: str):
        json.dump(
            [
                {"user": user, "post": post, "score": score}
                for (user, post), score in self.root.items()
            ],
            open(path, "w"),
            indent=4,
        )

    def filter_by_user(self, user: User) -> typing.List[typing.Tuple[PostID, float]]:
        return [
            (post_id, post_score)
            for (user_id, post_id), post_score in self.root.items()
            if user.id == user_id
        ]


class RankerInterfaceWeights(pydantic.BaseModel):
    network: float = 1.0
    individual: float = 1.0


class RankerArgsInterface(abc.ABC, pydantic.BaseModel):
    weights: RankerInterfaceWeights = pydantic.Field(
        default_factory=RankerInterfaceWeights
    )
    noise: Noise = pydantic.Field(default_factory=Noise)


class RankerInterface(abc.ABC, pydantic.BaseModel):
    args: RankerArgsInterface = pydantic.Field(default_factory=RankerArgsInterface)

    def __call__(
        self, users: typing.List[User], feed: Feed, network: Network
    ) -> RankerScores:
        # retrieve global score for each post
        # TODO parallelize on post level
        global_scores: typing.Dict[PostID, float] = {}
        for post in feed:
            global_scores[post.id] = self._compute_network(post)

        # retrieve indivual score for visible (if is neighbor) post for each user
        # TODO parallelize on user level
        final_scores: RankerScores = RankerScores()

        for user in users:
            logging.debug(user)
            for post in self.get_individual_posts(user, feed, network):
                individual_score = self._compute_individual(user, post, feed)

                combined_score = (
                    self.args.weights.individual * individual_score
                    + self.args.weights.network * global_scores[post.id]
                )

                final_scores.root[(user.id, post.id)] = self.args.noise() * combined_score

        return final_scores

    def get_individual_posts(self, user: User, feed: Feed, network: Network):
        return [
            post
            for neighbor in network.neighbors[user.id]
            for post in (
                feed
                .get_unread_items_by_user(user.id)
                .get_items_by_user(neighbor)
            )
        ]

    @abc.abstractmethod
    def _compute_network(self, post: Post) -> float:
        pass

    @abc.abstractmethod
    def _compute_individual(self, user: User, post: Post) -> float:
        pass
