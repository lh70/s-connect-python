from lh_lib.communication import Server
from lh_lib.sensors.manage import SensorManager
from lh_lib.logging import log

from lh_lib.sensors.esp32.dummy import Dummy
from lh_lib.sensors.esp32.poti import Poti, ATT3_6V


def run():
    dummy_sensor = Dummy()
    poti_sensor = Poti(32, attenuation=ATT3_6V)

    sensor_manager = SensorManager(dummy_sensor, poti_sensor)

    server = Server(8090, sensor_manager)

    log("Server opened on port 8090")

    while True:
        server.update()


if __name__ == '__main__':
    run()
