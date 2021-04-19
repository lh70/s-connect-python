from exceptions import CommunicationException


class SensorManager:

    def __init__(self, *sensors):
        self.sensors = sensors

    def update(self):
        for sensor in self.sensors:
            if sensor.leases > 0:
                sensor.update()

    def get_sensor_lease(self, communication_name):
        for sensor in self.sensors:
            if sensor.communication_name == communication_name:
                sensor.leases += 1
                return sensor
        raise CommunicationException('lease failed: sensor {} does not exist on this computer'.format(communication_name))

    def release_sensor_lease(self, sensor):
        sensor.leases -= 1
