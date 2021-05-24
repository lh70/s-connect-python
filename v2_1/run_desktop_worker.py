try:
    import usys as sys
except ImportError:
    import sys

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if not RUNNING_MICROPYTHON:
    import os
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))


from lh_lib.worker import Worker
from lh_lib.logging import log
from lh_lib.sensors.manage import SensorManager


def run():
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 8090

    worker = Worker(port, SensorManager())

    log("Worker started")

    while True:
        worker.update()


if __name__ == '__main__':
    run()
