import typing

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
        ... neighbors = network.get_neighbors(user)
        ... for user in network:
        ...    print(user)
    """

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
