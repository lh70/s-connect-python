from lh_lib.user_node_types import SingleInputSingleOutputUserNode
from lh_lib.base.time import ticks_ms, ticks_ms_diff_to_current


class Mean(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0, time_frame=0):
        super().__init__(in0, out0)
        self.time_frame = time_frame
        self.sum = 0
        self.size = 0
        self.last_time_frame = ticks_ms()

    def run(self):
        if self.time_frame == 0:
            for val in self.in0:
                self.sum += val
                self.size += 1
                self.out0.append(self.sum / float(self.size))
        else:
            for val in self.in0:
                self.sum += val
            self.size += len(self.in0)

            if ticks_ms_diff_to_current(self.last_time_frame) >= self.time_frame:
                self.out0.append(self.sum / float(self.size))
                self.sum = 0
                self.size = 0
                self.last_time_frame = ticks_ms()

        self.in0.clear()
