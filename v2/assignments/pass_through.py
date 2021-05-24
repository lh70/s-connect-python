from v2.assignments.abstract import AbstractAssignment
from lh_lib.exceptions import AssignmentException
from lh_lib.logging import log


class PassThrough(AbstractAssignment):

    def __init__(self, setup_obj):
        super().__init__(setup_obj)

        host = self.setup_obj['input-pipe-host']
        port = self.setup_obj['input-pipe-port']
        pipe_id = self.setup_obj['input-pipe-id']
        time_frame = self.setup_obj['input-pipe-time-frame']
        values_per_time_frame = self.setup_obj['input-pipe-values-per-time-frame']

        self.open_input_pipeline(host, port, pipe_id, time_frame, values_per_time_frame)

        self.input_pipe_id = pipe_id

        for pipe_id in self.possible_output_pipelines:
            self.add_dummy_pipeline(pipe_id, is_output=True)

    def update(self):
        for pipeline in self.pipelines.values():
            pipeline.update_recv()  # must called on every socket or they go blocking

        pipeline_in = self.pipelines[self.input_pipe_id]

        if not pipeline_in.valid:
            raise AssignmentException("input pipeline got invalid")

        if pipeline_in.buffer_in:
            for pipeline_out in self.pipelines.values():

                if pipeline_out.is_output and pipeline_out.valid and pipeline_in.buffer_in:
                    # log("passing values: {}".format(pipeline_in.buffer_in))
                    # pipeline_out.buffer_out += pipeline_in.buffer_in
                    pipeline_out.buffer_out.append(pipeline_in.buffer_in[0])

                pipeline_out.update_send()

            # pipeline_in.buffer_in.clear()
            del pipeline_in.buffer_in[0]
