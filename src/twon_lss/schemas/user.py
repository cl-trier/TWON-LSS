import pydantic

from twon_lss.agent import AgentInterface


class User(pydantic.BaseModel):
    """
    Represents a user in the simulation.

    The `User` class models individual users within the social media simulation,
    each with a unique identifier and an agent that controls their behavior.

    Attributes:
        id (int | str): A unique identifier of the user as either a string or integer.
        agent (AgentInterface): An `AgentInterface` object that controls the user's behavior in the simulation.

    Example:
        >>> from src.twon_lss.schemas import User

        ... user = User(
        ...     id="U001",
        ...     agent=None
        ... )
    """

    id: int | str
    agent: AgentInterface | None = None

    def __hash__(self):
        return hash(self.id)
