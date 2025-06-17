import datetime

import pydantic


class Decay(pydantic.BaseModel):
    minimum: float
    reference_timedelta: datetime.timedelta

    def __call__(
        self,
        observation_datetime: datetime.datetime,
        reference_datetime: datetime.datetime,
    ) -> float:
        decay: float = 1.0 - (
            (reference_datetime - observation_datetime).total_seconds()
            / self.reference_timedelta.total_seconds()
        )

        return max([decay, self.minimum])
