from lh_lib.base.logging import log
from lh_lib.base.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.base.exceptions import NoReadableDataException, ConnectionClosedDownException, InvalidDataException, AssignmentException

INPUT_PIPELINE_TIMEOUT_MS = 3000
INPUT_PIPELINE_MAX_VALUES = 4000


class AbstractPipeline:

    def __init__(self, pipe_id, time_frame_ms, heartbeat_ms):
        self.conn = None
        self.pipe_id = pipe_id

        # indicates whether both pipeline ends are connected, e.g. actively handle read and write
        # connected is set top down, like the distribution of the assignment -> inputs to outputs
        self.connected = False
        # assignment-initialization is done bottom up (outputs to inputs) to make sure we do not loose values and therefore trigger wrong states
        self.assignment_initialized = False

        self.buffer_in = []
        self.buffer_out = []

        self.time_frame_ms = time_frame_ms
        self.heartbeat_ms = heartbeat_ms

        self.last_time_frame = 0

        self.last_data_exchange = ticks_ms()

    def cleanup(self):
        self.invalidate('cleanup')

    def invalidate(self, reason):
        if self.conn:
            self.conn.close()
            log('invalidating pipeline connection: {} | pipe_id: {} | reason: {} | lost output buffer of length: {}', self.conn.address, self.pipe_id, reason, len(self.buffer_out))
            self.conn = None
        else:
            log('invalidating pipeline | pipe_id: {} | reason: {} | lost output buffer of length: {}', self.pipe_id, reason, len(self.buffer_out))
        self.buffer_in.clear()
        self.buffer_out.clear()
        self.connected = False

    def update_recv(self):
        if not self.connected:
            return

        try:
            obj = self.conn.recv()
            self.last_data_exchange = ticks_ms()
        except NoReadableDataException:
            pass

            # if ticks_ms_diff_to_current(self.last_data_exchange) > INPUT_PIPELINE_TIMEOUT_MS:
            #     self.invalidate("no data received for more than {} milliseconds".format(INPUT_PIPELINE_TIMEOUT_MS))
        except ConnectionClosedDownException as e:
            self.invalidate('connection closed down: {}'.format(e))
        except InvalidDataException as e:
            self.invalidate('invalid data: {}'.format(e))
        else:
            if isinstance(obj, dict):
                self.handle_control_message(obj)
            else:
                # currently no length check, so ram overflow is possible
                self.buffer_in += obj
                if len(self.buffer_in) > INPUT_PIPELINE_MAX_VALUES:
                    self.invalidate('input buffer length > {} : {}'.format(INPUT_PIPELINE_MAX_VALUES, len(self.buffer_in)))

    def must_send(self):
        if self.time_frame_ms == 0:
            return bool(self.buffer_out) or ticks_ms_diff_to_current(self.last_time_frame) >= self.heartbeat_ms
        else:
            return ticks_ms_diff_to_current(self.last_time_frame) >= self.time_frame_ms

    def update_send(self):
        if not self.connected or not self.assignment_initialized:
            self.buffer_out.clear()
            return

        if self.must_send():
            try:
                self.conn.send(self.buffer_out)
            except ConnectionClosedDownException as e:
                self.invalidate('connection closed down: {}'.format(e))
            else:
                self.buffer_out.clear()
                self.last_time_frame = ticks_ms()
                self.last_data_exchange = ticks_ms()

    def handle_control_message(self, obj):
        raise Exception('This pipeline {} {} cannot handle control messages'.format(type(self), self.pipe_id))


class InputPipeline(AbstractPipeline):

    def __init__(self, conn, pipe_id, time_frame_ms, heartbeat_ms):
        super().__init__(pipe_id, time_frame_ms, heartbeat_ms)
        self.conn = conn
        self.connected = True

    def update_send(self):
        pass

    def send_assignment_initialized_message(self):
        self.assignment_initialized = True
        self.conn.send({
            'type': 'assignment_initialization'
        })
        self.conn.recv_acknowledgement()


class OutputPipeline(AbstractPipeline):

    def __init__(self, pipe_id):
        super().__init__(pipe_id, 0, 100)

    def activate(self, conn, time_frame_ms, heartbeat_ms):
        self.conn = conn
        self.connected = True

        self.time_frame_ms = time_frame_ms
        self.heartbeat_ms = heartbeat_ms

        self.last_data_exchange = ticks_ms()  # reset because between object creation and being connected can be more than 3 seconds

    def handle_control_message(self, d):
        try:
            message_type = d['type']

            if message_type == 'assignment_initialization':
                self.assignment_initialized = True
            else:
                raise Exception('unknown control-message type: {}'.format(message_type))
        except Exception as e:
            raise AssignmentException('unexpected error during processing pipeline control-message: {} {}'.format(type(e), e))
        else:
            try:
                self.conn.send_acknowledgement()
            except ConnectionClosedDownException as e:
                raise AssignmentException('remote unexpectedly closed down connection during sending acknowledgement: {} {}'.format(type(e), e))


class LocalPipeline(AbstractPipeline):

    def __init__(self, pipe_id):
        super().__init__(pipe_id, 0, 100)
        self.buffer_out = self.buffer_in
        self.connected = True
        self.assignment_initialized = True

    def cleanup(self):
        pass

    def update_recv(self):
        pass

    def update_send(self):
        pass
