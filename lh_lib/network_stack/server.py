import socket

from lh_lib.network_stack.connection import Connection
from lh_lib.constants import RUNNING_MICROPYTHON

if RUNNING_MICROPYTHON:
    from lh_lib.network_stack.wlan import isconnected, reconnect


DEFAULT_PORT = 8090


class Server:
    """
    Initialises a tcp ipv4 stream server which listens for incoming connections

    server_port:integer the port to listen on
    max_connect_requests:integer the maximum requests in pre-accept queue before dismissing connect-requests
    """

    def __init__(self, server_port=DEFAULT_PORT, max_connect_requests=5):
        # a standard ipv4 stream socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # allow immediate rebind to a floating socket (last app crashed or otherwise non fully closed server socket)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind to all interfaces available
        self.socket.bind(('0.0.0.0', server_port))
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
        if RUNNING_MICROPYTHON and not isconnected():
            reconnect()

        try:
            client_socket, address = self.socket.accept()
        except OSError:
            # no new connect request waiting
            return None

        # change to non-blocking mode
        # MicroPython supports only one thread/process and therefore we need to implement everything synchronous
        client_socket.settimeout(0)

        return Connection(client_socket, address)
