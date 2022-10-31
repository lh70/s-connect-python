import os

from lh_lib.user_node_types import SingleInputNoOutputUserNode


class MonitorLatest(SingleInputNoOutputUserNode):

    def run(self):
        if len(self.in0) > 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('MonitorLatest\n\nvalue: {}'.format(self.in0[-1]))

        self.in0.clear()
