import rich
import networkx

from twon_lss.schemas import Network


network = Network.from_graph(networkx.random_regular_graph(5, 10))
rich.print(network)

for user in network:
    rich.print(user)
    rich.print(network.get_neighbors(user))
