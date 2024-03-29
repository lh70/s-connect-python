"""
NOT THE START SCRIPT FOR THE COMPUTER FRAMEWORK VERSION.

Only works if transferred to the esp32 running
micropython with for example: mpremote fs cp main.py :main.py

Micropython supports two scripts automatically. boot.py is run first as a setup script. main.py is run second for
program logic that should be run on micropython start (which is on poweron, or the EN button)
"""

import sys
import gc
import time

from lh_lib.base.constants import RUNNING_MICROPYTHON

if not RUNNING_MICROPYTHON:
    raise Exception("This is the ESP32-main-script that gets executed on startup. It needs to be copied to the esp32 root directory if you want the framework to be run automatically on startup.")


from lh_lib.base.logging import log
from lh_lib.base.network_stack.server import DEFAULT_PORT
from lh_lib.base.network_stack.wlan import isconnected, reconnect


if __name__ == '__main__':
    try:
        from lh_lib.worker import Worker
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

        # other lib files must be directly accessible via python-path
        if '/lh_lib/included_submodules_files' not in sys.path:
            sys.path.insert(1, '/lh_lib/included_submodules_files')

        # if wlan disconnected after boot script, reconnect
        if not isconnected():
            reconnect()

        sensor_manager = SensorManager(Dummy, Poti, Hall, Touch, Temperature, DHT11, Gyro, Ultrasonic, RotaryEncoder, CO2, Button)

        worker = Worker(DEFAULT_PORT, sensor_manager)
        log('Worker started with port {}'.format(DEFAULT_PORT))
    except ImportError:
        from lh_lib.base.base_worker import Worker

        worker = Worker(DEFAULT_PORT)
        log('Base Worker started with port {}'.format(DEFAULT_PORT))

    while True:
        worker.update()
        # gc.collect()
        # print("free: {}, used: {}".format(gc.mem_free(), gc.mem_alloc()))
        # time.sleep(1)
