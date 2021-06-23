

class Pipeline:

    pipeline_counter = 0

    def __init__(self, process_out):
        self.id = str(Pipeline.pipeline_counter)
        Pipeline.pipeline_counter += 1

        self.process_in = None
        self.process_out = process_out

    def assign_with_process(self, process_in):
        self.process_in = process_in
        return self

    def build_pipeline(self, devices, distribution):
        device_out = devices[self.process_out.device]
        device_in = devices[self.process_in.device]

        if self.process_out.device == self.process_in.device:
            distribution[self.process_out.device]['pipelines'][self.id] = {'type': 'local'}
            distribution[self.process_in.device]['pipelines'][self.id] = {'type': 'local'}
        elif device_out['host'] == device_in['host']:
            distribution[self.process_out.device]['pipelines'][self.id] = {'type': 'output'}
            distribution[self.process_in.device]['pipelines'][self.id] = {
                'type': 'input',
                'host': 'localhost',
                'port': device_out['port'],
                'time-frame': device_in['max-input-time-frame'],
                'values-per-time-frame': device_in['max-input-values-per-time-frame']
            }
        else:
            distribution[self.process_out.device]['pipelines'][self.id] = {'type': 'output'}
            distribution[self.process_in.device]['pipelines'][self.id] = {
                'type': 'input',
                'host': device_out['host'],
                'port': device_out['port'],
                'time-frame': device_in['max-input-time-frame'],
                'values-per-time-frame': device_in['max-input-values-per-time-frame']
            }


class Process:

    def __init__(self, device, **kwargs):
        self.device = device
        self.kwargs = kwargs
        self.input_pipelines = []
        self.output_pipelines = []

        for k, v in self.kwargs.items():
            if k.startswith('in'):
                pipe = v.assign_with_process(self)
                self.input_pipelines.append(pipe)
                self.kwargs[k] = pipe.id
            elif k.startswith('out'):
                pipe = Pipeline(self)
                self.output_pipelines.append(pipe)
                self.kwargs[k] = pipe.id
                setattr(self, k, pipe)

    def build_distribution(self, assignment_id, devices, distribution=None, assignment_order=None, seen_processes=None):
        if distribution is None:
            distribution = {device_id: {'assignment-id': assignment_id, 'pipelines': {}, 'processing': []} for device_id in devices}
        if assignment_order is None:
            assignment_order = []
        if seen_processes is None:
            seen_processes = set()

        seen_processes.add(self)

        for pipe in self.input_pipelines:
            if pipe.process_out not in seen_processes:
                pipe.build_pipeline(devices, distribution)
                pipe.process_out.build_distribution(assignment_id, devices, distribution, assignment_order, seen_processes)

        if self.device not in assignment_order:
            assignment_order.append(self.device)

        distribution[self.device]['processing'].append({'class': type(self).__name__, 'kwargs': self.kwargs})

        for pipe in self.output_pipelines:
            if pipe.process_in not in seen_processes:
                pipe.build_pipeline(devices, distribution)
                pipe.process_in.build_distribution(assignment_id, devices, distribution, assignment_order, seen_processes)

        return distribution, assignment_order
