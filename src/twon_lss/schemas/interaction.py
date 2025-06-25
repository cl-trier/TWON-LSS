import datetime
import enum

import pydantic

from .user import User


class InteractionTypes(str, enum.Enum):
    read = "read"
    like = "like"
    share = "share"


class Interaction(pydantic.BaseModel):
    user: User
    type: InteractionTypes

    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    def __hash__(self):
        return hash((self.user.id, self.type))
