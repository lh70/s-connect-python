try:
    import usys as sys
except ImportError:
    import sys

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if not RUNNING_MICROPYTHON:
    import os
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))

from communication import Client


def run():
    # client = Client('192.168.2.200', 8090)
    client = Client('192.168.2.177', 8090)
    # client = Client('127.0.0.1', 8090)

    client.request_data('rotary_encoder', 100)

    while True:
        data = client.receive_data()
        if data is not None:
            print("len: {} | {}".format(len(data), data), flush=True)


if __name__ == '__main__':
    run()
