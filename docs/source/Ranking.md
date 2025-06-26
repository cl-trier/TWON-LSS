# Ranking Algorithm

## Interface


## TWON-Ranker

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
