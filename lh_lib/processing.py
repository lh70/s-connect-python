import re

from lh_lib.network import Client


class Pipeline:

    pipeline_counter = 0

    def __init__(self, process_out):
        self.seen = False

        self.id = str(Pipeline.pipeline_counter)
        Pipeline.pipeline_counter += 1

        self.process_in = None
        self.process_out = process_out

    def assign_with_process(self, process_in):
        self.process_in = process_in
        return self

    def build_pipeline(self, distribution):
        self.seen = True

        if self.process_out.device == self.process_in.device:
            distribution[self.process_out.device.id]['pipelines'][self.id] = {'type': 'local'}
            distribution[self.process_in.device.id]['pipelines'][self.id] = {'type': 'local'}
        elif self.process_out.device.host == self.process_in.device.host:
            distribution[self.process_out.device.id]['pipelines'][self.id] = {'type': 'output'}
            distribution[self.process_in.device.id]['pipelines'][self.id] = {
                'type': 'input',
                'host': 'localhost',
                'port': self.process_out.device.port,
                'time-frame': self.process_in.device.max_time_frame,
                'values-per-time-frame': self.process_in.device.max_values_per_time_frame
            }
        else:
            distribution[self.process_out.device.id]['pipelines'][self.id] = {'type': 'output'}
            distribution[self.process_in.device.id]['pipelines'][self.id] = {
                'type': 'input',
                'host': self.process_out.device.host,
                'port': self.process_out.device.port,
                'time-frame': self.process_in.device.max_time_frame,
                'values-per-time-frame': self.process_in.device.max_values_per_time_frame
            }


class NoOutputProcess:

    def __init__(self, device, **kwargs):
        self.seen = False

        self.device = device
        self.kwargs = kwargs
        self.input_pipelines = []
        self.output_pipelines = []

        for k, v in self.kwargs.items():
            if re.match('^in[0-9]+$', k):
                pipe = v.assign_with_process(self)
                self.input_pipelines.append(pipe)
                self.kwargs[k] = pipe.id

    def build_distribution(self, assignment_id, distribution=None, assignment_order=None):
        self.seen = True

        if distribution is None:
            distribution = {device.id: {'assignment-id': assignment_id, 'pipelines': {}, 'processing': []} for device in Device.devices}
        if assignment_order is None:
            assignment_order = []

        for pipe in self.input_pipelines:
            if not pipe.seen:
                pipe.build_pipeline(distribution)
            if not pipe.process_out.seen:
                pipe.process_out.build_distribution(assignment_id, distribution, assignment_order)

        if self.device not in assignment_order:
            assignment_order.append(self.device)

        distribution[self.device.id]['processing'].append({'class': type(self).__name__, 'kwargs': self.kwargs})

        for pipe in self.output_pipelines:
            if not pipe.seen:
                pipe.build_pipeline(distribution)
            if not pipe.process_in.seen:
                pipe.process_in.build_distribution(assignment_id, distribution, assignment_order)

        return distribution, assignment_order


class SingleOutputProcess(NoOutputProcess):

    def __init__(self, device, **kwargs):
        super().__init__(device, **kwargs)
        self.out0 = Pipeline(self)
        self.output_pipelines.append(self.out0)
        self.kwargs['out0'] = self.out0.id


class DualOutputProcess(NoOutputProcess):
    def __init__(self, device, **kwargs):
        super().__init__(device, **kwargs)
        self.out0 = Pipeline(self)
        self.out1 = Pipeline(self)
        self.output_pipelines.append(self.out0)
        self.output_pipelines.append(self.out1)
        self.kwargs['out0'] = self.out0.id
        self.kwargs['out1'] = self.out1.id


class Device:

    devices = []
    device_counter = 0

    def __init__(self, host='localhost', port=8090, max_time_frame=100, max_values_per_time_frame=0):
        self.id = str(Device.device_counter)
        Device.device_counter += 1

        for device in Device.devices:
            if device.host == host and device.port == port:
                raise Exception("Devices {} and {} has same host/port configuration".format(device.id, self.id))

        Device.devices.append(self)
        self.host = host
        self.port = port
        self.max_time_frame = max_time_frame
        self.max_values_per_time_frame = max_values_per_time_frame

    def remove_assignment(self, assignment_id):
        conn = Client(self.host, self.port)
        conn.send({'remove-assignment': {'assignment-id': assignment_id}})
        conn.recv_acknowledgement()
        conn.socket.close()

    def distribute_assignment(self, distribution):
        conn = Client(self.host, self.port)
        conn.send({'processing-assignment': distribution[self.id]})
        conn.recv_acknowledgement()
        conn.socket.close()
