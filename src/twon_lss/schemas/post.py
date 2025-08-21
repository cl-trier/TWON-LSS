import datetime
import typing
import enum
import uuid

import pydantic

from twon_lss.schemas.user import User


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
        ...     reads=[],
        ...     likes=[],
        ... )
    """

    user: User
    content: str

    reads: typing.List[User] = pydantic.Field(default_factory=list)
    likes: typing.List[User] = pydantic.Field(default_factory=list)

    id: str = pydantic.Field(default_factory=lambda: f"post-{uuid.uuid4()}")
    timestamp: int = 0

    def __hash__(self):
        return hash(self.id)


