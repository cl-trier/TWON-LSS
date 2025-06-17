import rich

from twon_lss import Graph


my_graph = Graph.from_random_regular(5, 10)
rich.print(my_graph)

for user in my_graph:
    rich.print(user)
    rich.print(my_graph.get_neighbors(user))
