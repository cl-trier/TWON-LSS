import typing
import uuid

import pydantic

from twon_lss.schemas.post import Post


class User(pydantic.BaseModel):
    """
    Represents a user in the simulation.

    The `User` class models individual users within the social media simulation.

    Attributes:
        id (str): A unique identifier of the user as either a string (default: user-uuid4()).

    Example:
        >>> from src.twon_lss.schemas import User
        ... user = User()
    """

    id: str = pydantic.Field(default_factory=lambda: f"user-{uuid.uuid4()}")
    history: typing.List[Post] = pydantic.Field(default_factory=list)

    def __hash__(self):
        return hash(self.id)
