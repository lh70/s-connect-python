from utime import sleep_us
from machine import Pin, time_pulse_us

from lh_lib.sensors.sensor import AbstractSensor


class Ultrasonic(AbstractSensor):

    communication_name = 'ultrasonic'

    """
    Initialises an ultrasonic sensor with its trigger pin and echo pin

    trigger_pin:integer can be one of all the GPIO pins: 0-19, 21-23, 25-27  but NOT 32-39 as these are input only
                        it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    echo_pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                     it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    """
    def __init__(self, trigger_pin, echo_pin):
        super().__init__()
        self.trigger_pin = Pin(trigger_pin, Pin.OUT, value=0)
        self.echo_pin = Pin(echo_pin, Pin.IN)

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
        self.value = time_pulse_us(self.echo_pin, 0, timeout_us=2000)

    """
    utility function for later which converts the pulse duration to a distance in cm
    """
    def _in_cm(self, pulse_duration):
        # pulse duration * speed of sound (cm) / 2 (echo takes double the distance)
        return pulse_duration * 0.034 / 2
