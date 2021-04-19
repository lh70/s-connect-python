from communication import Server
from sensors.manage import SensorManager

from sensors.esp32.dummy import Dummy


def run():
    dummy_sensor = Dummy()

    sensor_manager = SensorManager(dummy_sensor)

    server = Server(8090, sensor_manager)

    while True:
        server.update()


if __name__ == '__main__':
    run()
