import datetime
import math
import typing

import pydantic

from .decay import Decay


class Engagement(pydantic.BaseModel):
    func: typing.Literal["count_based", "decay_based"]
    log_normalize: bool

    def __call__(self, items: typing.List[datetime.datetime], **kwargs) -> float:
        score: float = (
            len(items)
            if self.func == "count_based"
            else Engagement.get_decayed_score(items, **kwargs)
        )

        return math.log(score) if self.log_normalize else score

    @staticmethod
    def get_decayed_score(
        items: typing.List[datetime.datetime],
        reference_datetime: datetime.datetime,
        decay: Decay,
    ) -> float:
        return sum([decay(item, reference_datetime) for item in items])
