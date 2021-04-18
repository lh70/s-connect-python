from machine import Pin


class Touch:

    communication_name = 'touch'

    """
    This represents a touch sensor with integrated Logic, where there is only one output pin,
    which digitally represents the touched state.

    pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    """
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN)

    """
    returns 0 for LOW and 1 for HIGH
    """
    def get(self):
        return self.pin.value()
