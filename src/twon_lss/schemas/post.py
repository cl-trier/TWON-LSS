import datetime
import typing

import pydantic

from .user import User
from .interaction import Interaction, InteractionTypes


class Post(pydantic.BaseModel):
    """
    Models a social media post/comment for the simulation.

    The Post class represents individual posts or comments within the social media
    simulation, supporting nested comment structures and user interactions.

    Attributes:
        id (str | int): A unique identifier of the post as either a string or integer.
        user (User): A User object representing the author of the post.
        content (str): The text content of the post as a string.
        interactions (List[Interaction]): A list of Interaction objects representing user interactions (default: []).
        comments (List[Post]): A list of Post objects representing comments, allowing for nested comment structures (default: []).
        timestamp (datetime.datetime): The timestamp of post creation (default: current datetime.now).

    Example:
        >>> from src.twon_lss.schemas import Post

        >>> post = Post(
        ...     id="P001",
        ...    user=user,
        ...    content="This is a sample post content",
        ...    interactions=[],  # list of Interaction objects
        ...    comments=[],      # list of Post objects
        ... )
    """

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
