from lh_lib.network import Client
from lh_lib.exceptions import AssignmentException
from lh_lib.pipeline import PipelineConnection, PrintPipeline


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
        self.sensor_processing = setup_obj['sensor_processing']

        # sensor setup
        self.sensors = {sensor_id: sensor_manager.get_sensor_lease(sensor['name']) for sensor_id, sensor in setup_obj['input-sensors'].items()}

        # pipeline setup
        self.possible_output_pipelines = set(setup_obj['output-pipe-id-list'])

        self.pipelines = {}

        for pipe_id in self.possible_output_pipelines:
            self.add_dummy_pipeline(pipe_id, is_output=True)

        for pipe_id, pipe in setup_obj['print-pipes'].items():
            self.create_print_pipeline(pipe_id, pipe['time-frame'], pipe['values-per-time-frame'])

        for pipe_id, pipe in setup_obj['input-pipes'].items():
            self.open_input_pipeline(pipe['host'], pipe['port'], pipe_id, pipe['time-frame'], pipe['values-per-time-frame'])

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
                output_pipe.buffer_out.append(input_pipe.buffer_in[0])
                del input_pipe.buffer_in[0]

        for input_id, output_id in self.sensor_processing.items():
            input_sensor = self.sensors[input_id]
            output_pipe = self.pipelines[output_id]

            if output_pipe.valid and input_sensor.value is not None:
                output_pipe.buffer_out.append(input_sensor.value)

        for pipeline in self.pipelines.values():
            pipeline.update_send()  # only affects output pipelines

    def assign_output_pipeline(self, conn, pipe_id, time_frame, values_per_time_frame):
        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection (during assign output pipeline)".format(pipe_id))

        self.pipelines[pipe_id] = PipelineConnection(conn, pipe_id, time_frame, values_per_time_frame, is_output=True)

    def create_print_pipeline(self, pipe_id, time_frame, values_per_time_frame):
        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection (during create print pipeline)".format(pipe_id))

        self.pipelines[pipe_id] = PrintPipeline(pipe_id, time_frame, values_per_time_frame)

    def open_input_pipeline(self, host, port, pipe_id, time_frame, values_per_time_frame):
        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection (during open input pipeline)".format(pipe_id))

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
        self.pipelines[pipe_id] = PipelineConnection(conn, pipe_id, time_frame, values_per_time_frame, is_output=False)

    def add_dummy_pipeline(self, pipe_id, is_output):
        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection (during create dummy pipeline)".format(pipe_id))

        self.pipelines[pipe_id] = PipelineConnection(None, pipe_id, 0, 0, is_output, valid=False)

    def check_assignment(self):
        return True
