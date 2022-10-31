"""
to be run on an esp32 with mpremote run ... . Starts the framework on micropython.
"""
import sys

if not sys.implementation.name == 'micropython':
    raise Exception("Call this script on the microcontroller directly! (mpremote run scripts/run-micropython-worker.py)")

from lh_lib.worker import Worker
from lh_lib.base.logging import log
from lh_lib.sensors.manage import SensorManager
from lh_lib.sensors.esp32.dummy import Dummy
from lh_lib.sensors.esp32.poti import Poti, ATT3_6V
from lh_lib.sensors.esp32.hall import Hall
from lh_lib.sensors.esp32.touch import Touch
from lh_lib.sensors.esp32.temperature import Temperature
from lh_lib.sensors.esp32.dht11 import DHT11
from lh_lib.sensors.esp32.gyro import Gyro
from lh_lib.sensors.esp32.ultrasonic import Ultrasonic
from lh_lib.sensors.esp32.rotary_encoder import RotaryEncoder
from lh_lib.sensors.esp32.co2 import CO2
from lh_lib.sensors.esp32.button import Button
from lh_lib.base.network_stack.server import DEFAULT_PORT
from lh_lib.base.network_stack.wlan import isconnected, reconnect


def run():
    # other lib files must be directly accessible via python-path
    if '/lh_lib/included_submodules_files' not in sys.path:
        sys.path.insert(1, '/lh_lib/included_submodules_files')

    # if wlan disconnected after boot script, reconnect
    if not isconnected():
        reconnect()

    sensor_manager = SensorManager(Dummy, Poti, Hall, Touch, Temperature, DHT11, Gyro, Ultrasonic, RotaryEncoder, CO2, Button)

    worker = Worker(DEFAULT_PORT, sensor_manager)

    log('Worker started with port {}'.format(DEFAULT_PORT))

    while True:
        worker.update()


if __name__ == '__main__':
    run()
