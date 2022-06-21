import os

from lh_lib.user_node_types import DualInputNoOutputUserNode
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.logging import DataLogger


class CaseStudyDelayObserver(DualInputNoOutputUserNode):

    def __init__(self, in0, in1, filepath=False):
        super().__init__(in0, in1)
        self.filepath = filepath
        self.last_in0 = False
        self.last_in1 = False
        self.queue = []
        self.time_delays = []

        if filepath:
            self.file = DataLogger(filepath)

    def run(self):
        for i in self.in0:
            if i and not self.last_in0:  # on rising edge <==> False->True <==> button pressed
                if len(self.queue) == 0 or ticks_ms_diff_to_current(self.queue[-1]) > 10:
                    self.queue.append(ticks_ms())
            self.last_in0 = i

        for i in self.in1:
            if i != self.last_in1:  # on flipped state <==> True->False or False->True
                if len(self.queue) > 0:
                    # new approach. delay is < 2 seconds, so only one item should be in list, every other item is flickering, so take the first and delete the others
                    self.time_delays.append(ticks_ms_diff_to_current(self.queue[0]))
                    self.queue.clear()
            self.last_in1 = i

        if len(self.time_delays) > 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'Case Study Delay Observer\n\ntime delay: {self.time_delays}, queue: {self.queue}')

            if self.filepath:
                for delay in self.time_delays:
                    self.file.add(delay)

            self.time_delays.clear()

        self.in0.clear()
        self.in1.clear()
