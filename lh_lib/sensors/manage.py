from lh_lib.exceptions import CommunicationException


class SensorManager:

    """
    takes sensor objects as arguments and stores them for an efficient update policy, where unneeded sensors are ignored

    *sensors:AbstractSensor, AbstractSensor,... takes initialised sensors as input
    """
    def __init__(self, *supported_sensor_classes):
        self.supported_sensor_classes = supported_sensor_classes
        self.observables = {}

    """
    calls update on all observables
    """
    def update(self):
        for observables in self.observables.values():
            for observable in observables:
                observable.update()

    """
    creates a new sensor observable that gets updated by the sensor manager
    
    returns the sensor observable object or raises CommunicationException if sensor was not found by name (case sensitive)
    """
    def get_sensor_lease(self, sensor_class_name, assignment_id, **sensor_class_kwargs):
        for sensor_class in self.supported_sensor_classes:
            if sensor_class_name == sensor_class.__name__:
                if assignment_id not in self.observables:
                    self.observables[assignment_id] = []
                self.observables[assignment_id].append(sensor_class(**sensor_class_kwargs))
                return self.observables[assignment_id][-1]
        raise CommunicationException('lease failed: sensor {} is not supported by this computer'.format(sensor_class_name))

    """
    removes all sensors of an assignment
    """
    def remove_assignment_sensors(self, assignment_id):
        if assignment_id in self.observables:
            del self.observables[assignment_id]
