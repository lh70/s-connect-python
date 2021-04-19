import dht

from lh_lib.sensors.sensor import AbstractSensor


class DHT11(AbstractSensor):

    communication_name = 'dht11'

    """
    Initialises the standard library DHT11 class with the input/output pin

    pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    """
    def __init__(self, pin):
        super().__init__()
        self.d = dht.DHT11(pin)

    """
    updates the value to a tuple (temperature, humidity)
    """
    def update(self):
        self.d.measure()
        self.value = self.d.temperature(), self.d.humidity()
