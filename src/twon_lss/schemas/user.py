import pydantic


class User(pydantic.BaseModel):
    id: int | str

    def __hash__(self):
        return hash(self.id)
