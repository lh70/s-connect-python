from machine import Pin
from utime import ticks_ms, ticks_diff

from sensors.sensor import AbstractSensor


class CO2(AbstractSensor):

    communication_name = 'co2'

    """
    Initialises a the 5000ppm CO2 sensor MH-Z19B to retrieve its values via the pwm output interrupt driven.

    pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    """
    def __init__(self, pin):
        super().__init__()
        self.pin = Pin(pin)

        self.high_pulse_1 = 0
        self.low_pulse_1 = 0
        self.high_pulse_2 = 0
        self.low_pulse_2 = 0
        self.take_1 = True

        self.last_interrupt_time = ticks_ms()
        self.pin.irq(handler=self._interrupt, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, hard=True)

    """
    overwrites the standard get method, because we use custom asynchronously updated data.
    
    returns a valid pair of pulse durations as an integer tuple: (high_pulse, low_pulse)
    """
    def get(self):
        # if the first pair is valid return it
        if self.take_1:
            return self.high_pulse_1, self.low_pulse_1
        else:
            return self.high_pulse_2, self.low_pulse_2

    """
    NOP because we use interrupts to update this sensors data
    """
    def update(self):
        pass

    """
    interrupt handler which sets the pulse durations
    """
    def _interrupt(self):
        # determine the time duration since last interrupt
        duration = ticks_diff(ticks_ms(), self.last_interrupt_time)
        # on the rising edge set the low pulse duration
        if self.pin.value():
            # if first pair is currently valid write the second
            if self.take_1:
                self.low_pulse_2 = duration
            else:
                self.low_pulse_1 = duration
            # one high + low pulse duration pair are valid together, so switch output to the new valid pair
            self.take_1 = not self.take_1
        # on the falling edge set the high pulse duration
        else:
            # if first pair is currently valid write the second
            if self.take_1:
                self.high_pulse_2 = duration
            else:
                self.high_pulse_1 = duration
        # reset the time since last interrupt
        self.last_interrupt_time = ticks_ms()

    """
    utility function for later use which converts the pulse lengths into a co2 concentration in ppm
    """
    def _pulses_to_concentration(self, high_pulse, low_pulse):
        return (5000 * (high_pulse - 2000)) / (high_pulse + low_pulse - 4000)

