from gpiozero import InputDevice
from gpiozero import RotaryEncoder as GPIOZERORotaryEncoder

from lh_lib.sensors.sensor import AbstractSensor


class RotaryEncoder(AbstractSensor):
    """
    Reads an incremental rotary encoder.
    The callback functions look bulky, but they take the last state and reachable states in account to reduce jitter.

    clk_pin:integer, dt_pin:integer should be one of: (GPIO) 5, 6, 16, 17, 22, 23, 24, 25, 26, 27
        further information about the GPIO: https://pinout.xyz

    scale:float can be any float or integer.
                Default is 0.5 -> 2 steps per resting state -> states between resting states are also valid states
                0.25 would also be reasonable -> 1 step per resting state
    """
    def __init__(self, clk_pin=17, dt_pin=27, scale=0.5, use_gpio_implementation=False):
        super().__init__()

        self.use_gpio_implementation = use_gpio_implementation

        if self.use_gpio_implementation:
            self.sensor = GPIOZERORotaryEncoder(clk_pin, dt_pin)
        else:
            self.clk_pin = InputDevice(pin=clk_pin)
            self.dt_pin = InputDevice(pin=dt_pin)
            self.scale = scale
            self._pos = 0

            self.val_old_clk_pin = self.clk_pin.value
            self.val_old_dt_pin = self.dt_pin.value

            # default is to listen for both edge kinds
            self.clk_pin.pin.when_changed = self.clk_callback
            self.dt_pin.pin.when_changed = self.dt_callback

    def __del__(self):
        if not self.use_gpio_implementation:
            self.clk_pin.pin.when_changed = None
            self.dt_pin.pin.when_changed = None

    """
    updates the readout value according to scale. Cuts value to integer, because we want to output whole ticks.
    """
    def update(self):
        if self.use_gpio_implementation:
            self.value = self.sensor.steps
        else:
            self.value = int(self._pos * self.scale)

    """
    callback for clk pin, which only updates valid steps for the clk pin.

    this means:
        one step is only done once
        only steps which are reachable from the last step will happen
        only steps which are reachable from this pin changing state will happen

    this removes nearly all jitter.
    """
    def clk_callback(self, ticks, state):
        clk_val = state
        dt_val = self.dt_pin.value

        if self.val_old_clk_pin:
            if self.val_old_dt_pin:

                if not clk_val:
                    if dt_val:
                        self._pos += 1  # TT -> FT
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
            else:

                if not clk_val:
                    if not dt_val:
                        self._pos -= 1  # FF <- TF
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val

        else:
            if self.val_old_dt_pin:

                if clk_val:
                    if dt_val:
                        self._pos -= 1  # TT <- FT
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
            else:

                if clk_val:
                    if not dt_val:
                        self._pos += 1  # FF -> TF
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val

    """
    callback for dt pin, which only updates valid steps for the dt pin.

    this means:
        one step is only done once
        only steps which are reachable from the last step will happen
        only steps which are reachable from this pin changing state will happen

    this removes nearly all jitter.
    """

    def dt_callback(self, ticks, state):
        clk_val = self.clk_pin.value
        dt_val = state

        if self.val_old_clk_pin:
            if self.val_old_dt_pin:

                if clk_val:
                    if not dt_val:
                        self._pos -= 1  # TF <- TT
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
            else:

                if clk_val:
                    if dt_val:
                        self._pos += 1  # TF -> TT
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val

        else:
            if self.val_old_dt_pin:

                if not clk_val:
                    if not dt_val:
                        self._pos += 1  # FT -> FF
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
            else:

                if not clk_val:
                    if dt_val:
                        self._pos -= 1  # FT <- FF
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val