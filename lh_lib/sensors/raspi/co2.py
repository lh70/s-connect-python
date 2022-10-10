from gpiozero import InputDevice
from lh_lib.time import ticks_us, ticks_us_diff_to_current

from lh_lib.sensors.sensor import AbstractSensor

MIN_PULSE_DURATION_US = 2000


class CO2(AbstractSensor):

    """
    Initialises a the 5000ppm CO2 sensor MH-Z19B to retrieve its values via the pwm output interrupt driven.

    pin:integer should be one of: (GPIO) 5, 6, 16, 17, 22, 23, 24, 25, 26, 27
        further information about the GPIO: https://pinout.xyz
    """
    def __init__(self, pin=17):
        self.input_device = InputDevice(pin=pin)
        super().__init__()

        self.high_pulse = 0
        self.low_pulse = 0
        self.pulses_changed = False
        self.irq_fresh_start = True

        self.last_interrupt_time = ticks_us()

        # default is to listen for both edge kinds
        self.input_device.pin.when_changed = self._interrupt

    def __del__(self):
        self.input_device.pin.when_changed = None

    """
    if new pulse values available sets the sensors value to the set(high_pulse, low_pulse, computed_concentration)
    else sets value to None, which represents an invalid sensor value that will be ignored.
    """
    def update(self):
        if self.pulses_changed:
            if self.high_pulse >= MIN_PULSE_DURATION_US and self.low_pulse >= MIN_PULSE_DURATION_US:
                self.value = self.high_pulse, self.low_pulse, self._pulses_to_concentration(self.high_pulse, self.low_pulse)
            self.pulses_changed = False
        else:
            self.value = None

    """
    interrupt handler which sets the pulse durations
    """
    def _interrupt(self, ticks, state):
        # determine the time duration since last interrupt
        duration = ticks_us_diff_to_current(self.last_interrupt_time)
        # on the rising edge set the low pulse duration
        if state:
            self.low_pulse = duration
            # one high + low pulse duration pair are valid together, so switch output to the new valid pair
            # ignore second measurement if there is no valid first measurement
            if not self.irq_fresh_start:
                self.pulses_changed = True
        # on the falling edge set the high pulse duration
        else:
            self.high_pulse = duration
            # set true to indicate a valid first measurement
            if self.irq_fresh_start:
                self.irq_fresh_start = False
        # reset the time since last interrupt
        self.last_interrupt_time = ticks_us()

    """
    utility function for later use which converts the pulse lengths into a co2 concentration in ppm
    """
    def _pulses_to_concentration(self, high_pulse, low_pulse):
        return (5000 * (high_pulse - 2000)) / (high_pulse + low_pulse - 4000)

