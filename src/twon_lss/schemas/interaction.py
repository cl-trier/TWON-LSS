import datetime
import enum

import pydantic

from .user import User


class InteractionTypes(str, enum.Enum):
    """
    Enum defining the types of user interactions with posts.
    
    Supported interaction types:
        read: User has read the post
        like: User has liked the post
        share: User has shared the post
    """
    read = "read"
    like = "like"
    share = "share"


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
        ```python
        from src.twon_lss.schemas import Interaction, InteractionTypes
        
        interaction = Interaction(
            user=user,
            type=InteractionTypes.like
        )
        ```
    """
    user: User
    type: InteractionTypes

    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    def __hash__(self):
        return hash((self.user.id, self.type))
