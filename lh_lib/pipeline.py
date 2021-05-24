from lh_lib.logging import log
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.exceptions import NoReadableDataException, ConnectionClosedDownException, InvalidDataException

INPUT_PIPELINE_TIMEOUT_MS = 3000


class PipelineConnection:

    def __init__(self, conn, pipe_id, time_frame, values_per_time_frame, is_output, valid=True):
        self.conn = conn
        self.pipe_id = pipe_id
        self.is_output = is_output

        self.valid = valid

        self.buffer_in = []
        self.buffer_out = []

        self.time_frame = time_frame
        self.values_per_time_frame = values_per_time_frame

        self.last_time_frame = 0

        self.last_data_receive = ticks_ms()

    def invalidate(self, reason):
        self.conn.socket.close()
        log("invalidating pipeline connection: {} | pipe_id: {} | reason: {} | lost output buffer of length: {}", self.conn.address, self.pipe_id, reason, len(self.buffer_out))
        self.conn = None
        self.buffer_in = []
        self.buffer_out = []
        self.valid = False

    def update_recv(self):
        if not self.valid:
            return

        try:
            obj = self.conn.recv()
            # log("receiving message | len: {}", len(obj))
            self.last_data_receive = ticks_ms()
        except NoReadableDataException:
            if not self.is_output and ticks_ms_diff_to_current(self.last_data_receive) > INPUT_PIPELINE_TIMEOUT_MS:
                self.invalidate("no data received for more than {} milliseconds".format(INPUT_PIPELINE_TIMEOUT_MS))
        except ConnectionClosedDownException as e:
            self.invalidate("connection closed down: {}".format(e))
        except InvalidDataException as e:
            self.invalidate("invalid data: {}".format(e))
        else:
            if isinstance(obj, dict):
                self.handle_control_message(obj)
            else:
                # currently no length check, so ram overflow is possible
                self.buffer_in += obj
                if len(self.buffer_in) > 2000:
                    self.invalidate("input buffer length > 2000 : {}".format(len(self.buffer_in)))

    def update_send(self):
        if not self.valid or not self.is_output:
            return

        if self.time_frame == 0 or ticks_ms_diff_to_current(self.last_time_frame) >= self.time_frame:
            try:
                self.conn.send(self.buffer_out)
                # log("sending message | len: {}", len(self.buffer_out))
            except ConnectionClosedDownException as e:
                self.invalidate("connection closed down: {}".format(e))
            else:
                self.buffer_out.clear()
                self.last_time_frame = ticks_ms()

    def handle_control_message(self, obj):
        raise Exception("cannot process control message on pipeline")


class PrintPipeline:

    def __init__(self, pipe_id, time_frame, values_per_time_frame):
        self.pipe_id = pipe_id
        self.time_frame = time_frame
        self.values_per_time_frame = values_per_time_frame

        self.valid = True

        self.buffer_out = []

        self.last_time_frame = 0

    def update_recv(self):
        pass

    def update_send(self):
        if self.time_frame == 0 or ticks_ms_diff_to_current(self.last_time_frame) >= self.time_frame:
            print(self.buffer_out)
            self.buffer_out.clear()
            self.last_time_frame = ticks_ms()
