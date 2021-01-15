import pickle


class RoutingPacket:
    def __init__(self, src_router: int, dest_router: int, min_cost: list):
        self.src_router = src_router
        self.dest_router = dest_router
        self.min_cost = min_cost

    def encode(self):
        return pickle.dumps(self)
