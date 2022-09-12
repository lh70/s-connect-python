from lh_lib.user_node_types import SingleInputSingleOutputUserNode


class Throttle(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0):
        super().__init__(in0, out0)
        self.last_value = None

    def run(self):
        for val in self.in0:
            if val != self.last_value:
                self.out0.append(val)
                self.last_value = val

        self.in0.clear()
