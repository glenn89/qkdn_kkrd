import pickle

import numpy as np
import topology_conf


class Request:
    def __init__(self, max_time_step, topology_conf, dist_probability):
        self.discard_time = 0
        self.ID = 0

        self.rng = np.random.default_rng()
        self.requests = self.make_requests_for_all_steps(T=max_time_step,
                                                         N=topology_conf['NUM_QKD_NODE'],
                                                         p=dist_probability)
    def make_requests_for_all_steps(self, T, N, p):
        reqs_by_t = []
        iu, ju = np.triu_indices(N, k=1)  # 무방향 예시
        for _ in range(T):
            keep = self.rng.binomial(1, p, size=iu.shape[0]).astype(bool)
            reqs_by_t.append(np.column_stack([iu[keep], ju[keep]]))
        return reqs_by_t

    def save_requests(self, filename="requests/NSFNET_1000_requests_01.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.requests, f)

    def load_requests(self, filename="requests/NSFNET_1000_requests_05.pkl"):
        with open(filename, "rb") as f:
            self.requests = pickle.load(f)

if __name__ == "__main__":
    req = Request(1, topology_conf.nsfnet_topo, 0.3)
    req.load_requests()
    print(len(req.requests[0]))
    print(req.requests)
    count = 0
    for r in req.requests:
        for _ in r:
            count += 1
    print(count)
