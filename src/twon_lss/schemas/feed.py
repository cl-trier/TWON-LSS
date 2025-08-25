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
        """
        Get count of likes that user received on their posts
        """
        posts = self.get_items_by_user(user)
        return sum(len(post.likes) for post in posts)

    def get_likes_given_to_user(self, source_user: User, target_user: User) -> int:
        """
        Get count of likes that source_user gave to target_user's posts
        """
        target_posts = self.get_items_by_user(target_user)
        return sum(1 for post in target_posts if source_user in post.likes)

    def to_json(self, path: str) -> None:
        json.dump(self.model_dump(mode="json"), open(path, "w"), indent=4)
