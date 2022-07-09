from lh_lib.user_node_types import SingleInputNoOutputUserNode
from lh_lib.constants import RUNNING_MICROPYTHON

if RUNNING_MICROPYTHON:
    from lh_lib.peripherals.displays import SSD1306


class Display(SingleInputNoOutputUserNode):

    def __init__(self, in0, format_str='{}'):
        super().__init__(in0)
        self.format_str = format_str
        self.display = SSD1306()

    def run(self):
        for x in self.in0:
            self.display.fill(0)
            self.display.text(self.format_str.format(x), 0, 0, 1)
            self.display.show()
        self.in0.clear()
