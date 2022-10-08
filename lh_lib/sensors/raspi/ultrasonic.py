from lh_lib.time import sleep_us, ticks_us, ticks_us_diff_to_current
from gpiozero import InputDevice, OutputDevice

from lh_lib.sensors.sensor import AbstractSensor


class Ultrasonic(AbstractSensor):

    """
    Initialises an ultrasonic sensor with its trigger pin and echo pin

    trigger_pin:integer, echo_pin:integer should be one of: (GPIO) 5, 6, 16, 17, 22, 23, 24, 25, 26, 27
        further information about the GPIO: https://pinout.xyz
    """
    def __init__(self, trigger_pin=17, echo_pin=27):
        super().__init__()
        self.trigger_pin = OutputDevice(pin=trigger_pin, initial_value=False)
        self.echo_pin = InputDevice(pin=echo_pin)

    """
    sets an integer containing the time the trigger pulse took bouncing back 
    """
    def update(self):
        # repeated function local access is faster than object reference
        tp = self.trigger_pin
        # ensure pin is initially low
        tp.value(0)
        sleep_us(2)
        # trigger pulse
        tp.value(1)
        sleep_us(10)
        tp.value(0)
        # wait for echo == 0 -> 1
        pulse_duration = self._time_pulse_us(self.echo_pin, 1, 20000)

        self.value = pulse_duration, self._in_cm(pulse_duration)

    """
    utility function for later which converts the pulse duration to a distance in cm
    """
    def _in_cm(self, pulse_duration):
        # pulse duration * speed of sound (cm) / 2 (echo takes double the distance)
        return pulse_duration * 0.034 / 2

    """
    implementation inspired by a micropython c implementation:
    https://github.com/micropython/micropython-esp32/blob/2f4dac5f121a59fc187c1d9c1f9eade365b3aba1/extmod/machine_pulse.c
    
    doc from the c implementation:
        Time a pulse on the given pin, and return the duration of the pulse in microseconds. 
        The pulse_level argument should be 0 to time a low pulse or 1 to time a high pulse.

        If the current input value of the pin is different to pulse_level, 
        the function first (*) waits until the pin input becomes equal to pulse_level, 
        then (**) times the duration that the pin is equal to pulse_level. 
        If the pin is already equal to pulse_level then timing starts straight away.

        The function will return -2 if there was timeout waiting for condition marked (*) above, 
        and -1 if there was timeout during the main measurement, marked (**) above. 
        The timeout is the same for both cases and given by timeout_us (which is in microseconds).
    """
    def _time_pulse_us(self, pin, pulse_level, timeout_us):
        start = ticks_us()
        while int(pin.value) != int(pulse_level):
            if ticks_us_diff_to_current(start) >= timeout_us:
                return -2
        start = ticks_us()
        while int(pin.value) == int(pulse_level):
            if ticks_us_diff_to_current(start) >= timeout_us:
                return -1
        return ticks_us_diff_to_current(start)
