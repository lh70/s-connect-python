from machine import Pin

from lh_lib.sensors.sensor import AbstractSensor


class Button(AbstractSensor):

    communication_name = 'button'

    """
    Initialises a simple button input
    
    pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    
    pull:CONSTANT (default=Pin.PULL_UP) can be one of Pin.PULL_UP, Pin.PULL_DOWN, None
    
    Note: logic considers pull=None to read states as Pin.PULL_DOWN -> 1=>True, 0=>False
    """
    def __init__(self, pin=14, pull=Pin.PULL_UP):
        super().__init__()
        self.pin = Pin(pin, mode=Pin.IN, pull=pull)
        self.pull = pull

    """
    sets the sensors value to True if the button is pressed and to False if it is not pressed
    """
    def update(self):
        self.value = bool(self.pin.value() ^ (self.pull == Pin.PULL_UP))
