import random
import typing

import pydantic


class Noise(pydantic.BaseModel):
    """
    The `Noise` class generates random floating point numbers from a uniform distribution for multiplicative noise with the following attributes.

    Attributes:
        low (float): Lower boundary for the random number generation (default: 0.8).
        high (float): Upper boundary for the random number generation (default: 1.2).
    
    The neutral value (no noise) is achieved when `low = high = 1.0`. The class provides methods to generate single random numbers or multiple samples.
    """
    low: float = 0.8
    high: float = 1.2

    def __call__(self) -> float:
        return random.uniform(self.low, self.high)

    def draw_samples(self, n: int) -> typing.List[float]:
        return [self() for _ in range(n)]
