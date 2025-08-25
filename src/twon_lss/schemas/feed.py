import typing
import json

import pydantic

from twon_lss.schemas.user import User
from twon_lss.schemas.post import Post


class Feed(pydantic.RootModel):
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
        return Feed(list(filter(lambda post: user not in post.reads, self.root)))
    
    def filter_by_timestamp(self, timestamp:int, persistence: int) -> "Feed":
        return Feed(list(filter(lambda post: post.timestamp > (timestamp - persistence), self.root)))
    
    def get_like_count_by_user(self, user: User) -> int:
        posts = self.get_items_by_user(user)
        return sum(len(post.likes) for post in posts)

    def to_json(self, path: str) -> None:
        json.dump(self.model_dump(mode="json"), open(path, "w"), indent=4)
