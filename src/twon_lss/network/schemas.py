import datetime
import typing

import pydantic


class User(pydantic.BaseModel):
    id: str
    connections: typing.List["User"] = []

    def __hash__(self):
        return hash(self.id)


class Interaction(pydantic.BaseModel):
    user: "User"
    post: "Post"
    type: typing.Literal["read", "like", "share"]

    timestamp: datetime.datetime

    def __hash__(self):
        return hash((self.user.id, self.post.id, self.type))


class Post(pydantic.BaseModel):
    id: str
    user: "User"
    content: str

    reads: typing.List[Interaction] = []
    likes: typing.List[Interaction] = []
    shares: typing.List[Interaction] = []
    comments: typing.List["Post"] = []

    timestamp: datetime.datetime

    def __hash__(self):
        return hash(self.id)
