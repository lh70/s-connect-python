from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.exceptions import NoReadableDataException, ConnectionClosedDownException, InvalidDataException, AcknowledgementException

try:
    import usocket as socket
except ImportError:
    import socket

try:
    import ustruct as struct
except ImportError:
    import struct

try:
    import ujson as json
except ImportError:
    import json

try:
    import usys as sys
except ImportError:
    import sys

# general maximum for an 32bit unsigned integer value
MAX_UNSIGNED_INT = 4294967295
# maximum receive network buffer
MAX_RECEIVE_BYTES = 4096
# acknowledgement timeout
ACKNOWLEDGEMENT_TIMEOUT_MS = 2000

class Server:

    """
    Initialises a tcp ipv4 stream server which listens for incoming connections

    server_port:integer the port to listen on
    max_connect_requests:integer the maximum requests in pre-accept queue before dismissing connect-requests
    """
    def __init__(self, server_port, max_connect_requests=5):
        # a standard ipv4 stream socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind to all interfaces available
        self.socket.bind(('', server_port))
        # We will accept a maximum of x connect requests into our connect queue before we are busy
        # A connection gets out of this queue on socket creation
        self.socket.listen(max_connect_requests)
        # change to non-blocking mode
        # MicroPython supports only one thread/process and therefore we need to implement everything synchronous
        self.socket.settimeout(0)

    """
    Accepts new connect-requests if available and returns an instance of this projects own transport-protocol wrapped socket
    
    To be called in regularly intervals
    """
    def accept(self):
        try:
            client_socket, address = self.socket.accept()
        except OSError:
            # no new connect request waiting
            return None

        # change to non-blocking mode
        # MicroPython supports only one thread/process and therefore we need to implement everything synchronous
        client_socket.settimeout(0)

        return Transport(client_socket, address)


# creates a client socket with this projects own transport-protocol wrapped socket
# raises OSError on connect-timeout
def Client(host, port):
    # create a standard ipv4 stream socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to server
    # this will raise an error when it cannot be completed
    client_socket.connect((host, port))
    # change to non-blocking mode
    # only do this after a successful connect so we take advantage of the timeout handling on blocking sockets
    # MicroPython supports only one thread/process and therefore we need to implement everything synchronous
    client_socket.settimeout(0)

    return Transport(client_socket, (host, port))


class Transport:

    length_struct_fmt = '!I'
    length_struct_size = struct.calcsize(length_struct_fmt)

    """
    initialises with a connected socket and exposes methods to send and receive data with this projects own protocol
    """
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address

    """
    sends a json-serializable object trough the socket
    returns only after the message is sent completely
    
    raises ValueError on non json-serializable objects
    raises ValueError on non utf-8 encodable json-strings
    raises ConnectionClosedDownException if the message could not be sent due to a connection breakdown
    
    obj:Object any json-serializable object
    """
    def send(self, obj):
        # raises ValueError, but is unrecoverable so raise it
        msg = json.dumps(obj)
        # should raise no error -> if it does fix it or maybe use msg.encode('utf-8', 'replace')
        msg = msg.encode('utf-8')
        # should never be the case -> max == 4GB, but just in case we can split the message
        # in the rare rare case when length == MAX_UNSIGNED_INT we send an additional message with length 0
        # this is unavoidable if we want to keep it simple on the receiving socket
        while len(msg) >= MAX_UNSIGNED_INT:
            # send the maximum our length identifier can represent
            self._send_with_length(msg[:MAX_UNSIGNED_INT])
            # save the rest for the next iteration
            msg = msg[MAX_UNSIGNED_INT:]
        # send the rest which is smaller than our maximum length
        self._send_with_length(msg)

    """
    preambles the message with a length identifier
    length can not be bigger than a maximum 32bit unsigned integer -> 4294967295
    """
    def _send_with_length(self, msg):
        self._send_over_socket(struct.pack(self.length_struct_fmt, len(msg)))
        self._send_over_socket(msg)

    """
    sends the actual bytes
    does not return until the message is fully sent
    """
    def _send_over_socket(self, msg):
        bytes_to_send = len(msg)
        while bytes_to_send > 0:
            try:
                bytes_sent = self.socket.send(msg)
            # Windows behaviour??? If other end is forcibly closed it raises an ConnectionResetError -> OSError
            except OSError:
                raise ConnectionClosedDownException()
            # on 0 bytes sent the socket connection is closed
            if bytes_sent == 0:
                raise ConnectionClosedDownException()
            # update the message and length to send
            msg = msg[bytes_sent:]
            bytes_to_send -= bytes_sent

    """
    receives at maximum a given amount of bytes
    
    actually reverses the socket behaviour in raising en error on connection close
    and returning the received bytes on a successful read, even if there was nothing to read
    
    returns bytes
    """
    def _recv_over_socket(self, bytes):
        try:
            buf = self.socket.recv(bytes)
        # if a non blocking read fails we have read everything there is to read at the moment
        except OSError:
            return b''

        # on 0 bytes received the socket connection is closed
        if len(buf) == 0:
            raise ConnectionClosedDownException()

        return buf

    """
    receives a message fully or 
    raises a NoReadableDataException if no data was available or
    raises a ConnectionClosedDownException if the connection closed down
    
    on actual receive this method blocks potentially forever
    
    returns bytes
    """
    def _recv_with_length(self):
        msg = self._recv_over_socket(self.length_struct_size)

        # empty message means no data could be received
        if len(msg) == 0:
            raise NoReadableDataException()

        # else we need the message length
        # this can take time as we ignore the mass of empty (not ready) messages we can receive
        while len(msg) < self.length_struct_size:
            msg += self._recv_over_socket(self.length_struct_size - len(msg))

        # unpack the length and receive the rest of the message
        # unpack returns always a tuple, which in our case contains only one item
        length = struct.unpack(self.length_struct_fmt, msg)[0]

        # this can take time as we ignore the mass of empty (not ready) messages we can receive
        msg = self._recv_over_socket(min(length, MAX_RECEIVE_BYTES))
        while len(msg) < length:
            msg += self._recv_over_socket(min(length - len(msg), MAX_RECEIVE_BYTES))

        return msg

    """
    receives a full message or 
    raises a NoReadableDataException on no new data available or
    raises a ConnectionClosedDownException
    
    returns an deserialized json object
    """
    def recv(self):
        # this should only raise NoReadableDataException or ConnectionClosedDownException
        msg = buf = self._recv_with_length()
        # if we hit max length identifier the message got split
        # so we read until the current split message is smaller than MAX_UNSIGNED_INT
        # this also accounts for exactly MAX_UNSIGNED_INT from where an empty message == smaller than MAX_UNSIGNED_INT must be received
        while len(buf) >= MAX_UNSIGNED_INT:
            try:
                buf = self._recv_with_length()
                msg += buf
            # we ignore the NoReadableDataException because we know the message is not received fully yet
            # this means this can take time as we ignore no-data-available messages
            except NoReadableDataException:
                pass
        try:
            # this can raise an exception if the received data is not valid utf-8
            msg = msg.decode('utf-8')
            # this can raise an exception if the received data is not valid json
            return json.loads(msg)
        except ValueError:
            raise InvalidDataException()

    def send_acknowledgement(self):
        self.send({'ack': 1})

    def recv_acknowledgement(self):
        timestamp = ticks_ms()
        while ticks_ms_diff_to_current(timestamp) < ACKNOWLEDGEMENT_TIMEOUT_MS:
            try:
                msg = self.recv()
                assert msg['ack'] == 1
                return
            except NoReadableDataException:
                pass
            except Exception as e:
                raise AcknowledgementException("ack failed: {}".format(e))

        raise AcknowledgementException("timeout on receiving acknowledgement")
