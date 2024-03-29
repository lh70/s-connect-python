"""
to be run on a console. starts the framework on a computer with a cpython environment
"""

import os
import sys

try:
    from lh_lib.base.logging import log
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.base.logging import log

from lh_lib.base.network_stack.server import DEFAULT_PORT
from lh_lib.worker import Worker
from lh_lib.sensors.manage import SensorManager
from lh_lib.sensors.esp32.dummy import Dummy


if sys.implementation.name == 'micropython':
    raise Exception("Run this script in a CPython environment, not micropython! (python scripts/run-desktop-worker.py)")


def run():
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = DEFAULT_PORT

    worker = Worker(port, SensorManager(Dummy))

    log('Worker started with port {}'.format(port))

    while True:
        worker.update()


if __name__ == '__main__':
    run()
