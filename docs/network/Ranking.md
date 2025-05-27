# Ranking Algorithm: Success-Driven
todo

## Modules
The current TWON ranking/recommendation algorithm is divided into three encapsulated modules that composed denote the ranking function. These modules provide the functionalities to measure engagement given a predefined data format, represent the course of time, and partly randomize the final ranking.

### Noise
We draw random floating point numbers from the normal distribution provided lower and upper boundaries to generate a multiplicative noise (the neutral value defined as `LOW = HIGH = 1.` will result in no noise).

```python
from src.modules import Noise

LOW: float
HIGH: float
N: int

eps = Noise(low=LOW, high=HIGH)

rnd_number: float = eps()
rnd_samples: List[float] = eps.draw_samples(N)
```

### Decay
We compute a decay factor based on the time elapsed between two references. In the context of this project, the decay factor decreases the relevance of posts over time. That results in older posts without recent interaction being less often recommended. We instantiate a decay object by defining a minimum value that serves as a lower boundary for the decay and a reference time interval. When called, the decay object calculates a time difference between the reference time interval and the observed time interval. The maximum computed value is defined as 1, for `observation == reference`.


```python
from src.modules import Decay

MINIMUM: float
REFERENCE_TIMEDELTA: timedelta

decay = Decay(minimum=MINIMUM, reference_timedelta=REFERENCE_TIMEDELTA)

decay_factor: float = decay(observation_datetime=datetime, reference_datetime=datetime) 
```

### Engagement
The engagement module computes a score based on a plain count of observations `count_based` or the sum of decayed values for the individual data points `decay_based`. For the decayed-based version, an instantiated decay module is necessary. Optionally, the output can be normalized with the natural logarithm `log_normalize`.

```python
from src.modules import Engagement

FUNC: Literal['count_based', 'decay_based']
LOG_NORMALIZE: bool

E = Engagement(func=FUNC, log_normalize=LOG_NORMALIZE)

score_count: int = E(items=List[datetime])
score_decay: float = E(items=List[datetime], reference_datetime=datetime, decay=decay)
```

## Usage
todo



### Ranker
change according to implementation

The `Ranker` object denotes the attributes needed for interaction with the ranker. It collates all modules previously defined and combines them with weights for each observation type. The object contains the following attributes:
- **items:** A list of Post objects 
- **reference_datetime:** The reference timestamp (defaults to now while receiving the request). 
- **decay:** Attributes needed to instantiate the `Decay` module 
- **noise:** Attributes needed to instantiate the `Noise` module 
- **engagement:** Attributes needed to instantiate the `Engagement` module 
- **weights:** Weights to tweak the different engagement factors (defaults `1.0` for all)

```python
from src.request import Request, Weights

MODE: Literal["ranked", "chronological", "random"] = "ranked"
ITEMS: List[Post] # see Usage:Post
REFERENCE_DATETIME: datetime
DECAY: modules.Decay  # see Modules:Decay
NOISE: modules.Noise  # see Modules:Noise
ENGAGEMENT: modules.Engagement # see Modules:Engagement

WEIGHTS: Weights(
    likes=1.
    shares=1.
    comments=1.
)

req = Request(
    items=ITEMS,
    reference_datetime=REFERENCE_DATETIME,
    decay=DECAY,
    noise=NOISE,
    engagement=ENGAGEMENT
    weights=WEIGHTS
)
```

### Ranker
todo

```python
# todo
```