import typing

import pydantic

from twon_lss.graph import Graph
from twon_lss.schemas import Post


class SimulationArgs(pydantic.BaseModel):
    num_steps: int


class Simulation(pydantic.BaseModel):
    args: SimulationArgs

    graph: Graph
    feed: typing.List[Post] = []

    def __call__(self) -> None:
        pass
