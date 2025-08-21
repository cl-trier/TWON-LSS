import typing
import json
import functools

import pydantic

import networkx

from twon_lss.schemas.user import User


class Network(pydantic.RootModel):
    """
    Represents the social network structure using NetworkX.

    The Network class models the connections and relationships between users
    in the social media simulation using a NetworkX graph structure.
    The class supports iteration over the network users.

    Attributes:
        graph (networkx.Graph): A NetworkX Graph object representing the network connections between users (default: empty graph).

    Example:
        >>> from src.twon_lss.schemas import Network
        ... import networkx as nx
        ... graph = nx.Graph()
        ... network = Network.from_graph(graph)
        ... neighbors = network.neighbors[user]
        ... for user in network:
        ...    print(user)
    """

    root: networkx.Graph = networkx.Graph()

    _neighbors: typing.Dict[User, typing.List[User]]

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, _: typing.Any):
        self._neighbors = {
            user: self.root.neighbors(user)
            for user in self.root.nodes
        }

    def __iter__(self):
        return iter(self.root.nodes())

    def __len__(self):
        return len(self.root.nodes())
    
    @pydantic.computed_field()
    @functools.cached_property
    def neighbors(self) -> typing.Dict[User, typing.List[User]]:
        return self._neighbors

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
