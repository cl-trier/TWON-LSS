import typing
import datetime

import pydantic

from twon_lss.schemas import Post
from twon_lss.utility import Noise

from twon_lss.ranking._interface import RankingInterface, RankingArgsInterface

from .decay import Decay
from .engagement import Engagement


__all__ = ["Ranker", "RankerArgs", "Decay", "Engagement"]


class RankerArgs(RankingArgsInterface):
    class Weights(pydantic.BaseModel):
        likes: float = 1.0
        shares: float = 1.0
        comments: float = 1.0

    weights: Weights = Weights()

    decay: Decay = Decay(minimum=0.2, reference_timedelta=datetime.timedelta(days=3))
    noise: Noise = Noise(low=0.6, high=1.4)
    engagement: Engagement = Engagement(func="count_based", log_normalize=False)

    reference_datetime: datetime.datetime = datetime.datetime.now()


class Ranker(RankingInterface):
    args: RankerArgs = RankerArgs()

    def _compute_post_score(self, post: "Post") -> float:
        observations: typing.List[float] = [
            weight
            * self.args.engagement(
                items=items,
                reference_datetime=self.args.reference_datetime,
                decay=self.args.decay,
            )
            for weight, items in [
                (self.args.weights.likes, post.likes),
                (self.args.weights.shares, post.shares),
                (self.args.weights.comments, post.comments),
            ]
        ]

        if self.args.engagement.func == "count_based":
            return (
                self.args.noise()
                * self.args.decay(post.timestamp, self.args.reference_datetime)
                * sum(observations)
            )

        else:
            return self.args.noise() * sum(observations)
