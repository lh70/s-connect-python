import json
import struct

from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.exceptions import NoReadableDataException, InvalidDataException, AcknowledgementException
from lh_lib.network_stack.buffered_socket import BufferedSocket

# general maximum for an 32bit unsigned integer value
MAX_UNSIGNED_INT = 4294967295
# acknowledgement timeout
ACKNOWLEDGEMENT_TIMEOUT_MS = 7000

LENGTH_STRUCT = '!I'
LENGTH_STRUCT_LENGTH = struct.calcsize(LENGTH_STRUCT)


class Connection:

    def __init__(self, socket, address):
        self.address = address
        self._buffered_socket = BufferedSocket(socket)

        self._receive_length = None
        self._receive_message = b''

    def send(self, message):
        # raises ValueError, but is unrecoverable so raise it
        msg = json.dumps(message)
        # should raise no error -> if it does fix it or maybe use msg.encode('utf-8', 'replace')
        msg = msg.encode('utf-8')
        # should never be the case -> max == 4GB, but just in case we can split the message
        # in the rare rare case when length == MAX_UNSIGNED_INT we send an additional message with length 0
        # this is unavoidable if we want to keep it simple on the receiving socket
        while len(msg) >= MAX_UNSIGNED_INT:
            # send the maximum our length identifier can represent
            self._buffered_socket.send(struct.pack(LENGTH_STRUCT, MAX_UNSIGNED_INT))
            self._buffered_socket.send(msg[:MAX_UNSIGNED_INT])
            # save the rest for the next iteration
            msg = msg[MAX_UNSIGNED_INT:]
        # send the rest which is smaller than our maximum length
        self._buffered_socket.send(struct.pack(LENGTH_STRUCT, len(msg)))
        self._buffered_socket.send(msg)

    def receive(self):
        while True:
            if self._receive_length is None:
                byte_string = self._buffered_socket.read(LENGTH_STRUCT_LENGTH)
                if byte_string is not None:
                    self._receive_length = struct.unpack(LENGTH_STRUCT, byte_string)[0]
                else:
                    raise NoReadableDataException()
            elif self._receive_length == MAX_UNSIGNED_INT:
                byte_string = self._buffered_socket.read(MAX_UNSIGNED_INT)
                if byte_string is not None:
                    self._receive_message += byte_string
                    self._receive_length = None
                else:
                    raise NoReadableDataException()
            else:
                byte_string = self._buffered_socket.read(self._receive_length)
                if byte_string is not None:
                    self._receive_length = None

                    message = self._receive_message + byte_string

                    try:
                        # this can raise an exception if the received data is not valid utf-8
                        message = message.decode('utf-8')
                        # this can raise an exception if the received data is not valid json
                        return json.loads(message)
                    except ValueError:
                        raise InvalidDataException()
                else:
                    raise NoReadableDataException()

    def send_acknowledgement(self):
        self.send({'ack': 1})

    def recv_acknowledgement(self):
        timestamp = ticks_ms()
        while ticks_ms_diff_to_current(timestamp) < ACKNOWLEDGEMENT_TIMEOUT_MS:
            try:
                message = self.receive()
                if message is not None:
                    assert message['ack'] == 1
                    return
            except Exception as e:
                raise AcknowledgementException("ack failed: {}".format(e))

        raise AcknowledgementException("timeout on receiving acknowledgement")
