from lh_lib.network import Client
from lh_lib.pipeline import PipelineConnection
from lh_lib.exceptions import AssignmentException

INPUT_PIPELINE_TIMEOUT_MS = 3000


class AbstractAssignment:

    def __init__(self, setup_obj):
        self.setup_obj = setup_obj
        self.assignment_id = setup_obj['assignment-id']

        self.possible_output_pipelines = set(setup_obj['output-pipe-id-list'])
        self.pipelines = {}

    def cleanup(self):
        pass

    def assign_output_pipeline(self, conn, pipe_id, time_frame, values_per_time_frame):
        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection".format(pipe_id))

        self.pipelines[pipe_id] = PipelineConnection(conn, pipe_id, time_frame, values_per_time_frame, is_output=True)

    def open_input_pipeline(self, host, port, pipe_id, time_frame, values_per_time_frame):
        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection".format(pipe_id))

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
        self.pipelines[pipe_id] = PipelineConnection(None, pipe_id, 0, 0, is_output, valid=False)
