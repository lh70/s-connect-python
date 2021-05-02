from lh_lib.communication import Server
from lh_lib.sensors.manage import SensorManager
from lh_lib.logging import log

from lh_lib.sensors.esp32.dummy import Dummy
from lh_lib.sensors.esp32.poti import Poti, ATT3_6V
from lh_lib.sensors.esp32.hall import Hall
from lh_lib.sensors.esp32.touch import Touch
from lh_lib.sensors.esp32.temperature import Temperature
from lh_lib.sensors.esp32.dht11 import DHT11
from lh_lib.sensors.esp32.gyro import Gyro


def run():
    dummy_sensor = Dummy()
    poti_sensor = Poti(32, attenuation=ATT3_6V)
    hall_sensor = Hall()
    touch_sensor = Touch(35)
    temperature_sensor = Temperature()
    dht11_sensor = DHT11(13)
    gyro_sensor = Gyro()

    sensor_manager = SensorManager(dummy_sensor, poti_sensor, hall_sensor, touch_sensor, temperature_sensor, dht11_sensor, gyro_sensor)

    server = Server(8090, sensor_manager)

    log("Server opened on port 8090")

    while True:
        server.update()


if __name__ == '__main__':
    run()
