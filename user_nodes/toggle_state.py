from lh_lib.user_node_types import SingleInputSingleOutputUserNode


class ToggleState(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0, eval_str='x > 0', initial_state=False):
        super().__init__(in0, out0)
        self.code = compile(eval_str, '<string>', 'eval')
        self.output_state = initial_state

    def run(self):
        for x in self.in0:
            if eval(self.code, {}, {'x': x}):
                self.output_state = not self.output_state

            self.out0.append(self.output_state)

        self.in0.clear()
