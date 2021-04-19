import esp32

from lh_lib.sensors.sensor import AbstractSensor


class Temperature(AbstractSensor):

    communication_name = 'temperature'

    """
    sets the internal temperature sensor reading in Fahrenheit as an integer
    """
    def update(self):
        self.value = esp32.raw_temperature()
