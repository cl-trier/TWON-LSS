import datetime
import typing

import pydantic

from .user import User
from .interaction import Interaction, InteractionTypes


class Post(pydantic.BaseModel):
    id: str | int
    user: User
    content: str

    interactions: typing.List[Interaction] = pydantic.Field(default_factory=list)
    comments: typing.List["Post"] = pydantic.Field(default_factory=list)

    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    def __hash__(self):
        return hash(self.id)

    def add_comment(self, comment: "Post") -> None:
        self.comments.append(comment)
        self.interactions = list(
            filter(
                lambda interaction: interaction.type is not InteractionTypes.read,
                self.interactions,
            )
        )

    def get_interactions(
        self,
    ) -> typing.Dict[InteractionTypes, typing.List[Interaction]]:
        return {
            i_type: list(
                filter(
                    lambda interaction: i_type == interaction.type, self.interactions
                )
            )
            for i_type in InteractionTypes
        }
