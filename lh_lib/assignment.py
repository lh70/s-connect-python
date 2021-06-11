from lh_lib.network import Client
from lh_lib.exceptions import AssignmentException
from lh_lib.pipeline import InputPipeline, OutputPipeline, LocalPipeline

import lh_lib.processing


class GeneralAssignment:

    def __init__(self, setup_obj, sensor_manager):
        self.setup_obj = setup_obj
        self.sensor_manager = sensor_manager
        self.assignment_id = setup_obj['assignment-id']
        self.leased_sensors = []

        # pipeline setup
        self.pipelines = {}
        for pipe_id, pipe_config in setup_obj['pipelines'].items():
            self.create_pipeline(pipe_id, pipe_config)

        # processing setup
        self.processing = setup_obj['processing']
        for proc in self.processing:
            proc['method'] = getattr(lh_lib.processing, proc['method'])

            proc['kwargs']['storage'] = {}

            for kw, value in proc['kwargs'].items():
                if kw.startswith('in'):
                    proc['kwargs'][kw] = self.pipelines[value].buffer_in
                elif kw.startswith('out'):
                    proc['kwargs'][kw] = self.pipelines[value].buffer_out
                elif kw.startswith('sensor'):
                    proc['kwargs'][kw] = self.sensor_manager.get_sensor_lease(value)

    def cleanup(self):
        for pipeline in self.pipelines.values():
            pipeline.cleanup()

        for sensor in self.leased_sensors:
            sensor.release_sensor_lease()

    def update(self):
        for pipeline in self.pipelines.values():
            pipeline.update_recv()  # must called on every socket or they go blocking

        for proc in self.processing:
            proc['method'](**proc['kwargs'])

        for pipeline in self.pipelines.values():
            pipeline.update_send()  # only affects output pipelines

    def create_pipeline(self, pipe_id, pipeline_config):
        pipe_type = pipeline_config['type']  # get here, so we get no confusing exceptions during the possible raise

        if pipe_id in self.pipelines and self.pipelines[pipe_id].valid:
            raise AssignmentException("pipe_id {} has already a valid pipeline connection (during creating {} pipeline)".format(pipe_id, pipe_type))

        if pipe_type == 'input':
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
        elif pipe_type == 'output':
            self.pipelines[pipe_id] = OutputPipeline(pipe_id)  # dummy (invalid) pipeline, gets valid on pipeline request
        elif pipe_type == 'local':
            self.pipelines[pipe_id] = LocalPipeline(pipe_id)
        else:
            raise AssignmentException("pipeline type {} does not exist (during creating pipeline {})".format(pipe_type, pipe_id))

    def assign_output_pipeline(self, conn, pipe_id, time_frame, values_per_time_frame):
        if pipe_id in self.pipelines:
            if self.pipelines[pipe_id].valid:
                raise AssignmentException("pipe-id {} has already a valid pipeline connection (during assign output pipeline)".format(pipe_id))
            else:
                self.pipelines[pipe_id].make_valid(conn, time_frame, values_per_time_frame)
        else:
            raise AssignmentException("pipe-id {} does not exists in outputs of assignment {}".format(pipe_id, self.assignment_id))
