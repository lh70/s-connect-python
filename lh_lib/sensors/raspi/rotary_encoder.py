from gpiozero import RotaryEncoder as GPIOZERORotaryEncoder

from lh_lib.sensors.sensor import AbstractSensor


class RotaryEncoder(AbstractSensor):
    """
    Reads an incremental rotary encoder.
    The callback functions look bulky, but they take the last state and reachable states in account to reduce jitter.

    clk_pin:integer, dt_pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                                    it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash

    scale:float can be any float or integer.
                Default is 0.5 -> 2 steps per resting state -> states between resting states are also valid states
                0.25 would also be reasonable -> 1 step per resting state
    """

    def __init__(self, clk_pin=17, dt_pin=27):
        super().__init__()
        self.sensor = GPIOZERORotaryEncoder(clk_pin, dt_pin)

    """
    updates the readout value according to scale. Cuts value to integer, because we want to output whole ticks.
    """

    def update(self):
        self.value = self.sensor.steps


