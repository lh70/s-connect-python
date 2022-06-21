from lh_lib.user_node_types import SingleInputSingleOutputUserNode


class Filter(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0, eval_str='x > 0'):
        super().__init__(in0, out0)
        self.code = compile(eval_str, '<string>', 'eval')

    def run(self):
        for x in self.in0:
            if eval(self.code, {}, {'x': x}):
                self.out0.append(x)
        self.in0.clear()
