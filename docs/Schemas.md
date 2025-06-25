# Schemas

## User
The `User` class represents a user in the simulation with the following attributes:
- **id:** A unique identifier (ID) of the user as either a string or integer.
- **agent:** An `AgentInterface` object that controls the user's behavior in the simulation.

```python
from src.twon_lss.schemas import User

user = User(
    id="user123",
    agent=None
)
```

## Post
The `Post` class models a social media post/comment for the simulation with the following attributes:
- **id:** A unique identifier (ID) of the post as either a string or integer.
- **user:** A `User` object representing the author of the post.
- **content:** The text content of the post as a string.
- **interactions:** A list of `Interaction` objects representing user interactions (likes, shares, reads).
- **comments:** A list of `Post` objects representing comments, allowing for nested comment structures.
- **timestamp:** The timestamp of post creation, automatically set to current time if not provided.

The class also provides a computed property `interactions_grouped` that groups interactions by type.

```python
from src.twon_lss.schemas import Post

post = Post(
    id="post456",
    user=user,
    content="This is a sample post content",
    interactions=[],  # list of Interaction objects
    comments=[],      # list of Post objects
)
```

## Interaction
The `Interaction` class represents user interactions with posts, supporting the following interaction types:
- **read:** User has read the post
- **like:** User has liked the post  
- **share:** User has shared the post

Attributes:
- **user:** A `User` object representing who performed the interaction.
- **type:** An `InteractionTypes` enum value specifying the interaction type.
- **timestamp:** The timestamp when the interaction occurred, automatically set if not provided.

```python
from src.twon_lss.schemas import Interaction, InteractionTypes

interaction = Interaction(
    user=user,
    type=InteractionTypes.like
)
```

## Feed
The `Feed` class represents a collection of posts that can be displayed to users:
- **items:** A list of `Post` objects contained in the feed.

The class provides methods to filter posts by user and supports iteration and length operations.

```python
from src.twon_lss.schemas import Feed

feed = Feed(
    items=[post1, post2, post3]  # list of Post objects
)

# Filter posts by a specific user
user_feed = feed.get_items_by_user(user)

# Iterate through posts
for post in feed:
    print(post)
```

## Network
The `Network` class represents the social network structure using NetworkX:
- **graph:** A `networkx.Graph` object representing the network connections between users.

The class provides methods to get neighbors of a user and supports iteration over the network.

```python
from src.twon_lss.schemas import Network
import networkx as nx

# Create a network from an existing NetworkX graph
graph = nx.Graph()
network = Network.from_graph(graph)

# Get neighbors of a user
neighbors = network.get_neighbors(user)

# Iterate through users
for user in network:
    print(user)
```
