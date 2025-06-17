import typing

import pydantic

import networkx

from twon_lss.schemas import User

__all__ = ["Graph"]


class GraphArgs(pydantic.BaseModel):
    pass


class Graph(pydantic.BaseModel):
    structure: networkx.Graph = networkx.Graph()

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def get_neighbors(self, user: "User") -> typing.List["User"]:
        return list(self.structure.neighbors(user))

    @classmethod
    def from_random_regular(cls, d: int, n: int) -> "Graph":
        return cls(
            structure=Graph._relabel_to_users(networkx.random_regular_graph(d, n))
        )

    @staticmethod
    def _relabel_to_users(graph: networkx.Graph) -> networkx.Graph:
        return networkx.relabel_nodes(graph, mapping=lambda node_id: User(id=node_id))

    def __iter__(self):
        return iter(self.structure)

    def __next__(self):
        return next(self.structure)

    def __str__(self):
        return str(self.structure)
