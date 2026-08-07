import copy
import csv
import math
import pickle
from collections import defaultdict
from itertools import combinations
from random import random

import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import topology_conf


# ===================== 95% 신뢰구간 유틸 =====================
_T_TABLE_95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447,
                7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179,
                13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101,
                19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064,
                25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045}


def _t_critical(df, confidence=0.95):
    """자유도 df에 대한 양측 t 임계값. scipy가 있으면 정확값, 없으면 표에서 조회."""
    try:
        from scipy import stats
        return float(stats.t.ppf(0.5 + confidence / 2.0, df))
    except ImportError:
        if df in _T_TABLE_95:
            return _T_TABLE_95[df]
        if df > 29:
            return 1.96
        return _T_TABLE_95[max(k for k in _T_TABLE_95 if k <= df)]


def confidence_interval(samples, confidence=0.95):
    """시뮬레이션 표본 리스트 -> 평균/신뢰구간 하한(min)/상한(max)/반폭/표준편차."""
    a = np.asarray(samples, dtype=float)
    n = a.size
    if n == 0:
        return dict(n=0, mean=0.0, lower=0.0, upper=0.0, half=0.0,
                    std=0.0, sem=0.0, obs_min=0.0, obs_max=0.0)
    mean = float(a.mean())
    if n == 1:
        return dict(n=1, mean=mean, lower=mean, upper=mean, half=0.0,
                    std=0.0, sem=0.0, obs_min=mean, obs_max=mean)
    std = float(a.std(ddof=1))              # 표본표준편차 (ddof=1 필수)
    sem = std / np.sqrt(n)                  # 표준오차
    half = sem * _t_critical(n - 1, confidence)
    return dict(n=n, mean=mean, lower=mean - half, upper=mean + half,
                half=half, std=std, sem=sem,
                obs_min=float(a.min()), obs_max=float(a.max()))


def print_confidence_interval(label, ci, unit=""):
    """신뢰구간 결과를 보기 좋게 출력."""
    print(f"  {label:<16} n={ci['n']:<3} mean={ci['mean']:>12.4f}{unit}"
          f"  std={ci['std']:>10.4f}")
    print(f"  {'':<16} 95% CI  min={ci['lower']:>12.4f}{unit}"
          f"  max={ci['upper']:>12.4f}{unit}  (+/-{ci['half']:.4f})")
    print(f"  {'':<16} 실측범위 min={ci['obs_min']:>12.4f}{unit}"
          f"  max={ci['obs_max']:>12.4f}{unit}")
# ============================================================


class Request:
    def __init__(self, max_time_step, topology_conf, dist_probability):
        self.discard_time = 0
        self.ID = 0

        self.rng = np.random.default_rng()
        self.requests = self.make_requests_for_all_steps(T=max_time_step,
                                                         N=topology_conf['NUM_QKD_NODE'],
                                                         p=dist_probability)
        # self.requests = self.make_burst_requests_for_all_steps(T=max_time_step,
        #                                                  N=topology_conf['NUM_QKD_NODE'],
        #                                                  p=dist_probability)

    def make_requests_for_all_steps(self, T, N, p):
        reqs_by_t = []
        iu, ju = np.triu_indices(N, k=1)  # 무방향 예시
        for _ in range(T):
            keep = self.rng.binomial(1, p, size=iu.shape[0]).astype(bool)
            reqs_by_t.append(np.column_stack([iu[keep], ju[keep]]))
        return reqs_by_t

    def make_burst_requests_for_all_steps(self, T, N, p, zipf_a=2.0):
        iu, ju = np.triu_indices(N, k=1)
        total_pairs = len(iu)

        # Step 1: Bernoulli로 전체 총 request 수 결정 (기존과 동일한 총량)
        total_requests = sum(
            self.rng.binomial(1, p, size=total_pairs).sum()
            for _ in range(T)
        )

        # Step 2: Zipf 가중치로 스텝별 비율 결정
        zipf_weights = self.rng.zipf(zipf_a, size=T).astype(float)
        zipf_weights /= zipf_weights.sum()  # 비율 정규화

        # Step 3: 총 request 수를 Zipf 비율에 따라 각 스텝에 배분
        counts = np.floor(zipf_weights * total_requests).astype(int)

        # 반올림 오차로 인한 차이를 마지막 스텝에서 보정
        remainder = total_requests - counts.sum()
        top_indices = np.argsort(zipf_weights)[::-1][:remainder]
        counts[top_indices] += 1

        # Step 4: 각 스텝에서 counts[t]개의 pair를 랜덤 선택
        reqs_by_t = []
        for t in range(T):
            n = int(counts[t])
            if n == 0:
                reqs_by_t.append(np.empty((0, 2), dtype=int))
            else:
                chosen_idx = self.rng.choice(total_pairs, size=n, replace=True)
                reqs_by_t.append(np.column_stack([iu[chosen_idx], ju[chosen_idx]]))

        return reqs_by_t

    def save_requests(self, filename="requests/COST266_10000_requests_01.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.requests, f)

    def load_requests(self, filename="requests/COST266_10000_requests_01.pkl"):
        with open(filename, "rb") as f:
            self.requests = pickle.load(f)


class QuantumEnvironment:
    def __init__(self, max_time_step, topology_type):
        self.G = None
        self.logi_G = None
        self.expand_G = None
        self.topology_list = {
            'SIMPLE': topology_conf.simple_topo,
            'BUTTERFLY': topology_conf.butterfly_topo,
            'KREONET': topology_conf.kreonet_topo,
            'NSFNET': topology_conf.nsfnet_topo,
            'COST266': topology_conf.cost266_topo
        }
        self.topology_conf = self.topology_list[topology_type]
        if self.topology_conf['NAME'] == 'NSFNET':
            self.dist_probability = 0.10
        elif self.topology_conf['NAME'] == 'COST266':
            self.dist_probability = 0.10
        self.metric_type = 'qber'   # type: 'simple_shortest', 'weighted_shortest', 'qber', 'num_key', 'combination'
        self.num_seed = 0
        self.max_time_step = max_time_step
        self.training = None
        self.proactive = None
        self.proactive_type = None

        self.generate_key_size = 0
        self.generate_key_scale = 0
        self.generate_key_time_slot = 0
        self.consume_key_size = 0
        self.consume_mean = 0
        self.consume_std_dev = 0
        self.num_request = 0
        self.num_request_scale = 0
        self.init_qber = None
        self.init_num_channel = None
        self.key_pool_size = 0
        self.key_pool = None

        self.logi_G_edges = None
        self.logi_key_pool = None
        self.expand_key_pool = None
        self.key_pool_min_threshold = None
        self.key_life_time = 0

        self.time_step = 0
        self.lifetime_threshold_1 = None
        self.lifetime_threshold_4 = None
        self.source_node = None
        self.target_node = None
        self.service_duration_time = None
        self.service_routing_path = None
        self.path_length = None
        self.all_possible_edges = None
        self.all_link_delay = None
        self.request_fairness = None

        self.session_blocking = 0
        self.total_generation_keys = 0
        self.proactive_key_generation = 0
        self.proactive_key_consume = 0
        self.proactive_key_expired = 0
        self.proactive_key_consume_for_n_hop = 0
        self.n_hop_proactive_key_generation = 0
        self.n_hop_proactive_key_consume = 0
        self.n_hop_proactive_key_expired = 0
        self.remaining_keys = 0
        self.used_keys = 0
        self.expired_keys = 0
        self.delay = 0
        self.hops = 0

        # 평균 key pool 사용률 / overflow 횟수 누적용 (logi_key_pool 기준)
        self.key_pool_usage_ratio_sum = 0.0  # step마다 (전체 사용 key 수 / 전체 용량) 비율을 누적 -> 평균 계산용
        self.key_pool_usage_count = 0  # 누적 횟수 (평균 계산용 분모)
        self.key_pool_overflow_count = 0  # 용량 초과로 key가 trim(폐기)된 횟수 누적

        self.k = 0
        self.reward = 0
        self.mean_value = 0
        self.std_deviation = 0
        self.count = 0
        self.no_path_count = 0
        self.cumulative_size = 1
        self.cumulative_edge_keys = None
        self.alpha = 0

        self.requests = Request(self.max_time_step, self.topology_conf, self.dist_probability)
        # self.requests.load_requests()


    def generate_topology(self):
        self.G = nx.Graph()
        self.G.add_nodes_from(self.topology_conf['QKD_NODES'])
        # nx.set_node_attributes(self.G, self.topology_conf['QKD_NODES_NAME'], name="name")
        # nx.relabel_nodes(self.G, self.topology_conf['QKD_NODES_NAME'])

        edges = []
        node_1 = np.where(np.array(self.topology_conf['QKD_TOPOLOGY']) > 0)[0]
        node_2 = np.where(np.array(self.topology_conf['QKD_TOPOLOGY']) > 0)[1]

        for (i, j) in zip(node_1, node_2):
            edges.append((i, j))

        # Set edge's weight
        self.G.add_weighted_edges_from(list((edges[n][0], edges[n][1], 0) for n in range(len(edges))))
        edges_attribute = {
            (edges[n][0], edges[n][1]): {
                "weight": self.topology_conf['num_key'][n],
                "num_key": self.topology_conf['num_key'][n],
                "distance": self.topology_conf['num_key'][n],
            } for n in range(len(edges))
        }
        nx.set_edge_attributes(self.G, edges_attribute)
        if self.topology_conf['NAME'] == 'NSFNET' or self.topology_conf['NAME'] == 'COST266':
            for i in range(len(self.G.nodes)):
                for j in range(i + 1, len(self.G.nodes)):  # 대칭 행렬이므로 i < j
                    distance = self.topology_conf['QKD_TOPOLOGY_DISTANCE'][i][j]
                    if distance > 0:  # 가중치가 0이 아닌 경우만 추가
                        self.G.add_edge(i, j, distance=distance)

        self.key_pool.update((key, []) for key in self.G.edges)  # Generate key pool
        self.logi_key_pool.update((key, []) for key in self.G.edges)
        self.logi_G_edges = nx.to_numpy_array(self.G, weight='num_key')
        self.logi_G = copy.deepcopy(self.G)

        # Expand Nodes and Edges
        self.expand_G = copy.deepcopy(self.G)
        next_node_id = len(self.expand_G.nodes) + 1
        edges = list(self.expand_G.edges(data=True))
        for u, v, attr in edges:
            if self.topology_conf['NAME'] == 'NSFNET' or self.topology_conf['NAME'] == 'COST266':
                num_spans = math.ceil(attr['distance'] / 100)
                num_intermediates = max(0, num_spans - 1)
                path_nodes = [u]

                # n개의 중간 노드 생성
                for _ in range(num_intermediates):
                    new_node = next_node_id
                    self.expand_G.add_node(new_node, city=f"Node {new_node}", owner_edge=tuple((u, v)))
                    path_nodes.append(new_node)
                    next_node_id += 1

                path_nodes.append(v)

                # 기존 엣지 제거
                self.expand_G.remove_edge(u, v)

                # 새로 생성된 경로로 edge 연결
                num_key = attr["num_key"]
                for i in range(len(path_nodes) - 1):
                    n1, n2 = path_nodes[i], path_nodes[i + 1]
                    self.expand_G.add_edge(n1, n2, weight=num_key, num_key=num_key, owner_edge=tuple((u, v)))
            else:
                # 기존 엣지 중간에 두 개의 노드를 추가
                new_node1 = next_node_id
                new_node2 = next_node_id + 1
                next_node_id += 2

                # 새 노드 추가
                self.expand_G.add_node(new_node1, city=f"Node {new_node1}", owner_edge=tuple((u, v)))
                self.expand_G.add_node(new_node2, city=f"Node {new_node2}", owner_edge=tuple((u, v)))

                # 엣지 추가
                num_key = attr["num_key"]
                self.expand_G.add_edge(u, new_node1, weight=num_key, num_key=num_key, owner_edge=tuple((u, v)))
                self.expand_G.add_edge(new_node1, new_node2, weight=num_key, num_key=num_key, owner_edge=tuple((u, v)))
                self.expand_G.add_edge(new_node2, v, weight=num_key, num_key=num_key, owner_edge=tuple((u, v)))

                # 기존 엣지 제거
                self.expand_G.remove_edge(u, v)

        self.expand_key_pool.update((key, []) for key in self.expand_G.edges)  # Generate expand key pool
        for edge in self.expand_G.edges:
            self.logi_G.add_edge(edge[0], edge[1], weight=0, num_key=0)
        self.logi_key_pool.update({edge: [] for edge in self.expand_key_pool if edge not in self.logi_key_pool})  # generate logical key pool

        # for edge in self.logi_G.edges:
        #     print(edge)
        # self.G의 논리적 edge 추가
        self.all_possible_edges = list(combinations(self.G.nodes, 2))
        for u, v in self.all_possible_edges:
            if not self.logi_G.has_edge(u, v):
                self.logi_G.add_edge(u, v, weight=0, num_key=0)
            if (u, v) not in self.logi_key_pool and (v, u) not in self.logi_key_pool:
                self.logi_key_pool[(u, v)] = []

        self.key_generation()  # Reflect the number of keys with qber

    # source, target node 추가하여 key pool 업데이트 및 logical graph 만들기
    # next state로 활용 하면 좋을 것 같음
    def update_logical_topology(self):
        max_lifetime, min_lifetime = 0, 0
        G_edges_origin = self.G.edges

        for edge in G_edges_origin:
            min_lifetime = self.key_life_time
            max_lifetime = 0  # 0

            origin_nodes = {edge[0], edge[1]}
            origin_nodes |= {
                n for n, d in self.expand_G.nodes(data=True)
                if d.get("owner_edge") == edge
            }
            H = self.expand_G.subgraph(origin_nodes)
            path = nx.shortest_path(H, edge[0], edge[1])

            if any(self.logi_G[path[i]][path[i + 1]]['num_key'] < self.consume_key_size for i in range(len(path) - 1)):
                continue

            # 경로 상 모든 edge의 key 개수를 리스트로 저장
            key_counts, lifetimes = [], []
            min_key_count = 0
            for i in range(len(path) - 1):
                sorted_key = tuple(sorted((path[i], path[i + 1])))
                key_counts.append(len(self.logi_key_pool[sorted_key]))
                lifetimes.extend(self.logi_key_pool.get(sorted_key, []))
            # 경로 내에 key_pool이 비어있는 edge가 있을 수 있으므로 예외처리 필요

            if key_counts:
                min_key_count = min(key_counts)
                min_lifetime = min(lifetimes)
                max_lifetime = max(lifetimes)
            else:
                min_key_count = 0  # or handle appropriately
                min_lifetime = 0

            for _ in range(min_key_count):
                if max_lifetime - min_lifetime < self.lifetime_threshold_1:
                    # 2) proactive key 생성량 기록
                    self.proactive_key_generation += self.consume_key_size

                    # 3) 경로상 key 소비
                    for i in range(len(path) - 1):
                        sorted_key = tuple(sorted((path[i], path[i+1])))
                        # expand_G에서 소비
                        self.expand_G.edges[sorted_key]['num_key'] -= self.consume_key_size
                        self.expand_key_pool[sorted_key] = self.expand_key_pool[sorted_key][self.consume_key_size:]
                        # logi_G에서 소비
                        self.logi_G.edges[sorted_key]['num_key'] -= self.consume_key_size
                        self.logi_key_pool[sorted_key] = self.logi_key_pool[sorted_key][self.consume_key_size:]
                        self.node_num_heat[edge[0]][edge[1]] += 1
                        self.node_num_heat[edge[1]][edge[0]] += 1

                    # 4) 논리 그래프(edge)에 proactive key 추가
                    if edge in self.logi_key_pool:
                        self.logi_key_pool[edge].extend([min_lifetime] * self.consume_key_size)
                        if len(self.logi_key_pool[edge]) > self.key_pool_size:
                            overflow_amount = len(self.logi_key_pool[edge]) - self.key_pool_size
                            self.logi_key_pool[edge] = self.logi_key_pool[edge][overflow_amount:]
                            self.key_pool_overflow_count += overflow_amount
                        self.logi_G.edges[edge]['num_key'] = len(self.logi_key_pool[edge])

        # N-hop's proactive key generation process
        if self.proactive_type == 'n-hop':
            all_pairs = [p for p in combinations(self.G.nodes, 2) if p not in G_edges_origin]
            copied_G = copy.deepcopy(self.logi_G)
            subnet = nx.subgraph_view(
                copied_G,
                filter_edge=lambda u, v: self.G.has_edge(u, v)
            )

            priority = {}
            for u, v in all_pairs:
                for edge in G_edges_origin:
                    subnet[edge[0]][edge[1]]['weight'] = 100 + (1000 / (self.logi_G[edge[0]][edge[1]]['num_key']) - 1) if self.logi_G[edge[0]][edge[1]]['num_key'] > 1 else 100_000_000
                try:
                    path = nx.shortest_path(subnet, u, v, weight='weight')
                except nx.NetworkXNoPath:
                    continue
                remain_keys = min(
                    subnet.edges[tuple(sorted((path[i], path[i + 1])))]['num_key']
                    for i in range(len(path) - 1)
                )
                distance = len(path) - 1
                priority[(u, v)] = (1 / (remain_keys + 1)) + (1 / distance)
                # priority[(u, v)] = (remain_keys + 1)
                # priority[(u, v)] = 1.0 / distance
            sorted_pairs = sorted(priority, key=priority.get, reverse=True)
            # print(priority)
            # print(sorted_pairs)

            for edge in sorted_pairs:
                u, v = edge
                self.logi_G[u][v]['weight'] = 100 + (1000 / (self.logi_G[u][v]['num_key']) - 1) if self.logi_G[u][v]['num_key'] > 1 else 100_000_000
                path = nx.shortest_path(self.logi_G, u, v, weight='weight')
                if any(self.logi_G[path[i]][path[i+1]]['num_key'] < self.consume_key_size for i in range(len(path) - 1)):
                    continue

                counts, lifetimes = [], []
                for i in range(len(path) - 1):
                    sorted_key = tuple(sorted((path[i], path[i+1])))
                    counts.append(self.logi_G.edges[sorted_key]['num_key'])
                    lifetimes.extend(self.logi_key_pool.get(sorted_key, []))
                if not counts or not lifetimes or any(n <= self.key_pool_min_threshold for n in counts):
                    continue
                min_count = min(counts)
                min_life = min(lifetimes)
                max_life = max(lifetimes)
                existing_nhop = self.logi_G.edges[edge]['num_key'] if self.logi_G.has_edge(*edge) else 0

                # if enough 1-hop keys and lifetime gap < threshold
                if min_count > existing_nhop and (max_life - min_life) < self.lifetime_threshold_4:
                    self.n_hop_proactive_key_generation += self.consume_key_size
                    for i in range(len(path) - 1):
                        sorted_key = tuple(sorted((path[i], path[i+1])))
                        # self.used_keys += self.consume_key_size
                        self.logi_G.edges[sorted_key]['num_key'] -= self.consume_key_size
                        self.logi_key_pool[sorted_key] = self.logi_key_pool[sorted_key][self.consume_key_size:]
                        self.node_num_heat[path[i]][path[i+1]] -= 1
                        self.node_num_heat[path[i+1]][path[i]] -= 1
                        self.proactive_key_consume_for_n_hop += 1
                    if edge in self.logi_key_pool:
                        self.logi_key_pool[edge].extend([min_life] * self.consume_key_size)
                        # key_generation()과 동일하게 용량(key_pool_size) 초과 시 초과분 trim + overflow 카운트
                        if len(self.logi_key_pool[edge]) > self.key_pool_size:
                            overflow_amount = len(self.logi_key_pool[edge]) - self.key_pool_size
                            self.logi_key_pool[edge] = self.logi_key_pool[edge][overflow_amount:]
                            self.key_pool_overflow_count += overflow_amount
                        self.logi_G.edges[edge]['num_key'] = len(self.logi_key_pool[edge])
                        self.node_num_heat[edge[0]][edge[1]] += 1
                        self.node_num_heat[edge[1]][edge[0]] += 1

        # Sorting logi_key_pool
        for key in self.logi_key_pool:
            self.logi_key_pool[key].sort()

    def key_generation(self):
        edges = list(self.expand_G.edges())

        # Generate key with qber
        for edge in edges:
            ######### Apply static generated key #########
            # generated_keys = max(1, int(np.random.normal(loc=self.generate_key_size, scale=self.generate_key_scale, size=1)))
            generated_keys = np.random.randint(0, self.generate_key_size)
            self.total_generation_keys += generated_keys
            # if edge == (0, 15):
            #     print(self.time_step, generated_keys)
            # print("Gen key: ", generated_keys)
            if generated_keys < 0:
                generated_keys = 0

            for _ in range(generated_keys):
                life_time = self.key_life_time   # np.random.randint(3, self.key_life_time)
                self.expand_key_pool[edge].append(life_time)
                self.logi_key_pool[edge].append(life_time)

            if len(self.logi_key_pool[edge]) > self.key_pool_size:
                overflow_amount = len(self.logi_key_pool[edge]) - self.key_pool_size
                self.logi_key_pool[edge] = self.logi_key_pool[edge][overflow_amount:]
                self.key_pool_overflow_count += overflow_amount

            self.expand_G[edge[0]][edge[1]]['num_key'] = len(self.expand_key_pool[edge])
            self.logi_G[edge[0]][edge[1]]['num_key'] = len(self.logi_key_pool[edge])

            for key in self.logi_key_pool:
                self.logi_key_pool[key].sort()
            for key in self.expand_key_pool:
                self.expand_key_pool[key].sort()

    def accumulate_key_pool_usage(self):
        total_keys_in_pool = sum(len(keys) for keys in self.logi_key_pool.values())
        total_pool_capacity = self.key_pool_size * len(self.logi_key_pool)
        usage_ratio = total_keys_in_pool / total_pool_capacity if total_pool_capacity > 0 else 0

        self.key_pool_usage_ratio_sum += usage_ratio  # ← 누적(더하기)만 함
        self.key_pool_usage_count += 1  # ← 몇 번 더했는지 카운트

        return usage_ratio

    def get_average_key_pool_usage_percent(self):
        """지금까지 누적된 평균 key pool 사용률을 %로 반환"""
        if self.key_pool_usage_count == 0:
            return 0.0
        return (self.key_pool_usage_ratio_sum / self.key_pool_usage_count) * 100

    def plot_topology(self):
        edge_labels = {}
        pos = nx.spring_layout(self.G)

        # nx.draw(self.G, pos=position, node_color=self.topology_conf['QKD_NODES_COLOR_MAP'], with_labels=True)
        nx.draw(self.G, pos, with_labels=True)
        # labels = nx.get_edge_attributes(self.G, 'count_rate')
        for u, v, attr in self.G.edges(data=True):
            edge_labels[(u, v)] = "{0}".format(attr['num_key'])
        # nx.draw_networkx_edge_labels(self.G, position, edge_labels=edge_labels)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels)
        plt.show()

    def plot_expand_topology(self):
        edge_labels = {}
        pos = nx.spring_layout(self.expand_G)

        # nx.draw(self.G, pos=position, node_color=self.topology_conf['QKD_NODES_COLOR_MAP'], with_labels=True)
        nx.draw(self.expand_G, pos, with_labels=True)
        # labels = nx.get_edge_attributes(self.G, 'count_rate')
        for u, v, attr in self.expand_G.edges(data=True):
            edge_labels[(u, v)] = "{0}".format(attr['num_key'])
        # nx.draw_networkx_edge_labels(self.expand_G, pos)
        nx.draw_networkx_edge_labels(self.expand_G, pos, edge_labels=edge_labels)
        plt.show()

    def plot_heatmap(self):
        # Plot the lower triangular part of the heatmap with a red colormap
        lower_triangular = np.tril(self.node_num_heat)
        plt.imshow(lower_triangular, cmap='hot_r', interpolation='nearest', alpha=0.7, vmin=0, vmax=1)
        plt.colorbar(label='Link Strength')

        # Set the background color to white for the parts that do not appear
        plt.gca().set_facecolor('white')

        plt.title('Sophisticated Network with Red Link Strength Heatmap')
        plt.show()

    def reset(self, seed, max_time_step, proactive, proactive_type, threshold):
        self.num_seed = seed
        np.random.seed(self.num_seed)
        self.max_time_step = max_time_step
        self.requests = Request(self.max_time_step, self.topology_conf, self.dist_probability)

        self.generate_key_time_slot = 1
        self.generate_key_size = 10
        self.generate_key_scale = 3
        # max_test_threshold = 10  # 실험에서 쓰는 최대 threshold 값
        # threshold(1~13)를 key_life_time(10) 범위로 선형 변환
        # scaled = (threshold / max_test_threshold) * self.key_life_time
        # # 최소 1, 최대 key_life_time-1 사이로 클램핑
        self.lifetime_threshold_1 = 100   # int(min(max(scaled, 1), self.key_life_time))
        self.lifetime_threshold_4 = threshold   # threshold

        self.proactive = proactive   # proactive
        self.proactive_type = proactive_type #proactive_type
        # self.generate_key_size = np.random.pareto(1, 1).astype(int)[0] * 20
        self.init_num_channel = 3
        self.consume_key_size = 1
        self.consume_mean = 1
        self.consume_std_dev = 2
        self.num_request = 50
        self.num_request_scale = 1
        self.key_life_time = 100
        self.key_pool_size = 100_000
        self.key_pool_min_threshold = 1
        self.key_pool = {}
        self.logi_key_pool = {}
        self.expand_key_pool = {}
        self.service_duration_time = []
        self.service_routing_path = []

        self.time_step = 0
        self.session_blocking = 0
        self.total_generation_keys = 0
        self.proactive_key_generation = 0
        self.proactive_key_consume = 0
        self.proactive_key_expired = 0
        self.proactive_key_consume_for_n_hop = 0
        self.n_hop_proactive_key_generation = 0
        self.n_hop_proactive_key_consume = 0
        self.n_hop_proactive_key_expired = 0
        self.remaining_keys = 0
        self.used_keys = 0
        self.expired_keys = 0
        self.delay = 0
        self.hops = 0
        self.k = 5
        self.reward = 0
        self.alpha = 0.0001

        self.key_pool_usage_ratio_sum = 0.0
        self.key_pool_usage_count = 0
        self.key_pool_overflow_count = 0

        self.generate_topology()
        self.node_num_heat = np.zeros((len(self.G), len(self.G)))
        self.request_fairness = np.zeros((len(self.G), len(self.G)))
        self.all_link_delay = {edge: {} for edge in self.all_possible_edges}
        for edge in self.all_possible_edges:
            self.all_link_delay[edge] = {
                'generated': 0,
                'success': 0,
                'delays': []
            }
        self.count = 0
        self.no_path_count = 0
        self.cumulative_size = 5
        self.cumulative_edge_keys = {}
        self.path_length = {}
        for edge in self.G.edges:
            self.cumulative_edge_keys[edge] = []
            self.G[edge[0]][edge[1]]['num_channel'] = self.init_num_channel

        # self.calculate_based_lifetime_weight(self.G)
        # self.calculate_based_num_key_weight(self.G)

        self.source_node, self.target_node = np.random.choice(np.arange(0, self.topology_conf['NUM_QKD_NODE']), size=2, replace=False)
        # self.source_node, self.target_node = 0, self.topology_conf['NUM_QKD_NODE'] - 1

        state = self.generate_state()
        info = {}
        # self.observation_space = spaces

        return state, info

    def step(self, action):
        state = {}
        info = {}
        delay = 0
        done = False
        truncated = False
        next_state = {}
        num_request = 1

        if self.topology_conf['NAME'] == 'SIMPLE':
            self.source_node, self.target_node = 0, 3
        # else:
        #     if len(action) == 0:
                # self.source_node, self.target_node = random.sample(range(0, self.topology_conf['NUM_QKD_NODE']), 2)
                # self.source_node, self.target_node = np.random.choice(np.arange(0, self.topology_conf['NUM_QKD_NODE']), size=2, replace=False)
                # self.source_node, self.target_node = 0, self.topology_conf['NUM_QKD_NODE'] - 1

        # self.consume_key_size = max(int(np.random.normal(self.consume_mean, self.consume_std_dev)), 1)
        # self.consume_key_size = np.random.pareto(self.consume_mean, 1).astype(int)[0] + 3
        if self.topology_conf['NAME'] == 'SIMPLE':
            if self.time_step == 0:
                self.num_request = 2
            if self.time_step == 1:
                self.num_request = 7
        # else:
        #     # self.num_request = np.random.pareto(4, 1).astype(int)[0] * 5
        #     # self.num_request = np.random.randint(1, 2, 1)[0]

        step_delay = 0
        step_hops = 0
        success_request = 0
        # num_request = max(0, int(np.random.normal(loc=self.num_request, scale=self.num_request_scale, size=1)))
        # num_request = np.random.randint(0, self.num_request)
        # for i in range(num_request):
        #     self.source_node, self.target_node = np.random.choice(np.arange(0, self.topology_conf['NUM_QKD_NODE']),
        #                                                           size=2, replace=False)

        ## Bernoulli Distribution based requests generation
        # iu, ju = np.triu_indices(self.topology_conf['NUM_QKD_NODE'], k=1)  # (i<j)
        # keep = np.random.default_rng().random(iu.shape[0]) < self.dist_probability
        # requests = np.column_stack([iu[keep], ju[keep]]).astype(int)
        if self.proactive:
            self.update_logical_topology()
            # edges_weights = [
            #     f"({u}, {v}): {data.get('num_key', None)}"
            #     for u, v, data in self.logi_G.edges(data=True)
            # ]
            # print("after")
            # print(", ".join(edges_weights))
            # print("time step: ", self.time_step, self.logi_key_pool)
        for src, dst in self.requests.requests[self.time_step]:
            self.source_node, self.target_node = int(src), int(dst)
            routing_path = self.find_routing_path()
            # print("time step: ", self.time_step, "routing path: ", routing_path, "node: ", self.source_node, self.target_node)

            self.apply_routing_path(routing_path)

            # 길이별 카운트 업데이트
            length = len(routing_path) - 1
            self.path_length[length] = self.path_length.get(length, 0) + 1
            self.all_link_delay[(self.source_node, self.target_node)]['generated'] += 1

            if not routing_path:
                self.session_blocking -= 1
            else:
                success_request += 1
                self.reward += 1
                self.request_fairness[self.source_node][self.target_node] += 1
                self.request_fairness[self.target_node][self.source_node] += 1
                delay = 0
                step_hops += len(routing_path) - 1
                if len(routing_path) > 2:
                    for node in routing_path[1:-1]:
                        # self.node_num_heat[routing_path[i]][routing_path[i+1]] += 1
                        # self.node_num_heat[routing_path[i+1]][routing_path[i]] += 1
                        self.used_keys += self.consume_key_size
                        if node in self.G.nodes:
                            delay += 40
                        elif node in self.expand_G.nodes and node not in self.G.nodes:
                            delay += 20
                    delay += 20
                    step_delay += delay
                else:
                    delay += 20
                    step_delay += delay
                # print("timestep: ", self.time_step, "path: ", routing_path, "delay: ", step_delay)
                self.all_link_delay[(self.source_node, self.target_node)]['success'] += 1
                self.all_link_delay[(self.source_node, self.target_node)]['delays'].append(delay)
        self.delay += step_delay / success_request if num_request > 0 and step_delay > 0 else step_delay
        self.hops += step_hops / success_request if success_request > 0 and step_hops > 0 else step_hops
        # print("timestep: ", self.time_step, "num request: ", num_request, "delay: ", self.delay)

            # self.source_node, self.target_node = 1, 9
            # self.source_node, self.target_node = np.random.choice(np.arange(0, self.topology_conf['NUM_QKD_NODE']), size=2, replace=False)
            # for i in self.G.edges:
            #     if i == (0, 1):
            #         # if self.G.edges[i]['num_key'] != len(self.key_pool[i]):
            #         print("time step: ", self.time_step, "edge: ", i, "num_key: ", self.G.edges[i]['num_key'])
            #         print("time step: ", self.time_step, "edge: ", i, "num_key: ", len(self.key_pool[i]), self.key_pool[i])
            #         print()

        for u, v, attr in self.logi_G.edges(data=True):
            self.remaining_keys += attr['num_key']
            sorted_key = tuple(sorted((u, v)))
            if sorted_key in self.expand_G.edges:
                self.expand_key_pool[sorted_key] = [life - 1 for life in self.expand_key_pool[sorted_key]] # lifetime -1
                self.expand_key_pool[sorted_key] = [life for life in self.expand_key_pool[sorted_key] if life >= 1] # remove expired key
                self.expand_G.edges[sorted_key]['num_key'] = len(self.expand_key_pool[sorted_key])
            original_len_logi = len(self.logi_key_pool[sorted_key])
            self.logi_key_pool[sorted_key] = [life - 1 for life in self.logi_key_pool[sorted_key]]  # lifetime -1
            self.logi_key_pool[sorted_key] = [life for life in self.logi_key_pool[sorted_key] if life >= 1]  # remove expired key
            self.logi_G.edges[sorted_key]['num_key'] = len(self.logi_key_pool[sorted_key])
            self.expired_keys += original_len_logi - len(self.logi_key_pool[sorted_key])
            if sorted_key in self.all_possible_edges:
                if sorted_key in self.G.edges():
                    self.proactive_key_expired += original_len_logi - len(self.logi_key_pool[sorted_key])
                else:
                    self.n_hop_proactive_key_expired += original_len_logi - len(self.logi_key_pool[sorted_key])

        if self.time_step != 0 and self.time_step % self.generate_key_time_slot == 0:
            self.key_generation()
            # print(self.G.edges(data=True))
        # print(self.metric_type, self.G.edges(data=True))

        # self.source_node, self.target_node = np.random.choice(np.arange(0, self.topology_conf['NUM_QKD_NODE']), size=2, replace=False)
        # self.source_node, self.target_node = 0, self.topology_conf['NUM_QKD_NODE'] - 1

        self.accumulate_key_pool_usage()

        self.time_step += 1

        # Jain's Fairness Index: 하삼각(i>j) 원소만 추출해 이중 카운트 방지
        served_flat = self.request_fairness[np.tril_indices(len(self.G), k=-1)]
        active = served_flat[served_flat > 0]  # 1회 이상 서비스된 pair만
        if len(active) > 0:
            fairness = (active.sum() ** 2) / (len(active) * (active ** 2).sum())
        else:
            fairness = 1.0  # 요청 없으면 완전 공평으로 처리

        info = {
            'session_blocking': self.session_blocking,
            'total_generation_keys': self.total_generation_keys,
            'remaining_keys': self.remaining_keys,
            'used_keys': self.used_keys,
            'expired_keys': self.expired_keys,
            'graph': self.G,
            'delay': self.delay,
            'hops': self.hops,
            'path_length': self.path_length,
            'heat_map': self.node_num_heat,
            'all_link_delay': self.all_link_delay,
            'request_fairness': fairness,
            'average_key_pool_usage_percent': self.get_average_key_pool_usage_percent(),
            'key_pool_overflow_count': self.key_pool_overflow_count,
        }

        # Check environment | reflect action | reduction resource
        # print(self.time_step, action)
        # print(self.max_time_step, self.reward)
        # self.plot_topology()

        if self.max_time_step == self.time_step:
            done = True

        return next_state, self.reward, done, truncated, info

    def generate_state(self):
        state = {}
        # Configurate state
        adj_matrix_np = nx.to_numpy_array(self.G, weight=None)
        # Normalization adj matrix
        # adj_min, adj_max = adj_matrix_np.min(), adj_matrix_np.max()
        # adj_matrix_np = (adj_matrix_np - adj_min) / (adj_max - adj_min)

        weight_matrix_np = nx.to_numpy_array(self.G, weight='num_key')
        # Normalization weight matrix
        # weight_min, weight_max = weight_matrix_np.min(), weight_matrix_np.max()
        # weight_matrix_np = (weight_matrix_np - weight_min) / (weight_max - weight_min)

        state['obs'] = np.stack([adj_matrix_np, weight_matrix_np], axis=0)  # staked (2, H, W)
        state['obs'] = state['obs'][np.newaxis, :]  # shape convert (1, 2, H, W)

        state['paths'] = self.find_k_shortest_path()
        paths_info = []
        paths_index = self.k * 2
        start_index = 0
        for path in state['paths']:
            paths_info.append(len(path))
            paths_info.append(paths_index + start_index)
            start_index += len(path)
        flattened_paths = [node for path in state['paths'] for node in path]
        paths_info.extend(flattened_paths)
        paths_info = paths_info + [0] * (128 - len(paths_info))

        # Normalization flat_paths
        paths_info = np.array(paths_info)
        # paths_min, paths_max = paths_info.min(), paths_info.max()
        # paths_info = (paths_info - paths_min) / (paths_max - paths_min)
        state['flat_paths'] = paths_info

        # Transform np.array
        state['obs'] = np.array(state['obs'])
        state['flat_paths'] = np.array(state['flat_paths'])
        state['flat_paths'] = state['flat_paths'][np.newaxis, :]

        return state

    def find_routing_path(self):
        accumulate_qber = []
        accumulate_num_key = []
        accumulate_count_rate = []
        loop_nodes = []
        routing_path = []
        routing_path.append(self.source_node)

        # Using weighted shortest path
        # routing_path = nx.shortest_path(self.G, source=0, target=5, weight='num_key')

        if self.metric_type == 'simple_shortest':
            copied_G = copy.deepcopy(self.logi_G)
            subnet = nx.subgraph_view(
                copied_G,
                filter_edge=lambda node_1_id, node_2_id: \
                    True if copied_G.edges[(node_1_id, node_2_id)]['num_key'] >= self.consume_key_size else False
            )

            if len(subnet.edges) == 0 or not nx.has_path(subnet, source=self.source_node, target=self.target_node):
                return []

            # routing_path = nx.shortest_path(subnet, 0, 5)
            routing_path = nx.shortest_path(subnet, self.source_node, self.target_node)

        if self.metric_type == 'weighted_shortest':
            copied_G = copy.deepcopy(self.logi_G)
            subnet = nx.subgraph_view(
                copied_G,
                filter_edge=lambda node_1_id, node_2_id: \
                    True if copied_G.edges[(node_1_id, node_2_id)]['num_key'] >= self.consume_key_size else False
            )
            if len(subnet.edges) == 0 or not nx.has_path(subnet, source=self.source_node, target=self.target_node):
                return []

            # routing_path = nx.shortest_path(subnet, 0, 5)
            for edge in subnet.edges:
                subnet[edge[0]][edge[1]]['weight'] = 100 + (1000 / (subnet[edge[0]][edge[1]]['num_key']) - 1) if subnet[edge[0]][edge[1]]['num_key'] > 1 else 100_000_000
            routing_path = nx.shortest_path(subnet, self.source_node, self.target_node, 'weight')
            # total_weight = sum(subnet[routing_path[i]][routing_path[i + 1]]['weight'] for i in range(len(routing_path) - 1))
            # print(routing_path, total_weight)

        if self.metric_type == 'weighted_life_shortest':
            copied_G = copy.deepcopy(self.logi_G)
            subnet = nx.subgraph_view(
                copied_G,
                filter_edge=lambda node_1_id, node_2_id: \
                    True if copied_G.edges[(node_1_id, node_2_id)]['num_key'] >= self.consume_key_size else False
            )
            # Don't find the path
            if len(subnet.edges) == 0:
                self.no_path_count += 1
                # print("Don't find path: ", self.no_path_count, "({0}, {1})".format(self.source_node, self.target_node))
                return []
            if not nx.has_path(subnet, source=self.source_node, target=self.target_node):
                self.no_path_count += 1
                # print("Don't find path: ", self.no_path_count, "({0}, {1})".format(self.source_node, self.target_node))
                return []

            # routing_path = nx.shortest_path(subnet, 0, 5)
            self.calculate_based_lifetime_weight(subnet)

            routing_path = nx.shortest_path(subnet, self.source_node, self.target_node, 'weight')

        return routing_path

    def find_k_shortest_path(self):
        copied_G = copy.deepcopy(self.G)
        subnet = nx.subgraph_view(
            copied_G,
            filter_edge=lambda node_1_id, node_2_id: \
                True if copied_G.edges[(node_1_id, node_2_id)]['num_key'] >= self.consume_key_size else False
        )
        # subnet = nx.subgraph_view(
        #     copied_G,
        #     filter_edge=lambda node_1_id, node_2_id: \
        #         True if copied_G.edges[(node_1_id, node_2_id)]['num_key'] >= self.consume_key_size and
        #                 copied_G.edges[(node_1_id, node_2_id)]['num_channel'] > 0 else False
        # )
        paths = []
        if len(subnet.edges) == 0 or not nx.has_path(subnet, source=self.source_node, target=self.target_node):
            for _ in range(self.k):
                paths.append([])
            routing_path = paths
            return routing_path

        # routing_path = nx.shortest_path(subnet, 0, 5)
        for edge in subnet.edges:
            subnet[edge[0]][edge[1]]['weight'] = 1 / subnet[edge[0]][edge[1]]['num_key']
        # paths = list(nx.shortest_simple_paths(subnet, self.source_node, self.target_node, 'weight'))
        # paths = list(nx.all_shortest_paths(subnet, self.source_node, self.target_node, 'weight'))
        paths = list(nx.all_shortest_paths(subnet, self.source_node, self.target_node))

        if len(paths) < self.k:
            for _ in range(self.k - len(paths)):
                paths.append([])
        routing_path = paths[:self.k]

        return routing_path

    def logical_find_routing_path(self):
        accumulate_qber = []
        accumulate_num_key = []
        accumulate_count_rate = []
        loop_nodes = []
        routing_path = []
        routing_path.append(self.source_node)

        # Using Num_key
        # shortest_routing_path = self.temp_shrotest_path(self.source_node, self.target_node, 'weight')
        while self.source_node != self.target_node:
            neighbor_nodes = [node for node in self.logi_G.neighbors(self.source_node) if
                              self.logi_G[self.source_node][node]['num_key'] > 0 and
                              self.logi_G[self.source_node][node]['num_key'] >= self.consume_key_size]
            neighbor_nodes = [node for node in neighbor_nodes if node not in routing_path]  # check in routing path
            neighbor_nodes = [node for node in neighbor_nodes if node not in loop_nodes]  # check the loop

            if len(neighbor_nodes) == 0 and len(accumulate_count_rate) > 0:
                loop_nodes.append(self.source_node)
                routing_path.pop()
                accumulate_num_key.pop()
                accumulate_count_rate.pop()
                self.source_node = routing_path[-1]
                continue

            elif len(neighbor_nodes) == 0 and len(accumulate_count_rate) == 0:
                return []

            selected_node = self.select_next_node(neighbor_nodes, accumulate_qber, accumulate_num_key, accumulate_count_rate)
            routing_path.append(selected_node)
            self.source_node = selected_node

        # if len(shortest_routing_path) != 0 and len(shortest_routing_path) * 2 <= len(routing_path):
        #     routing_path = shortest_routing_path

        return routing_path

    def apply_routing_path(self, routing_path):
        for i in range(len(routing_path) - 1):
            sorted_key = tuple(sorted((routing_path[i], routing_path[i + 1])))
            self.logi_G[sorted_key[0]][sorted_key[1]]['num_key'] -= self.consume_key_size
            self.logi_key_pool[sorted_key] = self.logi_key_pool[sorted_key][self.consume_key_size:]
            if sorted_key in self.all_possible_edges:
                if sorted_key in self.G.edges():
                    self.proactive_key_consume += 1
                else:
                    self.n_hop_proactive_key_consume += 1
            if len(self.logi_key_pool[sorted_key]) != self.logi_G[sorted_key[0]][sorted_key[1]]['num_key']:
                print("!!!!!!!!!!!!!!!!!!!!!", sorted_key)
                print(len(self.logi_key_pool[sorted_key]), self.logi_G[sorted_key[0]][sorted_key[1]]['num_key'])

    def select_next_node(self, neighbor_nodes, accumulate_qber, accumulate_num_key, accumulate_count_rate):
        current_edges = list(self.G.edges(self.source_node))
        for edge in current_edges:
            self.G[edge[0]][edge[1]]['weight'] = self.calculate_weight(
                edge, accumulate_qber, accumulate_num_key, accumulate_count_rate,
                self.G[edge[0]][edge[1]]['qber'],
                self.G[edge[0]][edge[1]]['num_key'],
                self.G[edge[0]][edge[1]]['count_rate']
            )

        min_weight_neighbor = min(neighbor_nodes,
                                  key=lambda neighbor: self.G[self.source_node][neighbor].get('weight', float('inf'))
                                  )
        accumulate_qber.append(self.G[self.source_node][min_weight_neighbor]['qber'])
        accumulate_num_key.append(self.G[self.source_node][min_weight_neighbor]['num_key'])
        accumulate_count_rate.append(self.G[self.source_node][min_weight_neighbor]['count_rate'])

        return min_weight_neighbor

    def calculate_based_lifetime_weight(self, net):
        for edge in net.edges:
            sorted_key = tuple(sorted(edge))
            life_time_weight = []
            # for key_life in self.logi_key_pool[edge]:
            #     if key_life <= self.key_life_time * 0.1:
            #         life_time_weight.append(1000)
            #     elif key_life <= self.key_life_time * 0.5:
            #         life_time_weight.append(100)
            #     else:
            #         life_time_weight.append(1)
            life_time_weight.append(min(self.logi_key_pool[sorted_key]))
            if sum(life_time_weight) != 0:
                net[sorted_key[0]][sorted_key[1]]['weight'] = 1 / sum(life_time_weight)
                # net[edge[0]][edge[1]]['weight'] = (len(self.logi_key_pool[edge]) * 1) / sum(self.logi_key_pool[edge])
            elif sum(life_time_weight) == 0:
                net[sorted_key[0]][sorted_key[1]]['weight'] = 0.0

    def calculate_weight(self, edge, accumulate_qber, accumulate_num_key, accumulate_count_rate, current_qber, current_num_key, current_count_rate):
        weight = 0
        qber_weight = 0
        num_key_weight = 0
        numerator_sum = 0
        denominator_sum = 0

        if self.metric_type == 'qber':
            if len(accumulate_count_rate) == 0:
                qber_weight = (current_qber * current_count_rate) / (current_count_rate)
            else:
                for i in range(len(accumulate_qber)):
                    numerator_sum += accumulate_qber[i] * accumulate_count_rate[i]
                numerator_sum += current_qber * current_count_rate
                denominator_sum = sum(accumulate_count_rate) + current_count_rate
                qber_weight = numerator_sum / denominator_sum
            weight = qber_weight

        if self.metric_type == 'num_key':
            if current_num_key == 0:
                current_num_key = 10_000
            else:
                if edge[0] > edge[1]:
                    edge = (edge[1], edge[0])
                current_num_key = sum(self.cumulative_edge_keys[edge]) / len(self.cumulative_edge_keys[edge])
            if len(accumulate_count_rate) == 0:
                num_key_weight = 1 / current_num_key
            else:
                num_key_weight = 1 / current_num_key
                ######## Accumulate weight version ########
                # for i in range(len(accumulate_num_key)):
                #     denominator_sum += accumulate_num_key[i]
                # denominator_sum += current_num_key
                # numerator_sum = current_num_key
                # num_key_weight = numerator_sum / denominator_sum
            weight = num_key_weight

        return weight


if __name__ == "__main__":
    max_time_step = 10_000  # 1_000
    proactive = True
    proactive_type = 'n-hop' # '1-hop', 'n-hop'
    topology_type = 'NSFNET'
    env = QuantumEnvironment(max_time_step=max_time_step, topology_type=topology_type) # BUTTERFLY

    num_simulation = 5
    seed = [0, 5, 10, 15, 20]  # 42
    # seed = [0]
    action = []
    sp_delay, wsp_delay, lsp_delay = [], [], []
    # threshold_list = range(0, 21, 1)   # lifetime = 20
    # threshold_list = [80, 85, 90, 95, 100]
    threshold_list = [0, 20, 40, 60, 80, 85, 90, 95, 100]    # lifetime = 100

    print("Simulation information")
    print("The number of max time step: ", max_time_step)
    print("The number of simulation: ", num_simulation)
    print("Topology type: ", topology_type)
    print("Initial key lifetime: ", env.key_life_time)
    if proactive:
        print("Proactive Type: ", proactive_type)
        print("Request gen probability: ", env.dist_probability)
    print()

    metrics = [
        "average_provision", "average_session_blocking", "average_total_generation_keys",
        "average_remaining_keys", "average_used_keys", "average_expired_keys",
        "average_delay", "average_hops", "average_proactive_keys", "average_proactive_used_keys",
        "average_proactive_gen_keys", "average_proactive_expired_keys", "average_proactive_used_keys_for_n_hop",
        "average_n_hop_proactive_gen_keys", "average_n_hop_proactive_used_keys", "average_n_hop_proactive_expired_keys",
        "average_fairness", "average_overflow_keys", "average_key_pool_usage",
        "provision_mean", "provision_ci_min", "provision_ci_max", "provision_ci_half",
        "delay_mean", "delay_ci_min", "delay_ci_max", "delay_ci_half"
    ]

    shortest_path_info, weighted_shortest_path_info = [{k: [] for k in metrics} for _ in range(2)]
    shortest_path_delay, weighted_shortest_path_delay = {}, {}
    shortest_path_all_link_delay, weighted_shortest_path_all_link_delay = [], []

    for i in threshold_list:
        threshold = i

        weighted_shortest_reward, shortest_reward, qber_reward, num_key_reward, combination_reward = 0, 0, 0, 0, 0
        weighted_shortest_average_reward, shortest_average_reward, qber_average_reward, num_key_average_reward, combination_average_reward = 0, 0, 0, 0, 0
        weighted_shortest_average_session_blocking, shortest_average_session_blocking, qber_average_session_blocking, num_key_average_session_blocking, combination_average_session_blocking = 0, 0, 0, 0, 0
        weighted_shortest_average_total_generation_keys, shortest_average_total_generation_keys, qber_average_total_generation_keys, num_key_average_total_generation_keys, combination_average_total_generation_keys = 0, 0, 0, 0, 0
        weighted_shortest_average_remaining_keys, shortest_average_remaining_keys, qber_average_remaining_keys, num_key_average_remaining_keys, combination_average_remaining_keys = 0, 0, 0, 0, 0
        weighted_shortest_average_used_keys, shortest_average_used_keys, qber_average_used_keys, num_key_average_used_keys, combination_average_used_keys = 0, 0, 0, 0, 0
        weighted_shortest_average_expired_keys, shortest_average_expired_keys, qber_average_expired_keys, num_key_average_expired_keys, combination_average_expired_keys = 0, 0, 0, 0, 0
        weighted_shortest_average_delay, weighted_shortest_average_hops, shortest_average_delay, shortest_average_hops, qber_average_delay = 0, 0, 0, 0, 0
        weighted_shortest_average_proactive_keys, shortest_average_proactive_keys, qber_average_proactive_keys = 0, 0, 0
        weighted_shortest_average_proactive_used_keys, shortest_average_proactive_used_keys, qber_average_proactive_used_keys = 0, 0, 0
        weighted_shortest_average_proactive_gen_keys, shortest_average_proactive_gen_keys, qber_average_proactive_gen_keys = 0, 0, 0
        weighted_shortest_average_proactive_expired_keys, shortest_average_proactive_expired_keys, qber_average_proactive_expired_keys = 0, 0, 0
        weighted_shortest_average_proactive_used_keys_for_n_hop, shortest_average_proactive_used_keys_for_n_hop, qber_average_proactive_used_keys_for_n_hop = 0, 0, 0
        weighted_shortest_average_n_hop_proactive_used_keys, shortest_average_n_hop_proactive_used_keys, qber_average_n_hop_proactive_used_keys = 0, 0, 0
        weighted_shortest_average_n_hop_proactive_gen_keys, shortest_average_n_hop_proactive_gen_keys, qber_average_n_hop_proactive_gen_keys = 0, 0, 0
        weighted_shortest_average_n_hop_proactive_expired_keys, shortest_average_n_hop_proactive_expired_keys, qber_average_n_hop_proactive_expired_keys = 0, 0, 0
        weighted_shortest_average_fairness, weighted_shortest_average_key_pool_usage, weighted_shortest_average_key_overflow = 0, 0, 0,

        # Shortest path simulation
        # env.metric_type = 'simple_shortest'
        # env.plot_topology()
        # for i in range(num_simulation):
        #     env.reset(seed=seed[i], max_time_step=max_time_step, proactive=proactive, proactive_type=proactive_type,
        #               threshold=threshold)
            # for _ in range(max_time_step):
            #     _, shortest_reward, _, _, info = env.step(action)
            # shortest_average_reward += shortest_reward
            # shortest_average_session_blocking += info['session_blocking']
            # shortest_average_total_generation_keys += info['total_generation_keys']
            # shortest_average_remaining_keys += info['remaining_keys']
            # shortest_average_used_keys += info['used_keys']
            # shortest_average_expired_keys += info['expired_keys']
            # shortest_average_delay += info['delay']
            # shortest_average_hops += info['hops']
            # if proactive:
            #     shortest_proactive_keys_ratio = env.proactive_key_consume / env.proactive_key_generation if env.proactive_key_generation > 0 else 0
            #     shortest_average_proactive_keys += shortest_proactive_keys_ratio
            #     shortest_average_proactive_used_keys += env.proactive_key_consume
            #     shortest_average_proactive_gen_keys += env.proactive_key_generation
            #     shortest_average_proactive_expired_keys += env.proactive_key_expired
                # print("SP: ", env.proactive_key_generation, env.proactive_key_consume, shortest_proactive_keys_ratio * 100)

        #     shortest_path_all_link_delay.append({
        #         k: (sum(v['delays'])/len(v['delays']) if v['delays'] else 0)
        #         for k, v in env.all_link_delay.items()
        #     })
        #
        # rows = []
        # for (src, dst), requests in env.all_link_delay.items():
        #     for d in requests['delays']:
        #         rows.append([src, dst, d])
        # df = pd.DataFrame(rows, columns=['src', 'dst', 'delay'])
        # df.to_csv('delay_results/COST266_shortest_path_all_link_delay_03_n-hop_40.csv', index=False)
        #
        # shortest_path_all_link_average_delay = defaultdict(list)
        # for sm in shortest_path_all_link_delay:
        #     for k, v in sm.items():
        #         shortest_path_all_link_average_delay[k].append(v)
        #
        # shortest_path_all_link_average_delay = {k: sum(v) / len(v) for k, v in shortest_path_all_link_average_delay.items()}
        # with open("delay_results/COST266_shortest_path_all_link_average_delay_03_n-hop_40.csv", mode="w", newline="") as f:
        #     writer = csv.writer(f)
        #     writer.writerow(["source", "target", "generated", "success", "delays"])  # 헤더 작성
        #     for (src, dst), delays in shortest_path_all_link_average_delay.items():
        #         # delay 리스트를 문자열로 묶어서 저장
        #         writer.writerow([src, dst, env.all_link_delay[(src, dst)]['generated'], env.all_link_delay[(src, dst)]['success'], delays])

        # env.plot_topology()
        # env.plot_heatmap()
        # Weighted shortest path simulation
        env.metric_type = 'weighted_shortest'
        # --- 95% 신뢰구간용: 시드별 관측값 보관 ---
        wsp_reward_samples, wsp_delay_samples = [], []
        # env.plot_topology()
        for i in range(num_simulation):
            s, _ = env.reset(seed=seed[i], max_time_step=max_time_step, proactive=proactive,
                             proactive_type=proactive_type, threshold=threshold)
            for _ in range(max_time_step):
                _, weighted_shortest_reward, _, _, info = env.step(action)
            # --- 95% 신뢰구간용: 이 시드의 최종 관측값 저장 ---
            wsp_reward_samples.append(weighted_shortest_reward)
            wsp_delay_samples.append(info['delay'] / max_time_step)
            weighted_shortest_average_reward += weighted_shortest_reward
            weighted_shortest_average_session_blocking += info['session_blocking']
            weighted_shortest_average_total_generation_keys += info['total_generation_keys']
            weighted_shortest_average_remaining_keys += info['remaining_keys']
            weighted_shortest_average_used_keys += info['used_keys']
            weighted_shortest_average_expired_keys += info['expired_keys']
            weighted_shortest_average_delay += info['delay']
            weighted_shortest_average_hops += info['hops']
            weighted_shortest_average_fairness += info['request_fairness']
            weighted_shortest_average_key_pool_usage += info['average_key_pool_usage_percent']
            weighted_shortest_average_key_overflow += info['key_pool_overflow_count']
            if proactive:
                weighted_shortest_proactive_keys_ratio = env.proactive_key_consume / env.proactive_key_generation if env.proactive_key_generation > 0 else 0
                weighted_shortest_average_proactive_keys += weighted_shortest_proactive_keys_ratio
                weighted_shortest_average_proactive_used_keys += env.proactive_key_consume
                weighted_shortest_average_proactive_gen_keys += env.proactive_key_generation
                weighted_shortest_average_proactive_expired_keys += env.proactive_key_expired
                weighted_shortest_average_proactive_used_keys_for_n_hop += env.proactive_key_consume_for_n_hop
                weighted_shortest_average_n_hop_proactive_gen_keys += env.n_hop_proactive_key_generation
                weighted_shortest_average_n_hop_proactive_used_keys += env.n_hop_proactive_key_consume
                weighted_shortest_average_n_hop_proactive_expired_keys += env.n_hop_proactive_key_expired

                # print("WSP: ", env.proactive_key_generation, env.proactive_key_consume, weighted_shortest_proactive_keys_ratio * 100)

        #     weighted_shortest_path_all_link_delay.append({
        #         k: (sum(v['delays']) / len(v['delays']) if v['delays'] else 0)
        #         for k, v in env.all_link_delay.items()
        #     })
        #
        # rows = []
        # for (src, dst), requests in env.all_link_delay.items():
        #     for d in requests['delays']:
        #         rows.append([src, dst, d])
        # df = pd.DataFrame(rows, columns=['src', 'dst', 'delay'])
        # df.to_csv('delay_results/COST266_weighted_shortest_path_all_link_delay_03_n-hop_40.csv', index=False)
        #
        # weighted_shortest_path_all_link_average_delay = defaultdict(list)
        # for sm in weighted_shortest_path_all_link_delay:
        #     for k, v in sm.items():
        #         weighted_shortest_path_all_link_average_delay[k].append(v)
        #
        # weighted_shortest_path_all_link_average_delay = {k: sum(v) / len(v) for k, v in weighted_shortest_path_all_link_average_delay.items()}
        # with open("delay_results/COST266_weighted_shortest_path_all_link_average_delay_03_n-hop_40.csv", mode="w", newline="") as f:
        #     writer = csv.writer(f)
        #     writer.writerow(["source", "target", "generated", "success", "delays"])  # 헤더 작성
        #     for (src, dst), delays in weighted_shortest_path_all_link_average_delay.items():
        #         # delay 리스트를 문자열로 묶어서 저장
        #         writer.writerow([src, dst, env.all_link_delay[(src, dst)]['generated'], env.all_link_delay[(src, dst)]['success'], delays])

        # env.plot_topology()
        # env.plot_heatmap()
        # # QBER simulation
        # env.metric_type = 'weighted_life_shortest'
        # # env.plot_topology()
        # # env.plot_expand_topology()
        # for i in range(num_simulation):
        #     s, _ = env.reset(seed=seed[i], max_time_step=max_time_step, proactive=proactive, proactive_type=proactive_type, threshold=threshold)
        #     for _ in range(max_time_step):
        #         _, qber_reward, _, _, info = env.step(action)
        #     qber_average_reward += qber_reward
        #     qber_average_session_blocking += info['session_blocking']
        #     qber_average_total_generation_keys += info['total_generation_keys']
        #     qber_average_remaining_keys += info['remaining_keys']
        #     qber_average_used_keys += info['used_keys']
        #     qber_average_expired_keys += info['expired_keys']
        #     qber_average_delay += info['delay']
        #     if proactive:
        #         qber_proactive_keys_ratio = env.proactive_key_consume / env.proactive_key_generation if env.proactive_key_generation > 0 else 0
        #         qber_average_proactive_keys += qber_proactive_keys_ratio
        #         qber_average_proactive_used_keys += env.proactive_key_consume
        #         qber_average_proactive_gen_keys += env.proactive_key_generation
        #         # print("LSP: ", env.proactive_key_generation, env.proactive_key_consume, qber_proactive_keys_ratio * 100)

        # shortest_average_reward /= num_simulation
        # shortest_average_session_blocking /= num_simulation
        # shortest_average_total_generation_keys /= num_simulation
        # shortest_average_remaining_keys /= num_simulation
        # shortest_average_used_keys /= num_simulation
        # shortest_average_expired_keys /= num_simulation
        # shortest_average_delay /= num_simulation
        # shortest_average_hops /= num_simulation
        # shortest_average_proactive_keys /= num_simulation
        # shortest_average_proactive_used_keys /= num_simulation
        # shortest_average_proactive_gen_keys /= num_simulation
        # shortest_average_proactive_expired_keys /= num_simulation

        # ================= 95% 신뢰구간 =================
        ci_reward = confidence_interval(wsp_reward_samples, confidence=0.95)
        ci_delay = confidence_interval(wsp_delay_samples, confidence=0.95)

        print(f"--- [threshold={threshold}] weighted_shortest 95% 신뢰구간 ---")
        print_confidence_interval("average_reward", ci_reward)
        print_confidence_interval("average_delay", ci_delay, unit="ms")
        print(f"  시드별 reward: {[round(v, 4) for v in wsp_reward_samples]}")
        print(f"  시드별 delay : {[round(v, 4) for v in wsp_delay_samples]}")
        if ci_reward["n"] < 10:
            print(f"  [주의] n={ci_reward['n']}: 자유도가 작아 구간 폭 추정이 불안정합니다."
                  f" num_simulation >= 10 권장")
        print()
        # ===============================================

        weighted_shortest_average_reward /= num_simulation
        weighted_shortest_average_session_blocking /= num_simulation
        weighted_shortest_average_total_generation_keys /= num_simulation
        weighted_shortest_average_remaining_keys /= num_simulation
        weighted_shortest_average_used_keys /= num_simulation
        weighted_shortest_average_expired_keys /= num_simulation
        weighted_shortest_average_delay /= num_simulation
        weighted_shortest_average_hops /= num_simulation
        weighted_shortest_average_proactive_keys /= num_simulation
        weighted_shortest_average_proactive_used_keys /= num_simulation
        weighted_shortest_average_proactive_gen_keys /= num_simulation
        weighted_shortest_average_proactive_expired_keys /= num_simulation
        weighted_shortest_average_proactive_used_keys_for_n_hop /= num_simulation
        weighted_shortest_average_n_hop_proactive_gen_keys /= num_simulation
        weighted_shortest_average_n_hop_proactive_used_keys /= num_simulation
        weighted_shortest_average_n_hop_proactive_expired_keys /= num_simulation
        weighted_shortest_average_fairness /= num_simulation
        weighted_shortest_average_key_pool_usage /= num_simulation
        weighted_shortest_average_key_overflow /= num_simulation

        # qber_average_reward /= num_simulation
        # qber_average_session_blocking /= num_simulation
        # qber_average_total_generation_keys /= num_simulation
        # qber_average_remaining_keys /= num_simulation
        # qber_average_used_keys /= num_simulation
        # qber_average_expired_keys /= num_simulation
        # qber_average_delay /= num_simulation
        # qber_average_proactive_keys /= num_simulation
        # qber_average_proactive_used_keys /= num_simulation
        # qber_average_proactive_gen_keys /= num_simulation
        # qber_average_proactive_expired_keys /= num_simulation

        # Print the results in a tabular format

        if proactive:
            print("threshold 1: ", env.lifetime_threshold_1)
            print("threshold 4: ", env.lifetime_threshold_4)
        print()

        print("Average Results: ", threshold)
        print(f"{'Metric':<20}{'Success':<10}{'Session Blocking':<20}{'Total generation keys':<25}{'Used keys':<20}{'Expired keys':<20}{'Used percentage':<20}{'Average delay':<20}{'Average hops':<20}")
        # print(f"{'simple_shortest':<20}{shortest_average_reward:<10}{shortest_average_session_blocking:<20}{shortest_average_total_generation_keys:<25}{shortest_average_used_keys:<20}{shortest_average_expired_keys:<20}{(shortest_average_used_keys / shortest_average_total_generation_keys) * 100:<4.2f}%{' ':<15}{shortest_average_delay / max_time_step:<4.3f}ms{' ':<15}{shortest_average_hops / max_time_step:<4.2f}")
        print(f"{'weighted_shortest':<20}{weighted_shortest_average_reward:<10}{weighted_shortest_average_session_blocking:<20}{weighted_shortest_average_total_generation_keys:<25}{weighted_shortest_average_used_keys:<20}{weighted_shortest_average_expired_keys:<20}{(weighted_shortest_average_used_keys / weighted_shortest_average_total_generation_keys) * 100:<4.2f}%{' ':<15}{weighted_shortest_average_delay / max_time_step:<4.3f}ms{' ':<15}{weighted_shortest_average_hops / max_time_step:<4.2f}")
        # print(f"{'life_time_shortest':<20}{qber_average_reward:<10}{qber_average_session_blocking:<20}{qber_average_total_generation_keys:<25}{qber_average_used_keys:<20}{qber_average_expired_keys:<20}{(qber_average_used_keys/qber_average_total_generation_keys) * 100:<4.2f}%{' ':<15}{qber_average_delay/max_time_step:<4.3f}ms")
        print(f"{'Average key overflow : ':<30}{(weighted_shortest_average_key_overflow):<10}")
        print(f"{'Average key pool usage : ':<30}{(weighted_shortest_average_key_pool_usage):<10}")
        print(f"{'Average proactive keys probability: ':<30}{(shortest_average_proactive_keys) * 100:<4.2f}%{' ':<10}{(weighted_shortest_average_proactive_keys) * 100:<4.2f}%{' ':<10}{(qber_average_proactive_keys) * 100:<4.2f}%{' ':<10}")
        print(f"{'Average proactive keys : ':<30}{(shortest_average_proactive_used_keys)}/{(shortest_average_proactive_gen_keys):<10}{(weighted_shortest_average_proactive_used_keys)}/{(weighted_shortest_average_proactive_gen_keys):<10}{(qber_average_proactive_used_keys)}/{(qber_average_proactive_gen_keys):<10}")
        print(f"{'Average proactive keys expired : ':<30}{(weighted_shortest_average_proactive_expired_keys):<10}")
        print(f"{'Average proactive keys used for n_hop : ':<30}{(weighted_shortest_average_proactive_used_keys_for_n_hop):<10}")
        print(f"{'Average n_hop proactive keys generation : ':<30}{(weighted_shortest_average_n_hop_proactive_gen_keys):<10}")
        print(f"{'Average n_hop proactive keys used : ':<30}{(weighted_shortest_average_n_hop_proactive_used_keys):<10}")
        print(f"{'Average n_hop proactive keys expired : ':<30}{(weighted_shortest_average_n_hop_proactive_expired_keys):<10}")
        print(f"{'Average request fairness : ':<30}{(weighted_shortest_average_fairness):<10}")
        print()
        # print(f"{'Num keys':<20}{num_key_average_reward:<10}{num_key_average_session_blocking:<20}{num_key_average_total_generation_keys:<25}{num_key_average_used_keys:<20}{(num_key_average_used_keys/num_key_average_total_generation_keys) * 100:<4.2f}%")
        # print(f"{'QBER + Num keys':<20}{combination_average_reward:<10}{combination_average_session_blocking:<20}{combination_average_total_generation_keys:<25}{combination_average_used_keys:<20}{(combination_average_used_keys/combination_average_total_generation_keys) * 100:<4.2f}%")

        # shortest_path_info['average_reward'].append(shortest_average_reward)
        # shortest_path_info['average_session_blocking'].append(shortest_average_session_blocking)
        # shortest_path_info['average_total_generation_keys'].append(shortest_average_total_generation_keys)
        # shortest_path_info['average_remaining_keys'].append(shortest_average_remaining_keys)
        # shortest_path_info['average_used_keys'].append(shortest_average_expired_keys)
        # shortest_path_info['average_expired_keys'].append(shortest_average_expired_keys)
        # shortest_path_info['average_delay'].append(shortest_average_delay / max_time_step)
        # shortest_path_info['average_hops'].append(shortest_average_hops / max_time_step)
        # if proactive:
        #     shortest_path_info['average_proactive_keys'].append(shortest_average_proactive_keys)
        #     shortest_path_info['average_proactive_used_keys'].append(shortest_average_proactive_used_keys)
        #     shortest_path_info['average_proactive_gen_keys'].append(shortest_average_proactive_gen_keys)
        #     shortest_path_info['average_proactive_expired_keys'].append(shortest_average_proactive_expired_keys)

        weighted_shortest_path_info['average_provision'].append(weighted_shortest_average_reward)
        weighted_shortest_path_info['average_session_blocking'].append(weighted_shortest_average_session_blocking)
        weighted_shortest_path_info['average_total_generation_keys'].append(weighted_shortest_average_total_generation_keys)
        weighted_shortest_path_info['average_remaining_keys'].append(weighted_shortest_average_remaining_keys)
        weighted_shortest_path_info['average_used_keys'].append(weighted_shortest_average_used_keys)
        weighted_shortest_path_info['average_expired_keys'].append(weighted_shortest_average_expired_keys)
        weighted_shortest_path_info['average_delay'].append(weighted_shortest_average_delay / max_time_step)
        weighted_shortest_path_info['average_hops'].append(weighted_shortest_average_hops / max_time_step)
        weighted_shortest_path_info['average_fairness'].append(weighted_shortest_average_fairness)
        weighted_shortest_path_info['average_overflow_keys'].append(weighted_shortest_average_key_overflow)
        weighted_shortest_path_info['average_key_pool_usage'].append(weighted_shortest_average_key_pool_usage)

        # --- 95% 신뢰구간 결과 저장 ---
        weighted_shortest_path_info['provision_mean'].append(ci_reward['mean'])
        weighted_shortest_path_info['provision_ci_min'].append(ci_reward['lower'])
        weighted_shortest_path_info['provision_ci_max'].append(ci_reward['upper'])
        weighted_shortest_path_info['provision_ci_half'].append(ci_reward['half'])
        weighted_shortest_path_info['delay_mean'].append(ci_delay['mean'])
        weighted_shortest_path_info['delay_ci_min'].append(ci_delay['lower'])
        weighted_shortest_path_info['delay_ci_max'].append(ci_delay['upper'])
        weighted_shortest_path_info['delay_ci_half'].append(ci_delay['half'])
        if proactive:
            weighted_shortest_path_info['average_proactive_keys'].append(weighted_shortest_average_proactive_keys)
            weighted_shortest_path_info['average_proactive_used_keys'].append(weighted_shortest_average_proactive_used_keys)
            weighted_shortest_path_info['average_proactive_gen_keys'].append(weighted_shortest_average_proactive_gen_keys)
            weighted_shortest_path_info['average_proactive_expired_keys'].append(weighted_shortest_average_proactive_expired_keys)
            weighted_shortest_path_info['average_proactive_used_keys_for_n_hop'].append(weighted_shortest_average_proactive_used_keys_for_n_hop)
            weighted_shortest_path_info['average_n_hop_proactive_gen_keys'].append(weighted_shortest_average_n_hop_proactive_gen_keys)
            weighted_shortest_path_info['average_n_hop_proactive_used_keys'].append(weighted_shortest_average_n_hop_proactive_used_keys)
            weighted_shortest_path_info['average_n_hop_proactive_expired_keys'].append(weighted_shortest_average_n_hop_proactive_expired_keys)

    # logging
    # csv_file_path_1 = 'results/NSFNET_shortest_path_results_03_1-hop_10.csv'
    csv_file_path_2 = 'results/10_000/NSFNET_results_01_n-hop.csv'

    field_names = shortest_path_info.keys()
    # with open(csv_file_path_1, 'w', newline='', encoding='utf-8') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(field_names)
    #
    #     max_len = max(len(v) for v in shortest_path_info.values())
    #     for i in range(max_len):
    #         row = [shortest_path_info[key][i] if i < len(shortest_path_info[key]) else '' for key in field_names]
    #         writer.writerow(row)

    with open(csv_file_path_2, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)

        max_len = max(len(v) for v in weighted_shortest_path_info.values())
        for i in range(max_len):
            row = [weighted_shortest_path_info[key][i] if i < len(weighted_shortest_path_info[key]) else '' for key in field_names]
            writer.writerow(row)
