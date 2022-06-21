import os

from lh_lib.user_node_types import SingleInputNoOutputUserNode
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


class Monitor(SingleInputNoOutputUserNode):

    def __init__(self, in0, time_frame=100):
        super().__init__(in0)
        self.time_frame = time_frame
        self.time = ticks_ms()
        self.values = []

    def run(self):
        self.values += self.in0
        self.in0.clear()

        if ticks_ms_diff_to_current(self.time) >= self.time_frame:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'Monitor\n\ntimeframe: {self.time_frame}ms\nvalues: {self.values}')
            self.time = ticks_ms()
            self.values = []
