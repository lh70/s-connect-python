from lh_lib.exceptions import CommunicationException


class SensorManager:

    """
    takes sensor objects as arguments and stores them for an efficient update policy, where unneeded sensors are ignored

    *sensors:AbstractSensor, AbstractSensor,... takes initialised sensors as input
    """
    def __init__(self, *sensors):
        self.sensors = sensors

    """
    calls update on all sensors which are currently in use
    """
    def update(self):
        for sensor in self.sensors:
            # leases stores how many connections want to read from that sensor
            if sensor.leases > 0:
                sensor.update()

    """
    increases the sensors lease count by one
    
    returns the sensor object or raises CommunicationException if sensor was not found by name (case sensitive)
    """
    def get_sensor_lease(self, communication_name):
        for sensor in self.sensors:
            if sensor.communication_name == communication_name:
                sensor.leases += 1
                return sensor
        raise CommunicationException('lease failed: sensor {} does not exist on this computer'.format(communication_name))

    """
    decreases the sensors leases by one
    
    to be called on connection removal
    """
    def release_sensor_lease(self, sensor):
        sensor.leases -= 1
