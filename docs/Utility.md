# Utility

## Noise
We draw random floating point numbers from the normal distribution provided lower and upper boundaries to generate a multiplicative noise (the neutral value defined as `LOW = HIGH = 1.` will result in no noise).

```python
from twon_lss.utility import Noise

low: float
high: float
n_samples: int

eps = Noise(low=low, high=high)

rnd_number: float = eps()
rnd_samples: List[float] = eps.draw_samples(n_samples)
```

## Decay
We compute a decay factor based on the time elapsed between two references. In the context of this project, the decay factor decreases the relevance of an observation over time. We instantiate a decay object by defining a minimum value that serves as a lower boundary for the decay and a reference time interval (`timedelta`). When called, the decay object calculates a time difference between the reference time stamp and the observed time stamp. The maximum computed value is defined as 1, for `observation == reference`.

```python
from twon_lss.utility import Decay

minimum: float
timedelta: timedelta
observation: datetime
reference: datetime

decay = Decay(minimum=minimum, timedelta=timedelta)

decay_factor: float = decay(observation, reference) 
```