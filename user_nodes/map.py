from lh_lib.user_node_types import SingleInputSingleOutputUserNode


class Map(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0, eval_str='x'):
        super().__init__(in0, out0)
        self.code = compile(eval_str, '<string>', 'eval')

    def run(self):
        for x in self.in0:
            self.out0.append(eval(self.code, {}, {'x': x}))
        self.in0.clear()
