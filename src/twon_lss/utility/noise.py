import random
import typing

import pydantic


class Noise(pydantic.BaseModel):
    low: float = 0.8
    high: float = 1.2

    def __call__(self) -> float:
        return random.uniform(self.low, self.high)

    def draw_samples(self, n: int) -> typing.List[float]:
        return [self() for _ in range(n)]
