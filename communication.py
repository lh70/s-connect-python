import network

try:
    import usys as sys
except ImportError:
    import sys

try:
    import utime as time
except ImportError:
    import time

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'


class Server:

    def __init__(self, port, *sensors):
        self._server = network.Server(port)

        self.sensors = {s.communication_name: s for s in sensors}

        self.connections = []

    def update(self):
        conn = self._server.accept()
        while conn:
            self.connections.append(ServerConnection(conn, self.sensors))
            conn = self._server.accept()

        for connection in self.connections[:]:
            try:
                connection.update()
            except CommunicationException as e:
                connection.send_error(e)
            except network.ConnectionClosedDownException:
                self.connections.remove(connection)


class ServerConnection:

    def __init__(self, connection, sensors):
        self.connection = connection
        self.sensors = sensors
        # current task
        self.sensor = None
        self.time_frame = 0
        self.values_per_time_frame = 0
        # update information
        self.last_time_frame = 0
        self.values_to_send = []

    def update(self):
        # check for new control messages
        try:
            obj = self.connection.recv()
        except network.NoReadableDataException:
            pass
        else:
            if isinstance(obj, dict):
                if 'sensor' in obj and obj['sensor'] in self.sensors:
                    self.sensor = self.sensors[obj['sensor']]
                if 'time-frame' in obj:
                    try:
                        self.time_frame = int(obj['time-frame'])
                    except ValueError as e:
                        raise CommunicationException('wrong value for time-frame: '.format(e))
                if 'value-per-time-frame' in obj:
                    try:
                        self.values_per_time_frame = int(obj['values-per-time-frame'])
                    except ValueError as e:
                        raise CommunicationException('wrong value for values-per-time-frame: '.format(e))
            else:
                # alternative is list -> data message, but server connections do not process these (yet)
                pass
        # update and maybe send sensor values
        if self.sensor:
            if self._time_frame_expired:
                self.connection.send(self.values_to_send)
                self.values_to_send = []
                self._reset_time_frame()
            else:
                self.values_to_send.append(self.sensor.get())

    @property
    def _time_frame_expired(self):
        if self.time_frame == 0:
            return len(self.values_to_send) > 0

        if RUNNING_MICROPYTHON:
            # on MicroPython we take the wrap around ticks which are faster
            return time.ticks_diff(time.ticks_ms(), self.last_time_frame) >= self.time_frame
        else:
            # on CPython we cannot use ticks, but it is assumed fast enough to use time_ns()
            # time_ns() is converted to milliseconds with rounding using only integer arithmetic
            return (time.perf_counter_ns() + 500000) // 1000000 - self.last_time_frame >= self.time_frame

    def _reset_time_frame(self):
        if RUNNING_MICROPYTHON:
            self.last_time_frame = time.ticks_ms()
        else:
            self.last_time_frame = (time.perf_counter_ns() + 500000) // 1000000

    def send_error(self, communication_exception_obj):
        self.connection.send({'error': '{}'.format(communication_exception_obj)})


class Client:

    def __init__(self, host, port):
        self.connection = network.Client(host, port)

    def request_data(self, sensor, time_frame=None, values_per_time_frame=None):
        control_obj = {
            'sensor': sensor
        }
        if time_frame is not None:
            control_obj['time-frame'] = time_frame
        if values_per_time_frame is not None:
            control_obj['values-per-time-frame'] = values_per_time_frame

        self.connection.send(control_obj)

    def receive_and_print_data(self):
        try:
            data = self.connection.recv()
        except network.NoReadableDataException:
            pass
        else:
            print(len(data), flush=True)


class CommunicationException(Exception):
    pass
