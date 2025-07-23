import pydantic


class User(pydantic.BaseModel):
    """
    Represents a user in the simulation.

    The `User` class models individual users within the social media simulation.

    Attributes:
        id (int | str): A unique identifier of the user as either a string or integer.

    Example:
        >>> from src.twon_lss.schemas import User
        ... user = User(
        ...     id="U001",
        ... )
    """

    id: int | str

    def __hash__(self):
        return hash(self.id)
