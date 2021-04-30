import lh_lib.network

from lh_lib.exceptions import CommunicationException
from lh_lib.logging import log

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

    """
    initialises a server which listens on port x for new connections
    and can serve sensor data provided by the sensor_manager to clients

    port:integer the port to listen to
    sensor_manager:SensorManger a sensor_manager object with containing the initialised sensors
    """
    def __init__(self, port, sensor_manager):
        self._server = lh_lib.network.Server(port)

        self.sensor_manager = sensor_manager

        self.connections = []

    """
    accepts new connections
    updates the sensor_manager and thereby the sensors
    updates the connections
    removes connections on disconnect
    
    to be called regularly
    """
    def update(self):
        # accept any new connection into the pool
        conn = self._server.accept()
        while conn:
            self.connections.append(ServerConnection(conn, self.sensor_manager))
            log("new connection: {} | num connections: {}", conn.address, len(self.connections))
            conn = self._server.accept()

        # update sensor values
        self.sensor_manager.update()

        # update connections
        # order is valid:
        #  sensor data is only used if the sensor is leased
        #  that means a sensor must be updated before updating the connections
        #  and a new lease will only come to effect (read sensor values) on the next iteration
        for connection in self.connections[:]:
            try:
                connection.update()
            except CommunicationException as e:
                connection.send_error(e)
            except lh_lib.network.ConnectionClosedDownException:
                self.connections.remove(connection)
                log("connection closed: {} | num connections: {}", connection.connection.address, len(self.connections))


class ServerConnection:

    """
    represents an individual connection from the server to a client
    wraps the transport layer and provides a reactive json-protocol-layer

    connection:Transport an instance of the Transport class
    sensor_manager:SensorManager the servers sensor_manager to communicate with
    """
    def __init__(self, connection, sensor_manager):
        self.connection = connection
        self.sensor_manager = sensor_manager
        # current task
        self.sensor = None
        self.time_frame = 0
        self.values_per_time_frame = 0
        # update information
        self.last_time_frame = 0
        self.values_to_send = []

    """
    removes a sensors lease on garbage collection -> after connection breakdown
    """
    def __del__(self):
        if self.sensor:
            self.sensor_manager.release_sensor_lease(self.sensor)

    """
    either sends the currently aggregated timeframe of sensor data or
    adds sensor data to the current timeframe or
    does nothing when no sensor is currently requested
    
    and checks if sensor data gets requested
    """
    def update(self):
        # update and maybe send sensor values
        if self.sensor:
            if self._time_frame_expired:
                self.connection.send(self.values_to_send)
                self.values_to_send = []
                self._reset_time_frame()
            else:
                self.values_to_send.append(self.sensor.get())

        # check for new control messages
        # do this last so changed controls affect only the new iteration
        try:
            obj = self.connection.recv()
        except lh_lib.network.NoReadableDataException:
            pass
        else:
            if isinstance(obj, dict):
                if 'sensor' in obj:
                    # if we get a new data request do first abandon the old one
                    if self.sensor:
                        self.sensor_manager.release_sensor_lease(self.sensor)
                    # tell the manager we need new sensor data
                    # raises CommunicationException on wrong sensor name
                    self.sensor = self.sensor_manager.get_sensor_lease(obj['sensor'])
                if 'time-frame' in obj:
                    try:
                        self.time_frame = int(obj['time-frame'])
                    except ValueError as e:
                        raise CommunicationException('wrong value for time-frame: {}'.format(e))
                if 'value-per-time-frame' in obj:
                    try:
                        self.values_per_time_frame = int(obj['values-per-time-frame'])
                    except ValueError as e:
                        raise CommunicationException('wrong value for values-per-time-frame: {}'.format(e))
            else:
                # alternative is list -> data message, but server connections do not process these (yet)
                pass

    """
    checks if the current timeframe has expired
    this is done differently on MicroPython and CPython to be compatible with both
    
    returns a boolean
    """
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

    """
    resets the current timeframe in a MicroPython and CPython compatible manner
    to be called after a timeframe has expired
    """
    def _reset_time_frame(self):
        if RUNNING_MICROPYTHON:
            self.last_time_frame = time.ticks_ms()
        else:
            self.last_time_frame = (time.perf_counter_ns() + 500000) // 1000000

    """
    sends a string serializable object as error message back to the client
    to be used on wrong control messages sent by client for debugging
    
    communication_exception_obj:string serializable object
    """
    def send_error(self, communication_exception_obj):
        self.connection.send({'error': '{}'.format(communication_exception_obj)})


class Client:

    """
    initializes a client which connects to a given host

    host:string a network host identifier
    port:integer the port to connect to on host
    """
    def __init__(self, host, port):
        self.connection = lh_lib.network.Client(host, port)

    """
    issues a sensor request to the server in the compatible format
    """
    def request_data(self, sensor, time_frame=None, values_per_time_frame=None):
        control_obj = {
            'sensor': sensor
        }
        if time_frame is not None:
            control_obj['time-frame'] = time_frame
        if values_per_time_frame is not None:
            control_obj['values-per-time-frame'] = values_per_time_frame

        self.connection.send(control_obj)

    """
    simple data retrieval method which simply returns data or None 
    
    to be called continuously
    """
    def receive_data(self):
        try:
            return self.connection.recv()
        except lh_lib.network.NoReadableDataException:
            pass
