import pydantic

from twon_lss.schemas import Feed, Network


class SimulationArgs(pydantic.BaseModel):
    num_steps: int


class Simulation(pydantic.BaseModel):
    args: SimulationArgs

    network: Network
    feed: Feed = Feed()

    def __call__(self) -> None:
        pass
