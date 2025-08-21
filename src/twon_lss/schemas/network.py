import typing
import json

import pydantic

import networkx

from twon_lss.schemas.user import User


class Network(pydantic.RootModel):
    root: networkx.Graph = networkx.Graph()

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __iter__(self):
        return iter(self.root.nodes())

    def __len__(self):
        return len(self.root.nodes())

    def get_neighbors(self, user: User) -> typing.List[User]:
        return list(self.root.neighbors(user))

    @classmethod
    def from_graph(cls, graph: networkx.Graph, users: typing.List[User]) -> "Network":
        return cls(Network._relabel_to_users(graph, users))

    @staticmethod
    def _relabel_to_users(
        graph: networkx.Graph, users: typing.List[User]
    ) -> networkx.Graph:
        assert len(graph) == len(users)
        return networkx.relabel_nodes(graph, mapping=lambda node_id: users[node_id])

    def to_json(self, path: str) -> None:
        json.dump(
            networkx.node_link_data(
                networkx.relabel_nodes(self.root, mapping=lambda user: user.id),
                edges="edges",
            ),
            open(path, "w"),
            indent=4,
        )
