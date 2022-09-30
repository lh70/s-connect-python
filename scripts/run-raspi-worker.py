"""
to be run on a console. starts the framework on a raspberry pi
"""

import os
import sys

try:
    from lh_lib.logging import log
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.logging import log

from lh_lib.network_stack.server import DEFAULT_PORT
from lh_lib.worker import Worker
from lh_lib.sensors.manage import SensorManager
from lh_lib.sensors.raspi.button import Button
from lh_lib.sensors.raspi.dummy import Dummy
from lh_lib.sensors.raspi.gyro import Gyro
from lh_lib.sensors.raspi.co2 import CO2
from lh_lib.sensors.raspi.rotary_encoder import RotaryEncoder
from lh_lib.sensors.raspi.touch import Touch
from lh_lib.constants import PLATFORMS, PLATFORM


if PLATFORM != PLATFORMS.RASPBERRYPI:
    raise Exception("Please run this script on a Raspberry Pi!")


def run():
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = DEFAULT_PORT

    worker = Worker(port, SensorManager(Button, Dummy, Gyro, CO2, RotaryEncoder, Touch))

    log(f'Worker started with port {port}')

    while True:
        worker.update()


if __name__ == '__main__':
    run()
