from lh_lib.user_node_types import SingleInputSingleOutputUserNode


class PassThrough(SingleInputSingleOutputUserNode):

    def run(self):
        self.out0 += self.in0
        self.in0.clear()
