import datetime
import typing

import pydantic

from .user import User
from .interaction import Interaction, InteractionTypes


class Post(pydantic.BaseModel):
    id: str | int
    user: "User"
    content: str

    interactions: typing.List["Interaction"] = pydantic.Field(default_factory=list)
    comments: typing.List["Post"] = pydantic.Field(default_factory=list)

    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    @pydantic.computed_field
    @property
    def interactions_grouped(self) -> typing.Dict[InteractionTypes, Interaction]:
        return {
            i_type: filter(
                lambda interaction: i_type == interaction.type, self.interactions
            )
            for i_type in InteractionTypes
        }

    def __hash__(self):
        return hash(self.id)
