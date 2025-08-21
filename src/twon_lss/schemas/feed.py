import typing
import json

import pydantic

from twon_lss.schemas.post import Post
from twon_lss.schemas.mappings import UserID, PostID


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

    def get_item_by_id(self, post_id: PostID) -> Post:
        return list(filter(lambda post: post.id == post_id, self.root))[0]

    def get_items_by_user(self, user_id: UserID) -> "Feed":
        return Feed(list(filter(lambda post: post.user == user_id, self.root)))

    def get_unread_items_by_user(self, user_id: UserID) -> "Feed":
        return Feed(
            list(
                filter(lambda post: user_id not in post.reads, self.root)
            )
        )

    def to_json(self, path: str) -> None:
        json.dump(self.model_dump(mode="json"), open(path, "w"), indent=4)
