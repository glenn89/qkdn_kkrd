import random
import numpy as np

if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    for i in range(5):
        for j in range(5):
            if j == 2:
                break
            print(f"i={i}, j={j}")

    # results = np.random.binomial(500, 0.08)
    # print(results)
    #
    # # Set the random seed for reproducibility (optional)
    # np.random.seed(42)
    #
    # # Number of time steps
    # num_steps = 100
    #
    # # Initial mean and standard deviation
    # initial_mean = 5
    # initial_std_dev = 3
    #
    # # Lists to store qber values and time steps
    # time_steps = np.arange(num_steps)
    # qber_values = []
    #
    # # Generate qber values over multiple time steps
    # for step in range(num_steps):
    #     # Generate a random float from a normal distribution with current mean and standard deviation
    #     qber = np.random.normal(loc=initial_mean, scale=initial_std_dev)
    #
    #     # Clip the value to ensure it falls within a valid range (e.g., between 0 and 10)
    #     qber = np.clip(qber, 0, 10)
    #
    #     # Append the qber value to the list
    #     qber_values.append(qber)
    #
    #     # Adjust mean and standard deviation for the next time step (for demonstration purposes)
    #     # initial_mean += 0.1
    #     initial_std_dev -= 0.02
    #
    #     if initial_std_dev < 0:
    #         initial_std_dev = 0.
    #
    # # Plot the qber values over time
    # plt.plot(time_steps, qber_values, label='QBER')
    # plt.xlabel('Time Steps')
    # plt.ylabel('QBER')
    # plt.title('QBER Over Time')
    # plt.legend()
    # plt.show()
    #
    # def generate_packet_counts(size, alpha):
    #     # 파레토 분포를 따르는 패킷 수 생성
    #     pareto_counts = 30 - np.random.pareto(alpha, size) * 30
    #     print(pareto_counts)
    #     print(np.mean(pareto_counts), max(pareto_counts), min(pareto_counts))
    #     for i in range(len(pareto_counts)):
    #         if pareto_counts[i] < 0:
    #             pareto_counts[i] = 0
    #
    #     return pareto_counts.astype(int)
    #
    #
    # def simulate_packet_generation(steps, alpha):
    #     # 각 스텝에서 생성되는 패킷 수 생성
    #     packet_counts = generate_packet_counts(steps, alpha)
    #
    #     # 패킷 수 시각화
    #     plt.plot(range(1, steps + 1), packet_counts, marker='o', linestyle='-')
    #     plt.xlabel('Step', fontsize=15)
    #     plt.ylabel('The number of quantum key', fontsize=15)
    #     plt.title('Simulation of Quantum key Generation', fontsize=15)
    #     plt.xticks(fontsize=15)
    #     plt.yticks(fontsize=15)
    #     plt.grid(True)
    #     plt.show()
    #
    #
    # # 시뮬레이션 파라미터 설정
    # steps = 100  # 시뮬레이션 스텝 수
    # alpha = 12     # 파레토 분포의 모수
    #
    # # 패킷 생성 시뮬레이션
    # simulate_packet_generation(steps, alpha)

#
# cost266_desc = {
#     'NAME': "COST266",
#
#     'QKD_NODES': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
#                   15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
#
#     'QKD_TOPOLOGY': [
#         [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
#     ],
#
#     'NUM_QKD_NODE': 28,
#     'NUM_QKD_LINK': 41,
#
#     'NUM_DIRECT_KEY_POOL': 82,
#     'NUM_INDIRECT_KEY_POOL': 674,
#
#
#     # QKD setting
#     'KEY_AVERAGE_RATE': 5,  # 개수
#     'INITIAL_LIFE_TIME': 5,  # step
#     'LIFE_TIME': 7,  # step
#
#     # User setting
#     'PATH_SEQUENCE': 'KEY',  #
#     'NUM_INITIAL_DIRECT_KEY': 15,
#     'NUM_INITIAL_INDIRECT_KEY': 3,
#     'NUM_DIRECT_KEY_THRESHOLD': 3,
#
#     # ENV setting
#     'MAX_DIRECT_KEY': 5,
#     'MAX_INDIRECT_KEY': 5,
#     'REWARD_INDICATOR': 1.0,
#     'VERBOSE': 1,
#     'MODE': 'REPLACE',  # REPLACE(default), LIMIT
#
# }
#
#
    import networkx as nx
    import matplotlib.pyplot as plt

    # NSFNet 노드 정의: 도시 이름 및 위치
    nsfnet_nodes = {
        1: {"city": "Ithaca", "pos": (4, 8)},
        2: {"city": "Princeton", "pos": (6, 6)},
        3: {"city": "Pittsburgh", "pos": (5, 5)},
        4: {"city": "Ann Arbor", "pos": (3, 4)},
        5: {"city": "Champaign", "pos": (3, 3)},
        6: {"city": "Lincoln", "pos": (2, 2)},
        7: {"city": "Boulder", "pos": (1, 3)},
        8: {"city": "Salt Lake City", "pos": (1, 5)},
        9: {"city": "Seattle", "pos": (0, 8)},
        10: {"city": "San Diego", "pos": (0, 2)},
        11: {"city": "Sunnyvale", "pos": (0, 6)},
        12: {"city": "Los Angeles", "pos": (0, 4)},
        13: {"city": "Houston", "pos": (4, 0)},
        14: {"city": "Atlanta", "pos": (5, 2)},
    }

    # NSFNet 엣지 정의: 노드 간 연결 및 가중치
    nsfnet_edges = [
        (1, 2, {"weight": 2}),
        (1, 3, {"weight": 3}),
        (2, 3, {"weight": 1}),
        (3, 4, {"weight": 4}),
        (4, 5, {"weight": 5}),
        (5, 6, {"weight": 3}),
        (6, 7, {"weight": 2}),
        (7, 8, {"weight": 4}),
        (8, 9, {"weight": 5}),
        (9, 11, {"weight": 6}),
        (11, 12, {"weight": 1}),
        (12, 10, {"weight": 2}),
        (10, 13, {"weight": 4}),
        (13, 14, {"weight": 3}),
        (14, 1, {"weight": 6}),
    ]

    # 그래프 생성 및 확장
    G = nx.Graph()
    for node, attr in nsfnet_nodes.items():
        G.add_node(node, **attr)

    # 엣지 확장: 각 링크에 두 개의 노드 추가
    extra_node_id = max(nsfnet_nodes.keys()) + 1
    for u, v, attr in nsfnet_edges:
        # 기존 엣지를 두 개의 새로운 엣지로 분리
        new_node1 = extra_node_id
        new_node2 = extra_node_id + 1
        extra_node_id += 2

        # 두 새로운 노드의 위치를 기존 노드 위치의 중간으로 설정
        pos_u = nsfnet_nodes[u]["pos"]
        pos_v = nsfnet_nodes[v]["pos"]
        pos_new1 = ((pos_u[0] + pos_v[0]) / 2, (pos_u[1] + pos_v[1]) / 2)
        pos_new2 = ((pos_new1[0] + pos_v[0]) / 2, (pos_new1[1] + pos_v[1]) / 2)

        # 그래프에 새로운 노드 추가
        G.add_node(new_node1, city=f"Node {new_node1}", pos=pos_new1)
        G.add_node(new_node2, city=f"Node {new_node2}", pos=pos_new2)

        # 기존 노드와 새로운 노드 연결
        G.add_edge(u, new_node1, weight=attr["weight"] / 3)  # 분리된 링크의 가중치
        G.add_edge(new_node1, new_node2, weight=attr["weight"] / 3)
        G.add_edge(new_node2, v, weight=attr["weight"] / 3)

    # 기존 노드와 새로운 노드의 위치 가져오기
    pos = {node: data["pos"] for node, data in G.nodes(data=True)}
    labels = {node: data["city"] for node, data in G.nodes(data=True)}
    weights = nx.get_edge_attributes(G, "weight")

    print()
    print(nx.to_numpy_array(G, weight='weight'))

    # 시각화
    plt.figure(figsize=(12, 8))
    nx.draw(
        G,
        pos,
        with_labels=True,
        labels=labels,
        node_color="lightblue",
        node_size=800,
        font_size=8,
        font_weight="bold",
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels={e: f"{w:.2f}" for e, w in weights.items()}, font_size=8)
    plt.title("NSFNet Topology with Additional Nodes on Each Link")
    plt.axis("off")
    plt.show()