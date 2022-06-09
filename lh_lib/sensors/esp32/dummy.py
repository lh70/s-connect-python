from lh_lib.sensors.sensor import AbstractSensor


class Dummy(AbstractSensor):

    def update(self):
        self.value = 42
