import typing

import pydantic

from twon_lss.schemas.user import User
from twon_lss.schemas.post import Post


class Feed(pydantic.RootModel):
    """
    Represents a collection of posts that can be displayed to users.

    The Feed class manages collections of posts and provides methods to filter
    and access posts based on various criteria. It supports iteration and
    length operations for easy manipulation.

    The class supports iteration and length operations:
        - Iterate through posts: `for post in feed:`
        - Get feed length: `len(feed)`

    Attributes:
        items (List[Post]): A list of Post objects contained in the feed. (default: []).

    Example:
        >>> from src.twon_lss.schemas import Feed
        ... feed = Feed(
        ...     items=[post1, post2, post3]  # list of Post objects
        ... )
        ... user_feed = feed.get_items_by_user(user)
        ... for post in feed:
        ...     print(post)
    """

    root: typing.List[Post] = pydantic.Field(default_factory=list)

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, index):
        return self.root[index]

    def append(self, post: Post) -> None:
        self.root.append(post)

    def extend(self, posts: typing.List[Post]) -> None:
        self.root.extend(posts)

    def get_items_by_user(self, user: User) -> "Feed":
        return Feed(list(filter(lambda post: post.user == user, self.root)))

    def get_unread_items_by_user(self, user: User) -> "Feed":
        return Feed(
            list(
                filter(
                    lambda post: user
                    not in map(
                        lambda interaction: interaction.user,
                        post.get_interactions()["read"],
                    ),
                    self.root,
                )
            )
        )
