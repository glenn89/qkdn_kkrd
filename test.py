import numpy as np

#  (NODES,  LINKS)  (28,  41)
NODES = [
    "Dublin", "Glasgow", "London", "Paris", "Brussels", "Amsterdam", "Hamburg", "Copenhagen",
    "Oslo", "Stockholm", "Berlin", "Frankfurt", "Munich", "Zurich", "Lyon", "Bordeaux",
    "Madrid", "Barcelona", "Milan", "Rome", "Vienna", "Prague", "Budapest", "Zagreb",
    "Belgrade", "Athens", "Warsaw", "Strasbourg"
]
idx = {name: i for i, name in enumerate(NODES)}
N = len(NODES)

LINKS = [
    ("Dublin", "Glasgow"), ("Dublin", "London"),
    ("Glasgow", "Amsterdam"), ("London", "Amsterdam"),
    ("London", "Paris"), ("Paris", "Brussels"),
    ("Brussels", "Amsterdam"), ("Amsterdam", "Hamburg"),
    ("Frankfurt", "Brussels"), ("Paris", "Strasbourg"),
    ("Strasbourg", "Frankfurt"), ("Paris", "Lyon"),
    ("Lyon", "Zurich"), ("Zurich", "Strasbourg"),
    ("Zurich", "Milan"), ("Milan", "Munich"),
    ("Munich", "Frankfurt"), ("Munich", "Berlin"),
    ("Berlin", "Hamburg"), ("Paris", "Bordeaux"),
    ("Bordeaux", "Madrid"), ("Madrid", "Barcelona"),
    ("Barcelona", "Lyon"), ("Milan", "Rome"),
    ("Rome", "Zagreb"), ("Zagreb", "Vienna"),
    ("Vienna", "Munich"), ("Vienna", "Prague"),
    ("Prague", "Berlin"), ("Rome", "Athens"),
    ("Athens", "Belgrade"), ("Belgrade", "Zagreb"),
    ("Belgrade", "Budapest"), ("Budapest", "Prague"),
    ("Budapest", "Warsaw"), ("Warsaw", "Berlin"),
    ("Warsaw", "Stockholm"), ("Stockholm", "Oslo"),
    ("Oslo", "Copenhagen"), ("Copenhagen", "Hamburg"),
    ("Hamburg", "Frankfurt")
]


def build_edge_matrix(nodes, links):
    n = len(nodes)
    m = np.zeros((n, n), dtype=int)
    name_to_i = {name: i for i, name in enumerate(nodes)}
    for u, v in links:
        i, j = name_to_i[u], name_to_i[v]
        m[i, j] = 1
        m[j, i] = 1
    np.fill_diagonal(m, 0)
    return m


cost266_edge_matrix = build_edge_matrix(NODES, LINKS)

assert np.all(cost266_edge_matrix.T == cost266_edge_matrix)
assert np.all(np.diag(cost266_edge_matrix) == 0)


def build_distance_matrix(nodes, links, distances, use_inf_for_absent=False, validate=False):
    assert len(links) == len(distances), "len(distances)  must  equal  len(links)."
    n = len(nodes)
    M = np.full((n, n), np.inf if use_inf_for_absent else 0.0, dtype=int)
    name_to_i = {name: i for i, name in enumerate(nodes)}

    for (u, v), d in zip(links, distances):
        i, j = name_to_i[u], name_to_i[v]
        M[i, j] = int(d)
        M[j, i] = int(d)

    np.fill_diagonal(M, 0.0)

    if validate:
        assert np.allclose(M, M.T), "distance_matrix  must  be  symmetric."
        for (u, v), d in zip(links, distances):
            i, j = name_to_i[u], name_to_i[v]
            assert M[i, j] > 0, f"distance  for  edge  {u}-{v}  must  be  >  0."
        if not use_inf_for_absent:
            pass
    return M


DIST = [
    462, 690,
    1067, 540,
    514, 393,
    259, 552,
    474, 600,
    271, 594,
    507, 218,
    327, 552,
    456, 757,
    381, 747,
    834, 760,
    796, 720,
    783, 400,
    434, 376,
    420, 1500,
    1209, 551,
    474, 668,
    819, 775,
    1213, 623,
    722, 540,
    592
]

cost266_distance_matrix = build_distance_matrix(
    NODES, LINKS, DIST,
    use_inf_for_absent=False,  # 비연결은  0.0으로
    validate=False  # 값  채운  후  True로  바꿔  점검
)

print(cost266_edge_matrix)
print(cost266_distance_matrix)


