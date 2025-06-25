import typing

import pydantic

from .post import Post
from .user import User


class Feed(pydantic.BaseModel):
    """
    Represents a collection of posts that can be displayed to users.
    
    The Feed class manages collections of posts and provides methods to filter
    and access posts based on various criteria. It supports iteration and 
    length operations for easy manipulation.
    
    Attributes:
        items (List[Post]): A list of Post objects contained in the feed.
            Defaults to empty list.
    
    Methods:
        get_items_by_user(user): Filter posts by a specific user.
        get_unread_items_by_user(user): Filter unread posts by a specific user.
    
    The class supports iteration and length operations:
        - Iterate through posts: `for post in feed:`
        - Get feed length: `len(feed)`
    
    Example:
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
    """
    # TODO handled displaying of shared posts
    items: typing.List[Post] = pydantic.Field(default_factory=list)

    def get_items_by_user(self, user: User) -> "Feed":
        return Feed(items=list(filter(lambda post: post.user == user, self.items)))

    def get_unread_items_by_user(self, user: User) -> "Feed":
        return Feed(
            items=list(
                filter(
                    lambda post: user
                    not in map(
                        lambda interaction: interaction.user,
                        post.get_interactions()["read"],
                    ),
                    self.items,
                )
            )
        )

    def __iter__(self):
        return iter(self.items)

    def __next__(self):
        return next(self.items)

    def __len__(self) -> int:
        return len(self.items)
