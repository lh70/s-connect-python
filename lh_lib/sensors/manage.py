from lh_lib.exceptions import CommunicationException


class SensorManager:

    """
    takes sensor objects as arguments and stores them for an efficient update policy, where unneeded sensors are ignored

    *sensors:AbstractSensor, AbstractSensor,... takes initialised sensors as input
    """
    def __init__(self, *sensors):
        self.observables = {sensor.communication_name: SensorObservable(sensor) for sensor in sensors}

    """
    calls update on all observables
    """
    def update(self):
        for observable in self.observables.values():
            observable.update()

    """
    increases the sensors lease count by one
    
    returns the sensor observable object or raises CommunicationException if sensor was not found by name (case sensitive)
    """
    def get_sensor_lease(self, communication_name):
        if communication_name in self.observables:
            self.observables[communication_name].get_sensor_lease()
            return self.observables[communication_name]
        raise CommunicationException('lease failed: sensor {} does not exist on this computer'.format(communication_name))

    """
    decreases the sensors leases by one
    
    to be called on connection removal
    """
    def release_sensor_lease(self, observable):
        observable.release_sensor_lease()


class SensorObservable:

    """
    adds state to a sensor, implementing lazy updates,
    so updates and interrupts are only used when the sensor is in use

    sensor:AbstractSensor the sensor to observe
    """
    def __init__(self, sensor):
        self.sensor = sensor
        self.leases = 0

    """
    gets called repeatedly by the sensor manager
    only updates sensor when it is in use
    """
    def update(self):
        if self.leases > 0:
            self.sensor.update()

    """
    returns the sensors value
    mimics the sensors behavior
    
    can return any serializable value
    """
    @property
    def value(self):
        return self.sensor.value

    """
    updates the in-use-counter
    starts the sensors irq if necessary
    """
    def get_sensor_lease(self):
        if self.leases == 0:
            self.sensor.start_irq()
        self.leases += 1

    """
    updates the in-use-counter
    stops the sensors irq if necessary
    """
    def release_sensor_lease(self):
        self.leases -= 1
        if self.leases == 0:
            self.sensor.stop_irq()
