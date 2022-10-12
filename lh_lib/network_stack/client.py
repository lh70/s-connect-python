import socket

from lh_lib.network_stack.connection import Connection


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

    return Connection(client_socket, (host, port))
