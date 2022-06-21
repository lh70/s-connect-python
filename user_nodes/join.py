from lh_lib.user_node_types import DualInputSingleOutputUserNode


class Join(DualInputSingleOutputUserNode):

    def __init__(self, in0, in1, out0, eval_str='x + y'):
        super().__init__(in0, in1, out0)
        self.code = compile(eval_str, '<string>', 'eval')
        self.latest_x = None
        self.latest_y = None

    def run(self):
        length = len(self.in0) if len(self.in0) > len(self.in1) else len(self.in1)
        for i in range(length):
            x = self.in0[i] if i < len(self.in0) else self.latest_x
            y = self.in1[i] if i < len(self.in1) else self.latest_y

            if x is not None and y is not None:
                self.out0.append(eval(self.code, {}, {'x': x, 'y': y}))

            self.latest_x = x
            self.latest_y = y

        self.in0.clear()
        self.in1.clear()
