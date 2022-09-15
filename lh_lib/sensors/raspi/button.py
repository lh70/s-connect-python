from gpiozero import Button as GPIOButton

from lh_lib.sensors.sensor import AbstractSensor


class Button(AbstractSensor):

    """
    Initialises a simple button input
    
    pin:integer should be one of: (GPIO) 5, 6, 16, 17, 22, 23, 24, 25, 26, 27
        further information about the GPIO: https://pinout.xyz
    
    pull_up:bool whether to use an internal pull_up resistor on the input or not
    """
    def __init__(self, pin=22, pull_up=True):
        super().__init__()
        self.gpioButton = GPIOButton(pin=pin, pull_up=pull_up)

    """
    sets the sensors value to True if the button is pressed and to False if it is not pressed
    """
    def update(self):
        self.value = bool(self.gpioButton.value)
