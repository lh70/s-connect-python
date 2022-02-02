from lh_lib.exceptions import ConnectionClosedDownException

# maximum receive network buffer
MAX_RECEIVE_BYTES = 4096


class BufferedSocket:

    def __init__(self, socket):
        self._socket = socket
        self.input = b''
        self.output = b''

    def read(self, length):
        self._update()
        if len(self.input) >= length:
            result = self.input[:length]
            self.input = self.input[length:]
            return result

    def send(self, byte_string):
        self.output += byte_string
        self._update()

    def _update(self):
        while True:
            try:
                buf = self._socket.recv(MAX_RECEIVE_BYTES)
            # if a non blocking read fails we have read everything there is to read at the moment
            except OSError:
                break
            else:
                # on 0 bytes received the socket connection is closed
                if len(buf) == 0:
                    raise ConnectionClosedDownException()

                # add received bytes to buffer
                self.input += buf

        while len(self.output) > 0:
            try:
                bytes_sent = self._socket.send(self.output)
            # Windows behaviour??? If other end is forcibly closed it raises an ConnectionResetError -> OSError
            except OSError as e:
                if e.args[0] == 11:
                    # EAGAIN Error was raised, which states "try again",
                    # but really means that you probably did not call receive on the socket for a long time.
                    # Do this, even if you do not expect to receive anything.
                    raise ConnectionClosedDownException(
                        "EAGAIN: {} was raised. When was the last time you called receive on this socket?", e)
                else:
                    raise ConnectionClosedDownException(e)
            else:
                # on 0 bytes sent the socket connection is closed
                if bytes_sent == 0:
                    raise ConnectionClosedDownException("0 bytes")
                # update the message and length to send
                self.output = self.output[bytes_sent:]
