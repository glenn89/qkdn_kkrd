import networkx as nx

G = nx.Graph()

G.add_edge(0, 2)
G.add_edge(2, 3)

G.add_edge(0, 1)
G.add_edge(1, 3)

print(nx.shortest_path(G, 0, 3))