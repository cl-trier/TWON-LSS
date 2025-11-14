import typing
import uuid

import pydantic

from twon_lss.schemas.user import User


class Post(pydantic.BaseModel):
    user: User
    content: str

    reads: typing.Set[User] = pydantic.Field(default_factory=set)
    likes: typing.Set[User] = pydantic.Field(default_factory=set)

    id: str = pydantic.Field(default_factory=lambda: f"post-{uuid.uuid4()}")
    timestamp: int = 0
    embedding: typing.Optional[typing.List[float]] = None

    def __hash__(self):
        return hash(self.id)
    
    @pydantic.field_serializer('reads', 'likes')
    def serialize_sets(self, v: typing.Set[User]) -> typing.List[User]:
        return list(v)
