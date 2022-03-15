import re

from lh_lib.network_stack.client import Client
from lh_lib.exceptions import AssignmentException
from lh_lib.pipeline import InputPipeline, OutputPipeline, LocalPipeline

"""
Following imports are usable in the dynamic node functions
"""
import os

from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.logging import DataLogger


class Assignment:

    def __init__(self, setup_obj, sensor_manager):
        # initialization happens after distribution is finished and all pipelines are active
        # the initialization then happens bottom up, where the outputs are first
        self.assignment_initialized = False

        self.setup_obj = setup_obj
        self.sensor_manager = sensor_manager
        self.assignment_id = setup_obj['id']
        self.leased_sensors = []

        # pipeline setup
        self.pipelines = {}
        for pipe_id, pipe_config in setup_obj['pipelines'].items():
            self.create_pipeline(pipe_id, pipe_config)

        # processing setup
        self.processing = setup_obj['processing']
        for proc in self.processing:
            exec(proc['code'], globals(), locals())
            proc['run'] = locals()[proc['func_name']]
            proc['kwargs']['storage'] = {}
            for kw, value in proc['kwargs'].items():
                if re.match('^in[0-9]+$', kw):
                    proc['kwargs'][kw] = self.pipelines[value].buffer_in
                elif re.match('^out[0-9]+$', kw):
                    proc['kwargs'][kw] = self.pipelines[value].buffer_out
                elif re.match('^sensor$', kw):
                    proc['kwargs'][kw] = self.sensor_manager.get_sensor_lease(value)

    def cleanup(self):
        for pipeline in self.pipelines.values():
            pipeline.cleanup()

        for sensor in self.leased_sensors:
            sensor.release_sensor_lease()

    def update(self):
        for pipeline in self.pipelines.values():
            pipeline.update_recv()  # must called on every socket or they go blocking

        if self.assignment_initialized:
            # only process and produce values if initialization is finished
            for proc in self.processing:
                proc['run'](**proc['kwargs'])
        else:
            # check if all output pipelines received an assignment-initialization message
            output_pipelines_initialized = True
            for pipeline in self.pipelines.values():
                if isinstance(pipeline, OutputPipeline):
                    output_pipelines_initialized &= pipeline.assignment_initialized

            if output_pipelines_initialized:
                # send the initialization message forward on all input pipelines
                for pipeline in self.pipelines.values():
                    if isinstance(pipeline, InputPipeline) and not pipeline.assignment_initialized:
                        pipeline.send_assignment_initialized_message()
                # initialization is now finished for this assignment on this device
                self.assignment_initialized = True

        for pipeline in self.pipelines.values():
            pipeline.update_send()  # only affects output pipelines

    def create_pipeline(self, pipe_id, pipeline_config):
        pipe_type = pipeline_config['type']  # get here, so we get no confusing exceptions during the possible raise

        if pipe_id in self.pipelines and self.pipelines[pipe_id].connected:
            raise AssignmentException(f'pipe_id {pipe_id} has already a valid pipeline connection (during creating {pipe_type} pipeline)')

        if pipe_type == 'input':
            host = pipeline_config['host']
            port = pipeline_config['port']
            time_frame = pipeline_config['time_frame']
            values_per_time_frame = pipeline_config['values_per_time_frame']

            conn = Client(host, port)
            conn.send({
                'type': 'pipeline_request',
                'content': {
                    'assignment_id': self.assignment_id,
                    'pipe_id': pipe_id,
                    'time_frame': time_frame,
                    'values_per_time_frame': values_per_time_frame
                }
            })
            conn.recv_acknowledgement()
            self.pipelines[pipe_id] = InputPipeline(conn, pipe_id, time_frame, values_per_time_frame)
        elif pipe_type == 'output':
            self.pipelines[pipe_id] = OutputPipeline(pipe_id)  # dummy (invalid) pipeline, gets valid on pipeline request
        elif pipe_type == 'local':
            self.pipelines[pipe_id] = LocalPipeline(pipe_id)  # local pipeline is always valid
        else:
            raise AssignmentException(f'pipeline type {pipe_type} does not exist (during creating pipeline {pipe_id})')

    def assign_output_pipeline(self, conn, pipe_id, time_frame, values_per_time_frame):
        if pipe_id in self.pipelines:
            if self.pipelines[pipe_id].connected:
                raise AssignmentException(f'pipe-id {pipe_id} has already a valid pipeline connection (during assign output pipeline)')
            else:
                self.pipelines[pipe_id].activate(conn, time_frame, values_per_time_frame)
        else:
            raise AssignmentException(f'pipe-id {pipe_id} does not exists in outputs of assignment {self.assignment_id}')
