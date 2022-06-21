import os

from lh_lib.user_node_types import SingleInputNoOutputUserNode
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.logging import DataLogger


class ThroughputObserver(SingleInputNoOutputUserNode):

    def __init__(self, in0, filepath=False):
        super().__init__(in0)
        self.filepath = filepath
        self.time = ticks_ms()
        self.sum = 0

        if filepath:
            self.file = DataLogger(filepath)

    def run(self):
        self.sum += len(self.in0)
        self.in0.clear()

        if ticks_ms_diff_to_current(self.time) >= 1000:
            self.time = ticks_ms()

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'Throughput Observer\n\ncurrent throughput: {self.sum} values/second')

            if self.filepath:
                self.file.add(self.sum)

            self.sum = 0
