import esp32

from lh_lib.sensors.sensor import AbstractSensor


class Hall(AbstractSensor):

    """
    sets an integer of range +- unknown representing the current internal hall sensor reading
    """
    def update(self):
        self.value = esp32.hall_sensor()
