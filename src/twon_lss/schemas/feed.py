from twon_lss.schemas.user import User
from twon_lss.schemas.post import Post
import json

from pydantic import model_validator, PrivateAttr, Field, RootModel
from typing import List, Dict
from bisect import bisect_right
import typing

class Feed(RootModel):
    root: typing.List[Post] = Field(default_factory=list)
    _user_index: Dict[User, List[Post]] = PrivateAttr(default_factory=dict)
    
    @model_validator(mode='after')
    def _build_indexes(self):
        self.root = sorted(self.root, key=lambda p: p.timestamp)
        self._user_index = {}
        for post in self.root:
            self._user_index.setdefault(post.user, []).append(post)
        return self

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, index):
        return self.root[index]

    def append(self, post: Post) -> None:
        self.root.append(post)
        self._user_index.setdefault(post.user, []).append(post)

    def extend(self, posts: typing.List[Post]) -> None:
        for post in posts:
            self.append(post)

    def get_items_by_user(self, user: User) -> "Feed":
        return Feed(root=self._user_index.get(user, []))
    
    def get_unread_items_by_user(self, user: User) -> "Feed":
        return Feed(root=[p for p in self.root if user not in p.reads])
    
    def filter_by_timestamp(self, timestamp: int, persistence: int) -> "Feed":
        cutoff = timestamp - persistence
        idx = bisect_right([p.timestamp for p in self.root], cutoff)
        return Feed(root=self.root[idx:])
    
    def to_json(self, path: str) -> None:
        """Save the Feed to a JSON file without the private attributes."""
        with open(path, "w") as f:
            json.dump([post.model_dump() for post in self.root], f, indent=4)

    class Config:
        arbitrary_types_allowed = True