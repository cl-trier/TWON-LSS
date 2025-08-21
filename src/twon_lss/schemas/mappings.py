import uuid

import pydantic


class UserID(pydantic.RootModel):
    root: str = pydantic.Field(default_factory=lambda: f"user-{uuid.uuid4()}")

    def __hash__(self):
        return hash(self.root)


class PostID(pydantic.RootModel):
    root: str = pydantic.Field(default_factory=lambda: f"post-{uuid.uuid4()}")

    def __hash__(self):
        return hash(self.root)
