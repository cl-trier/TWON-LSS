import datetime
import math
import typing

import pydantic

if typing.TYPE_CHECKING:
    from twon_lss.utility import Decay


class Engagement(pydantic.BaseModel):
    log_normalize: bool = False

    def __call__(self, items: typing.List[datetime.datetime], **kwargs) -> float:
        score: float = Engagement.get_decayed_score(items, **kwargs)
        return math.log(score) if self.log_normalize else score

    @staticmethod
    def get_decayed_score(
        items: typing.List[datetime.datetime],
        reference_datetime: datetime.datetime,
        decay: "Decay",
    ) -> float:
        return sum([decay(item, reference_datetime) for item in items])
