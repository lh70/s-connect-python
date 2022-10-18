from lh_lib.user_node_types import SingleInputSingleOutputUserNode
from lh_lib.base.time import ticks_ms, ticks_ms_diff_to_current


class Throughput(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0):
        super().__init__(in0, out0)
        self.time = ticks_ms()
        self.sum = 0

    def run(self):
        self.sum += len(self.in0)
        self.in0.clear()

        if ticks_ms_diff_to_current(self.time) >= 1000:
            self.time = ticks_ms()

            self.out0.append(self.sum)

            self.sum = 0
