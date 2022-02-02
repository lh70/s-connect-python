import socket

from lh_lib.network_stack.connection import Connection


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

        return Connection(client_socket, address)
