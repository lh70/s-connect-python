from lh_lib.user_node_types import SingleInputDualOutputUserNode


class Duplicate(SingleInputDualOutputUserNode):

    def run(self):
        for val in self.in0:
            self.out0.append(val)
            self.out1.append(val)
        self.in0.clear()
