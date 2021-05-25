from lh_lib.network import Client
from lh_lib.exceptions import AssignmentException
from lh_lib.pipeline import InputPipeline, OutputPipeline, PrintPipeline


class GeneralAssignment:

    def __init__(self, setup_obj, sensor_manager):
        self.setup_obj = setup_obj
        self.assignment_id = setup_obj['assignment-id']

        # check assignment for double id usage of any kind
        self.check_assignment()

        # processing setup... currently only pass-through
        # k:v -> input-id:output-id
        self.pipeline_processing = setup_obj['pipeline-processing']
        # k:v -> sensor-id:output-id
        self.sensor_processing = setup_obj['sensor-processing']

        # sensor setup
        self.sensors = {sensor_id: sensor_manager.get_sensor_lease(sensor['name']) for sensor_id, sensor in setup_obj['sensors'].items()}

        # pipeline setup
        self.pipelines = {}
        for pipe_id, pipe_config in setup_obj['pipelines'].items():
            self.create_pipeline(pipe_id, pipe_config)

        self.possible_output_pipelines = set(pipe_id for pipe_id, pipe in self.pipelines.items() if isinstance(pipe, OutputPipeline))

    def cleanup(self):
        for sensor in self.sensors.values():
            sensor.release_sensor_lease()

    def update(self):
        for pipeline in self.pipelines.values():
            pipeline.update_recv()  # must called on every socket or they go blocking

        for input_id, output_id in self.pipeline_processing.items():
            input_pipe = self.pipelines[input_id]
            output_pipe = self.pipelines[output_id]

            if output_pipe.valid and input_pipe.buffer_in:
                #output_pipe.buffer_out += input_pipe.buffer_in
                #input_pipe.buffer_in.clear()
                output_pipe.buffer_out.append(input_pipe.buffer_in[0])
                del input_pipe.buffer_in[0]

        for input_id, output_id in self.sensor_processing.items():
            input_sensor = self.sensors[input_id]
            output_pipe = self.pipelines[output_id]

            if output_pipe.valid and input_sensor.value is not None:
                output_pipe.buffer_out.append(input_sensor.value)

        for pipeline in self.pipelines.values():
            pipeline.update_send()  # only affects output pipelines

    def create_pipeline(self, pipe_id, pipeline_config):
        pipe_type = pipeline_config['type']  # get here, so we get no confusing exceptions during the possible raise

        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection (during creating {} pipeline)".format(pipe_id, pipe_type))

        if pipe_type == 'output':
            self.pipelines[pipe_id] = OutputPipeline(None, pipe_id, 0, 0, valid=False)  # dummy pipeline, because it must exist
        elif pipe_type == 'print':
            time_frame = pipeline_config['time-frame']
            values_per_time_frame = pipeline_config['values-per-time-frame']

            self.pipelines[pipe_id] = PrintPipeline(pipe_id, time_frame, values_per_time_frame)
        elif pipe_type == 'input':
            host = pipeline_config['host']
            port = pipeline_config['port']
            time_frame = pipeline_config['time-frame']
            values_per_time_frame = pipeline_config['values-per-time-frame']

            conn = Client(host, port)
            conn.send({
                'pipeline-request': {
                    'assignment-id': self.assignment_id,
                    'pipe-id': pipe_id,
                    'time-frame': time_frame,
                    'values-per-time-frame': values_per_time_frame
                }
            })
            conn.recv_acknowledgement()
            self.pipelines[pipe_id] = InputPipeline(conn, pipe_id, time_frame, values_per_time_frame)
        else:
            raise AssignmentException("pipeline type {} does not exist (during creating pipeline {})".format(pipe_type, pipe_id))

    def assign_output_pipeline(self, conn, pipe_id, time_frame, values_per_time_frame):
        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection (during assign output pipeline)".format(pipe_id))

        self.pipelines[pipe_id] = OutputPipeline(conn, pipe_id, time_frame, values_per_time_frame, valid=True)

    def check_assignment(self):
        return True
