import datetime
import typing

import pydantic

if typing.TYPE_CHECKING:
    from .user import User
    from .post import Post


class Interaction(pydantic.BaseModel):
    user: "User"
    post: "Post"
    type: typing.Literal["read", "like", "share"]

    timestamp: datetime.datetime

    def __hash__(self):
        return hash((self.user.id, self.post.id, self.type))
