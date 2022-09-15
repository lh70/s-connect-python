from machine import Pin

from lh_lib.sensors.sensor import AbstractSensor


class Button(AbstractSensor):

    """
    Initialises a simple button input
    
    pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    
    pull_up:bool whether to use an internal pull_up resistor on the input or not
    """
    def __init__(self, pin=14, pull_up=True):
        super().__init__()
        self.pin = Pin(pin, mode=Pin.IN, pull=Pin.PULL_UP if pull_up else Pin.PULL_DOWN)
        self.pull_up = pull_up

    """
    sets the sensors value to True if the button is pressed and to False if it is not pressed
    """
    def update(self):
        self.value = bool(self.pin.value() ^ self.pull_up)
