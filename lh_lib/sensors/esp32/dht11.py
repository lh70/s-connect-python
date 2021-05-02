import dht

from machine import Pin
from utime import ticks_ms, ticks_diff

from lh_lib.sensors.sensor import AbstractSensor

"""
For an inexplicable reason there is a minimum interval on which repeating requests will not run into timeout.
For my esp32 + dht11 combo this seems to be 1 second == 1000ms.
Lesser values seem to run into timeout immediately or after some readings.
"""
MINIMUM_MEASURING_INTERVAL_MS = 1000


class DHT11(AbstractSensor):

    communication_name = 'dht11'

    """
    Initialises the standard library DHT11 class with the input/output pin

    pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-33
                it cannot be one of GPIO pins: 34-39 (input only pins)
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    
    Note:
        The driver used here seems fragile.
        Except the timeout, also the pin choice seem to affect if it works or runs into timeout.
        Pins that seem to work: 13
    """
    def __init__(self, pin):
        super().__init__()
        self.d = dht.DHT11(Pin(pin, mode=Pin.IN, pull=Pin.PULL_UP))
        self.last_measuring = ticks_ms() - MINIMUM_MEASURING_INTERVAL_MS

    """
    updates the value to a tuple (temperature, humidity)
    """
    def update(self):
        if ticks_diff(ticks_ms(), self.last_measuring) > MINIMUM_MEASURING_INTERVAL_MS:
            self.d.measure()
            self.value = (self.d.temperature(), self.d.humidity())
            self.last_measuring = ticks_ms()
        else:
            self.value = None
