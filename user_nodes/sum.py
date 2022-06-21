from lh_lib.user_node_types import SingleInputSingleOutputUserNode
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


class Sum(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0, time_frame=0):
        super().__init__(in0, out0)
        self.time_frame = time_frame
        self.last_time_frame = 0
        self.sum = 0

    def run(self):
        if self.time_frame == 0:
            for val in self.in0:
                self.sum += val
                self.out0.append(self.sum)
        else:
            for val in self.in0:
                self.sum += val

            if ticks_ms_diff_to_current(self.last_time_frame) >= self.time_frame:
                self.out0.append(self.sum)
                self.last_time_frame = ticks_ms()
                self.sum = 0

        self.in0.clear()
