from lh_lib.user_node_types import SingleInputSingleOutputUserNode


class ButtonToSingleEmit(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0):
        super().__init__(in0, out0)
        self.emitted_state = None

    def run(self):
        for is_pressed in self.in0:
            if self.emitted_state is None:
                self.out0.append(is_pressed)
                self.emitted_state = is_pressed
            elif is_pressed != self.emitted_state:
                self.out0.append(is_pressed)
                self.emitted_state = is_pressed

        self.in0.clear()
