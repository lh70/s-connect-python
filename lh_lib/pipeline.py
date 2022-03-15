from lh_lib.logging import log
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.exceptions import NoReadableDataException, ConnectionClosedDownException, InvalidDataException, \
    AssignmentException

INPUT_PIPELINE_TIMEOUT_MS = 3000


class AbstractPipeline:

    def __init__(self, pipe_id, time_frame, values_per_time_frame):
        self.conn = None
        self.pipe_id = pipe_id

        # indicates whether both pipeline ends are connected, e.g. actively handle read and write
        # connected is set top down, like the distribution of the assignment -> inputs to outputs
        self.connected = False
        # assignment-initialization is done bottom up (outputs to inputs) to make sure we do not loose values and therefore trigger wrong states
        self.assignment_initialized = False

        self.buffer_in = []
        self.buffer_out = []

        self.time_frame = time_frame
        self.values_per_time_frame = values_per_time_frame

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
            self.invalidate(f'connection closed down: {e}')
        except InvalidDataException as e:
            self.invalidate(f'invalid data: {e}')
        else:
            if isinstance(obj, dict):
                self.handle_control_message(obj)
            else:
                # currently no length check, so ram overflow is possible
                self.buffer_in += obj
                if len(self.buffer_in) > 2000:
                    self.invalidate(f'input buffer length > 2000 : {len(self.buffer_in)}')

    def update_send(self):
        if not self.connected:
            self.buffer_out.clear()
            return

        # if self.buffer_out and (self.time_frame is 0 or ticks_ms_diff_to_current(self.last_time_frame) >= self.time_frame):

        if (self.buffer_out and self.time_frame == 0) or (self.time_frame != 0 and ticks_ms_diff_to_current(self.last_time_frame) >= self.time_frame):
            try:
                self.conn.send(self.buffer_out)
                # log("sending message | len: {}", len(self.buffer_out))
            except ConnectionClosedDownException as e:
                self.invalidate(f'connection closed down: {e}')
            else:
                self.buffer_out.clear()
                self.last_time_frame = ticks_ms()
                self.last_data_exchange = ticks_ms()

    def handle_control_message(self, obj):
        raise Exception(f'This pipeline {type(self)} {self.pipe_id} cannot handle control messages')


class InputPipeline(AbstractPipeline):

    def __init__(self, conn, pipe_id, time_frame, values_per_time_frame):
        super().__init__(pipe_id, time_frame, values_per_time_frame)
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
        super().__init__(pipe_id, 0, 0)

    def activate(self, conn, time_frame, values_per_time_frame):
        self.conn = conn
        self.connected = True

        self.time_frame = time_frame
        self.values_per_time_frame = values_per_time_frame

        self.last_data_exchange = ticks_ms()  # reset because between object creation and being connected can be more than 3 seconds

    def handle_control_message(self, d):
        try:
            message_type = d['type']

            if message_type == 'assignment_initialization':
                self.assignment_initialized = True
            else:
                raise Exception(f'unknown control-message type: {message_type}')
        except Exception as e:
            raise AssignmentException(f'unexpected error during processing pipeline control-message: {type(e)} {e}')
        else:
            try:
                self.conn.send_acknowledgement()
            except ConnectionClosedDownException as e:
                raise AssignmentException(f'remote unexpectedly closed down connection during sending acknowledgement: {type(e)} {e}')


class LocalPipeline(AbstractPipeline):

    def __init__(self, pipe_id):
        super().__init__(pipe_id, 0, 0)
        self.buffer_out = self.buffer_in
        self.connected = True
        self.assignment_initialized = True

    def cleanup(self):
        pass

    def update_recv(self):
        pass

    def update_send(self):
        pass
