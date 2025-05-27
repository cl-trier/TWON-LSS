import typing
import datetime

import pydantic

from twon_lss.network.schemas import Post

from .decay import Decay
from .engagement import Engagement
from .noise import Noise


__all__ = ["Ranker", "RankerArgs", "Decay", "Engagement", "Noise"]


class RankerArgs(pydantic.BaseModel):
    class Weights(pydantic.BaseModel):
        likes: float = 1.0
        shares: float = 1.0
        comments: float = 1.0

    weights: Weights = Weights()

    decay: Decay = Decay(minimum=0.2, reference_timedelta=datetime.timedelta(days=3))
    noise: Noise = Noise(low=0.6, high=1.4)
    engagement: Engagement = Engagement(func="count_based", log_normalize=False)

    reference_datetime: datetime.datetime = datetime.datetime.now()


class Ranker(pydantic.BaseModel):
    args: RankerArgs = RankerArgs()

    def __call__(self, posts: typing.List["Post"]) -> typing.Dict[str, float]:
        return {post.id: self._compute_post_score(post) for post in posts}

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
