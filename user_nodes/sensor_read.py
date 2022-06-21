from lh_lib.user_node_types import NoInputSingleOutputUserNode
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


class SensorRead(NoInputSingleOutputUserNode):

    def __init__(self, out0, sensor_class_name, read_delay_ms=0):
        super().__init__(out0)
        self.read_delay_ms = read_delay_ms
        self.last_valid_value = None
        self.last_read_time = 0
        self.register_sensor('sensor', sensor_class_name)

    def run(self):
        sensor_value = self.sensors['sensor'].value

        if self.read_delay_ms == 0:  # old behaviour. read is faster than the sensor can provide values.
            if sensor_value is not None:
                self.out0.append(sensor_value)
        else:  # new behaviour. sensor is faster than the framework can process the values further down the line.
            if sensor_value is not None:
                self.last_valid_value = sensor_value

            if ticks_ms_diff_to_current(self.last_read_time) > self.read_delay_ms and self.last_valid_value is not None:
                self.last_read_time = ticks_ms()
                self.out0.append(self.last_valid_value)
