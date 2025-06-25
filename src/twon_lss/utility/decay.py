import datetime

import pydantic


class Decay(pydantic.BaseModel):
    minimum: float = 0.2
    timedelta: datetime.timedelta = datetime.timedelta(days=3)

    def __call__(
        self,
        observation: datetime.datetime,
        reference: datetime.datetime,
    ) -> float:
        decay: float = 1.0 - (
            (reference - observation).total_seconds()
            / self.timedelta.total_seconds()
        )

        return max([decay, self.minimum])
