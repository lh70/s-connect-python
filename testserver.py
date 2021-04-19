from lh_lib.communication import Server
from lh_lib.sensors.manage import SensorManager

from lh_lib.sensors.esp32.dummy import Dummy


def run():
    dummy_sensor = Dummy()

    sensor_manager = SensorManager(dummy_sensor)

    server = Server(8090, sensor_manager)

    while True:
        server.update()


if __name__ == '__main__':
    run()
