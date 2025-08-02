import datetime
import typing
import enum
import uuid

import pydantic

from twon_lss.schemas.user import User


class InteractionTypes(str, enum.Enum):
    """
    Enum defining the types of user interactions with posts.

    Supported interaction types:
        read: User has read the post
        like: User has liked the post
    """

    read = "read"
    like = "like"


class Interaction(pydantic.BaseModel):
    """
    Represents user interactions with posts.

    The Interaction class models various types of user engagement with posts,
    including reads, likes, and shares, with automatic timestamping.

    Attributes:
        user (User): A User object representing who performed the interaction.
        type (InteractionTypes): An InteractionTypes enum value specifying the interaction type (read, like, or share).
        timestamp (datetime.datetime): The timestamp when the interaction occurred, automatically set to current time if not provided.

    Example:
        >>> from src.twon_lss.schemas import Interaction, InteractionTypes
        ... interaction = Interaction(
        ...    user=user,
        ...    type=InteractionTypes.like
        ... )
    """

    user: "User"
    type: InteractionTypes

    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    def __hash__(self):
        return hash((self.user.id, self.type))


class Post(pydantic.BaseModel):
    """
    Models a social media post/comment for the simulation.

    The Post class represents individual posts or comments within the social media
    simulation, supporting nested comment structures and user interactions.

    Attributes:
        user (User): A User object representing the author of the post.
        content (str): The text content of the post as a string.
        interactions (List[Interaction]): A list of Interaction objects representing user interactions (default: []).
        comments (List[Post]): A list of Post objects representing comments, allowing for nested comment structures (default: []).
        id (str): A unique identifier of the post as either a string (default: user-uuid4())
        timestamp (datetime.datetime): The timestamp of post creation (default: current datetime.now).

    Example:
        >>> from src.twon_lss.schemas import Post
        ... post = Post(
        ...     user=user,
        ...     content="This is a sample post content",
        ...     interactions=[],  # list of Interaction objects
        ...     comments=[],      # list of Post objects
        ... )
    """

    user: "User"
    content: str

    interactions: typing.List["Interaction"] = pydantic.Field(default_factory=list)
    comments: typing.List["Post"] = pydantic.Field(default_factory=list)

    id: str = pydantic.Field(default_factory=lambda: f"post-{uuid.uuid4()}")
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
    ) -> typing.Dict["InteractionTypes", typing.List["Interaction"]]:
        return {
            i_type: list(
                filter(
                    lambda interaction: i_type == interaction.type, self.interactions
                )
            )
            for i_type in InteractionTypes
        }
