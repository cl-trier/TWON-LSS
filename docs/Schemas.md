# Schemas

## Post
We model a social media post for the TWON simulation with the following class. The object contains the following attributes:
- **id:** A unique identifier (ID) of the post as a string.
- **timestamp:** The timestamp containing the post creation date and time. The class expect a string formatted defined by ISO 8601.
- **likes/dislikes:** A list of observations denoted as timestamps (see above).
- **comments:** A list of `Post` objects representing comments. This approach allows arbitrary nest posts into complex tree structures for future TWON modifications. The current implementation ignores those sublevel structures and only counts direct comments of the main posts into the observations.


```python
from src.post import Post

ID: str
TIMESTAMP: datetime
OBERSERVATIONS: List[datetime]
COMMENTS: List[Post] # post objects w/o comments

post = Post(
    id=ID,
    timestamp=TIMESTAMP,
    likes=OBERSERVATIONS,
    dislikes=OBERSERVATIONS,
    comments=COMMENTS,
)
```