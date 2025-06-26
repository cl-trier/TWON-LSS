import datetime

import pydantic


class Decay(pydantic.BaseModel):
    """
    The `Decay` class computes a decay factor based on the time elapsed between two timestamps, decreasing the relevance of observations over time.
    When called, the decay object calculates the time difference between the reference timestamp and the observed timestamp. The maximum computed value is 1.0, achieved when `observation == reference`.

    Attributes:
        low (minimum): Lower boundary for the decay factor (default: 0.2).
        timedelta(timedelta): Reference time interval for decay calculation (default: 3 days).

    """

    minimum: float = 0.2
    timedelta: datetime.timedelta = datetime.timedelta(days=3)

    def __call__(
        self,
        observation: datetime.datetime,
        reference: datetime.datetime,
    ) -> float:
        decay: float = 1.0 - (
            (reference - observation).total_seconds() / self.timedelta.total_seconds()
        )

        return max([decay, self.minimum])
