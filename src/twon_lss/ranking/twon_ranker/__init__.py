import typing
import datetime
import statistics

import pydantic

from twon_lss.schemas import User, Post, Feed
from twon_lss.utility import Decay, LLM

from twon_lss.ranking._interface import RankingInterface, RankingArgsInterface
from twon_lss.ranking.twon_ranker.engagement import Engagement


__all__ = ["Ranker", "RankerArgs", "Engagement"]


class RankerArgs(RankingArgsInterface):
    class EngagementWeights(pydantic.BaseModel):
        likes: float = 1.0
        shares: float = 1.0
        comments: float = 1.0

    decay: Decay = Decay()

    engagement: Engagement = Engagement()
    engagementWeights: EngagementWeights = EngagementWeights()


class Ranker(RankingInterface):
    llm: LLM
    args: RankerArgs = RankerArgs()

    def _compute_network(self, post: "Post") -> float:
        reference_datetime: datetime.datetime = datetime.datetime.now()

        observations: typing.List[float] = [
            weight
            * self.args.engagement(
                items=items,
                reference_datetime=reference_datetime,
                decay=self.args.decay,
            )
            for weight, items in [
                (self.args.engagementWeights.likes, post.interactions),
                (self.args.engagementWeights.shares, post.interactions),
                (self.args.engagementWeights.comments, post.interactions),
            ]
        ]

        return sum(observations)

    def _compute_invidual(self, user: User, post: Post, feed: Feed) -> float:
        return statistics.mean(
            self.llm.similarity(
                post.content, [item.content for item in feed.get_items_by_user(user)]
            )
        )
