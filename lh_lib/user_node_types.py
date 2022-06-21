
class UserNode:

    """
    Base class (abstract). Do not instantiate directly.
    """
    def __init__(self):
        self.sensors = {}

    def register_sensor(self, sensor_id, sensor_class):
        self.sensors[sensor_id] = sensor_class

    def execution_setup(self, pipelines, sensor_manager, assignment_id):
        for sensor_id in self.sensors:
            self.sensors[sensor_id] = sensor_manager.get_sensor_lease(self.sensors[sensor_id], assignment_id)

    """
    Overwrite this method for iterative updates
    """
    def run(self):
        raise Exception('Overwrite this method for iterative updates')


class NoInputSingleOutputUserNode(UserNode):

    def __init__(self, out0):
        super().__init__()
        self.out0 = out0

    def execution_setup(self, pipelines, sensor_manager, assignment_id):
        super().execution_setup(pipelines, sensor_manager, assignment_id)
        self.out0 = pipelines[self.out0].buffer_out


class SingleInputNoOutputUserNode(UserNode):

    def __init__(self, in0):
        super().__init__()
        self.in0 = in0

    def execution_setup(self, pipelines, sensor_manager, assignment_id):
        super().execution_setup(pipelines, sensor_manager, assignment_id)
        self.in0 = pipelines[self.in0].buffer_in


class SingleInputSingleOutputUserNode(UserNode):

    def __init__(self, in0, out0):
        super().__init__()
        self.in0 = in0
        self.out0 = out0

    def execution_setup(self, pipelines, sensor_manager, assignment_id):
        super().execution_setup(pipelines, sensor_manager, assignment_id)
        self.in0 = pipelines[self.in0].buffer_in
        self.out0 = pipelines[self.out0].buffer_out


class SingleInputDualOutputUserNode(UserNode):

    def __init__(self, in0, out0, out1):
        super().__init__()
        self.in0 = in0
        self.out0 = out0
        self.out1 = out1

    def execution_setup(self, pipelines, sensor_manager, assignment_id):
        super().execution_setup(pipelines, sensor_manager, assignment_id)
        self.in0 = pipelines[self.in0].buffer_in
        self.out0 = pipelines[self.out0].buffer_out
        self.out1 = pipelines[self.out1].buffer_out


class DualInputNoOutputUserNode(UserNode):

    def __init__(self, in0, in1):
        super().__init__()
        self.in0 = in0
        self.in1 = in1

    def execution_setup(self, pipelines, sensor_manager, assignment_id):
        super().execution_setup(pipelines, sensor_manager, assignment_id)
        self.in0 = pipelines[self.in0].buffer_in
        self.in1 = pipelines[self.in1].buffer_in


class DualInputSingleOutputUserNode(UserNode):

    def __init__(self, in0, in1, out0):
        super().__init__()
        self.in0 = in0
        self.in1 = in1
        self.out0 = out0

    def execution_setup(self, pipelines, sensor_manager, assignment_id):
        super().execution_setup(pipelines, sensor_manager, assignment_id)
        self.in0 = pipelines[self.in0].buffer_in
        self.in1 = pipelines[self.in1].buffer_in
        self.out0 = pipelines[self.out0].buffer_out
