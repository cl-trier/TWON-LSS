import uuid

import pydantic


class User(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=lambda: f"user-{uuid.uuid4()}")

    def __hash__(self):
        return hash(self.id)
