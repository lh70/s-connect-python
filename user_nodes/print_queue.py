from lh_lib.user_node_types import SingleInputNoOutputUserNode
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


class PrintQueue(SingleInputNoOutputUserNode):

    def __init__(self, in0, format_str='{}', time_frame=0):
        super().__init__(in0)
        self.format_str = format_str
        self.time_frame = time_frame
        self.last_time_frame = ticks_ms()

    def run(self):
        if self.time_frame == 0 and self.in0:
            print(self.format_str.format(self.in0))
            self.in0.clear()
        elif self.time_frame != 0 and ticks_ms_diff_to_current(self.last_time_frame) >= self.time_frame:
            print(self.format_str.format(self.in0))
            self.in0.clear()
            self.last_time_frame = ticks_ms()
