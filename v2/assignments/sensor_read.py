from v2.assignments.abstract import AbstractAssignment


class ReadRawSensorData(AbstractAssignment):

    def __init__(self, setup_obj, sensor_manager):
        super().__init__(setup_obj)

        self._sensor_manager = sensor_manager
        self.sensor = sensor_manager.get_sensor_lease(self.setup_obj['sensor'])

        for pipe_id in self.possible_output_pipelines:
            self.add_dummy_pipeline(pipe_id, is_output=True)

    def cleanup(self):
        self.sensor.release_sensor_lease()

    def update(self):

        for pipeline in self.pipelines.values():
            pipeline.update_recv()  # must called on every socket or they go blocking

            if pipeline.is_output and pipeline.valid and self.sensor.value is not None:
                pipeline.buffer_out.append(self.sensor.value)

            pipeline.update_send()
