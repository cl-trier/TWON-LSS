import typing
import datetime

import pydantic

from twon_lss.schemas import User
from twon_lss.schemas import Post

from twon_lss.ranking._interface import RankingInterface, RankingArgsInterface

from twon_lss.utility import Decay

from .engagement import Engagement


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

    def _compute_invidual(self, user: "User", post: "Post") -> float:
        return 1.0
