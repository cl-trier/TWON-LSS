import typing
import math
import datetime
import statistics

import pydantic

from twon_lss.interfaces import RankerInterface, RankerArgsInterface

from twon_lss.schemas import User, Post, Feed, InteractionTypes
from twon_lss.utility import Decay, LLM


__all__ = ["Ranker", "RankerArgs", "Engagement"]


class Engagement(pydantic.BaseModel):
    """
    TODO
    """

    log_normalize: bool = False

    def __call__(self, items: typing.List[datetime.datetime], **kwargs) -> float:
        """
        TODO
        """
        score: float = Engagement.get_decayed_score(items, **kwargs)
        return math.log(score) if self.log_normalize else score

    @staticmethod
    def get_decayed_score(
        items: typing.List[datetime.datetime],
        reference_datetime: datetime.datetime,
        decay: Decay,
    ) -> float:
        """
        TODO
        """
        return sum([decay(item, reference_datetime) for item in items])


class RankerArgs(RankerArgsInterface):
    """
    TODO
    """

    class EngagementWeights(pydantic.BaseModel):
        """
        TODO
        """

        likes: float = 1.0
        comments: float = 1.0

    engagement: Engagement = Engagement()
    engagementWeights: EngagementWeights = EngagementWeights()


class Ranker(RankerInterface):
    """
    TODO
    """

    decay: Decay
    llm: LLM

    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: Post) -> float:
        """
        TODO
        """
        reference_datetime: datetime.datetime = datetime.datetime.now()

        observations: typing.List[float] = [
            weight
            * self.args.engagement(
                items=items,
                reference_datetime=reference_datetime,
                decay=self.decay,
            )
            for weight, items in [
                (
                    self.args.engagementWeights.likes,
                    [
                        interaction.timestamp
                        for interaction in post.get_interactions()[
                            InteractionTypes.like
                        ]
                    ],
                ),
                (
                    self.args.engagementWeights.comments,
                    [comment.timestamp for comment in post.comments],
                ),
            ]
        ]

        return sum(observations)

    def _compute_individual(self, user: User, post: Post, feed: Feed) -> float:
        """
        TODO
        """
        return 1.0
        # FIXME authorization error on huggingface similarity endpoint
        return statistics.mean(
            self.llm.similarity(
                post.content, [item.content for item in feed.get_items_by_user(user)]
            )
        )
