import datetime
import typing

import pydantic

if typing.TYPE_CHECKING:
    from .user import User
    from .interaction import Interaction


class Post(pydantic.BaseModel):
    id: str
    user: "User"
    content: str

    reads: typing.List["Interaction"] = []
    likes: typing.List["Interaction"] = []
    shares: typing.List["Interaction"] = []
    comments: typing.List["Post"] = []

    timestamp: datetime.datetime

    def __hash__(self):
        return hash(self.id)
