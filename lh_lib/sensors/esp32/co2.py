from machine import Pin
from utime import ticks_us, ticks_diff

from lh_lib.sensors.sensor import AbstractSensor


class CO2(AbstractSensor):

    communication_name = 'co2'

    """
    Initialises a the 5000ppm CO2 sensor MH-Z19B to retrieve its values via the pwm output interrupt driven.

    pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    """
    def __init__(self, pin):
        super().__init__()
        self.pin = Pin(pin, Pin.IN)

        self.high_pulse = 0
        self.low_pulse = 0
        self.pulses_changed = False

        self.last_interrupt_time = ticks_us()
        self.pin.irq(handler=self._interrupt, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

    """
    NOP because we use interrupts to update this sensors data
    """
    def update(self):
        if self.pulses_changed:
            self.value = self.high_pulse, self.low_pulse
            self.pulses_changed = False
        else:
            self.value = None

    """
    interrupt handler which sets the pulse durations
    """
    def _interrupt(self, pin):
        # determine the time duration since last interrupt
        duration = ticks_diff(ticks_us(), self.last_interrupt_time)
        # on the rising edge set the low pulse duration
        if pin.value():
            self.low_pulse = duration
            # one high + low pulse duration pair are valid together, so switch output to the new valid pair
            self.pulses_changed = True
        # on the falling edge set the high pulse duration
        else:
            self.high_pulse = duration
        # reset the time since last interrupt
        self.last_interrupt_time = ticks_us()

    """
    utility function for later use which converts the pulse lengths into a co2 concentration in ppm
    """
    def _pulses_to_concentration(self, high_pulse, low_pulse):
        return (5000 * (high_pulse - 2000)) / (high_pulse + low_pulse - 4000)

