import esp32

from sensors.sensor import AbstractSensor


class Hall(AbstractSensor):

    communication_name = 'hall'

    """
    sets an integer of range +- unknown representing the current internal hall sensor reading
    """
    def update(self):
        self.value = esp32.hall_sensor()
