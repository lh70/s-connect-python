from lh_lib.sensors.sensor import AbstractSensor


class Dummy(AbstractSensor):

    communication_name = 'dummy'

    def update(self):
        self.value = 42
