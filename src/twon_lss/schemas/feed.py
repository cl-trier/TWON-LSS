import typing

import pydantic

from .post import Post
from .user import User


class Feed(pydantic.BaseModel):
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
