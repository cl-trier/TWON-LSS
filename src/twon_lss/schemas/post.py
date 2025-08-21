import typing

import pydantic

from twon_lss.schemas.mappings import UserID, PostID


class Post(pydantic.BaseModel):
    user: UserID
    content: str

    reads: typing.List[UserID] = pydantic.Field(default_factory=list)
    likes: typing.List[UserID] = pydantic.Field(default_factory=list)

    id: PostID = pydantic.Field(default_factory=PostID)
    timestamp: int = 0

    def __hash__(self):
        return hash(self.id)


