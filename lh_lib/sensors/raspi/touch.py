from gpiozero import InputDevice

from lh_lib.sensors.sensor import AbstractSensor


class Touch(AbstractSensor):

    """
    This represents a touch sensor with integrated Logic, where there is only one output pin,
    which digitally represents the touched state.

    pin:integer should be one of: (GPIO) 5, 6, 16, 17, 22, 23, 24, 25, 26, 27
        further information about the GPIO: https://pinout.xyz
    """
    def __init__(self, pin=17):
        super().__init__()
        self.input_device = InputDevice(pin=pin)

    """
    sets 0 for LOW and 1 for HIGH
    """
    def update(self):
        self.value = self.input_device.value
