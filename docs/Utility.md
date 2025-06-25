# Utility

## Noise
The `Noise` class generates random floating point numbers from a uniform distribution for multiplicative noise with the following attributes:
- **low:** Lower boundary for the random number generation (default: 0.8).
- **high:** Upper boundary for the random number generation (default: 1.2).

The neutral value (no noise) is achieved when `low = high = 1.0`. The class provides methods to generate single random numbers or multiple samples.

```python
from twon_lss.utility import Noise

noise = Noise(
    low=0.8,
    high=1.2
)

# Generate a single random number
rnd_number: float = noise()

# Generate multiple samples
n_samples: int = 10
rnd_samples: list[float] = noise.draw_samples(n_samples)
```

## Decay
The `Decay` class computes a decay factor based on the time elapsed between two timestamps, decreasing the relevance of observations over time with the following attributes:
- **minimum:** Lower boundary for the decay factor (default: 0.2).
- **timedelta:** Reference time interval for decay calculation (default: 3 days).

When called, the decay object calculates the time difference between the reference timestamp and the observed timestamp. The maximum computed value is 1.0, achieved when `observation == reference`.

```python
from twon_lss.utility import Decay
import datetime

decay = Decay(
    minimum=0.2,
    timedelta=datetime.timedelta(days=3)
)

# Calculate decay factor
observation: datetime.datetime = datetime.datetime.now()
reference: datetime.datetime = datetime.datetime.now() + datetime.timedelta(hours=1)

decay_factor: float = decay(observation, reference)
```