import pydantic

from twon_lss.agent import AgentInterface


class User(pydantic.BaseModel):
    id: int | str
    agent: AgentInterface | None = None

    def __hash__(self):
        return hash(self.id)
