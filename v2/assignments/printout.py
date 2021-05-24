from lh_lib.logging import log
from lh_lib.exceptions import AssignmentException
from v2.assignments.abstract import AbstractAssignment


class SensorPrintout(AbstractAssignment):

    def __init__(self, setup_obj):
        super().__init__(setup_obj)

        host = self.setup_obj['input-pipe-host']
        port = self.setup_obj['input-pipe-port']
        pipe_id = self.setup_obj['input-pipe-id']
        time_frame = self.setup_obj['input-pipe-time-frame']
        values_per_time_frame = self.setup_obj['input-pipe-values-per-time-frame']

        self.open_input_pipeline(host, port, pipe_id, time_frame, values_per_time_frame)

        self.input_pipe_id = pipe_id

    def update(self):
        for pipeline in self.pipelines.values():
            pipeline.update_recv()  # must called on every socket or they go blocking

        pipeline = self.pipelines[self.input_pipe_id]

        if not pipeline.valid:
            raise AssignmentException("input pipeline got invalid")

        if pipeline.buffer_in:
            log("got values: {}".format(pipeline.buffer_in))
            pipeline.buffer_in.clear()
