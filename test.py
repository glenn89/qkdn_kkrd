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
        print("src: ", iu, "dst: ", ju)
        for _ in range(T):
            keep = self.rng.binomial(1, p, size=iu.shape[0]).astype(bool)
            reqs_by_t.append(np.column_stack([iu[keep], ju[keep]]))
        return reqs_by_t

if __name__ == "__main__":
    req = Request(1, topology_conf.nsfnet_topo, 0.3)
    print(req.requests)
