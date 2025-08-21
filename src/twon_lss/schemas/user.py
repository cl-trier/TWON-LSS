import pydantic

from twon_lss.schemas.feed import Feed
from twon_lss.schemas.mappings import UserID


class User(pydantic.BaseModel):
    id: UserID = pydantic.Field(default_factory=UserID)
    posts: Feed = pydantic.Field(default_factory=Feed)

    def __hash__(self):
        return hash(self.id)
