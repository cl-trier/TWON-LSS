import typing
import json
import functools
import logging

import pydantic

import networkx

from twon_lss.schemas.mappings import UserID


class Network(pydantic.RootModel):
    root: networkx.Graph = networkx.Graph()

    _neighbors: typing.Dict[UserID, typing.List[UserID]]

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
    def neighbors(self) -> typing.Dict[UserID, typing.List[UserID]]:
        logging.debug([(key, val) for key, val in self._neighbors.items()])
        return self._neighbors

    def relabel(self, labels: typing.List[typing.Any]) -> "Network":
        assert len(self.root) == len(labels)
        return Network(networkx.relabel_nodes(self.root, mapping=lambda node_id: labels[node_id]))

    def to_json(self, path: str) -> None:
        json.dump(
            networkx.node_link_data(self.root, edges="edges"),
            open(path, "w"),
            indent=4,
        )
