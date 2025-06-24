import datetime

import pydantic


class Decay(pydantic.BaseModel):
    minimum: float = 0.2
    reference_timedelta: datetime.timedelta = datetime.timedelta(days=3)

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
