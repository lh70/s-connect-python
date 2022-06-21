from lh_lib.user_node_types import SingleInputSingleOutputUserNode


class ButtonFilter(SingleInputSingleOutputUserNode):

    def __init__(self, in0, out0, flip_threshold=5, initial_state=False):
        super().__init__(in0, out0)
        self.flip_threshold = flip_threshold
        self.pressed = initial_state
        self.pressed_count = 0
        self.out_state = initial_state

    def run(self):
        for is_pressed in self.in0:
            if is_pressed == self.pressed:
                self.pressed_count += 1
            else:
                self.pressed = is_pressed
                self.pressed_count = 0

            if self.pressed_count > self.flip_threshold:
                self.out_state = self.pressed

            self.out0.append(self.out_state)

        self.in0.clear()

