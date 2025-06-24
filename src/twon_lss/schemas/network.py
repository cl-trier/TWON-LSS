import typing

import pydantic

import networkx

from .user import User


class Network(pydantic.BaseModel):
    graph: networkx.Graph = networkx.Graph()

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def get_neighbors(self, user: "User") -> typing.List["User"]:
        return list(self.graph.neighbors(user))

    @classmethod
    def from_graph(cls, graph: networkx.Graph) -> "Network":
        return cls(structure=Network._relabel_to_users(graph))

    @staticmethod
    def _relabel_to_users(graph: networkx.Graph) -> networkx.Graph:
        return networkx.relabel_nodes(graph, mapping=lambda node_id: User(id=node_id))

    def __iter__(self):
        return iter(self.graph)

    def __next__(self):
        return next(self.graph)

    def __str__(self):
        return str(self.graph)
