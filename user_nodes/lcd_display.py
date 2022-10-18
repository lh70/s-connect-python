from lh_lib.user_node_types import SingleInputNoOutputUserNode
from lh_lib.base.constants import RUNNING_MICROPYTHON
from lh_lib.base.time import ticks_ms, ticks_ms_diff_to_current

if RUNNING_MICROPYTHON:
    from machine import Pin
    from lh_lib.peripherals.esp32.displays import ESP32GpioLcd


class LCDDisplay(SingleInputNoOutputUserNode):

    def __init__(self, in0, print_before_str='', format_str='{}', rate_limit_ms=500,  rs_pin=32, enable_pin=33, d4_pin=25, d5_pin=26, d6_pin=27, d7_pin=14):
        super().__init__(in0)
        self.format_str = format_str
        self.display = ESP32GpioLcd(rs_pin=Pin(rs_pin, mode=Pin.OUT), enable_pin=Pin(enable_pin), d4_pin=Pin(d4_pin), d5_pin=Pin(d5_pin), d6_pin=Pin(d6_pin), d7_pin=Pin(d7_pin))
        self.display.clear()
        self.display.putstr(print_before_str)

        self.start_pos = len(print_before_str)
        self.rate_limit_ms = rate_limit_ms
        self.last_display_update = ticks_ms() - rate_limit_ms

    def run(self):
        for x in self.in0:
            if ticks_ms_diff_to_current(self.last_display_update) > self.rate_limit_ms:
                output_str = self.format_str.format(x)

                self.display.move_to(self.start_pos, 0)
                self.display.putstr(' ' * len(output_str))
                self.display.move_to(self.start_pos, 0)
                self.display.putstr(output_str)

                self.last_display_update = ticks_ms()
        self.in0.clear()
