from micropython import alloc_emergency_exception_buf

from v1.communication import Server
from lh_lib.sensors.manage import SensorManager
from lh_lib.logging import log

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

alloc_emergency_exception_buf(100)


def run():
    dummy_sensor = Dummy()
    poti_sensor = Poti(32, attenuation=ATT3_6V)
    hall_sensor = Hall()
    touch_sensor = Touch(35)
    temperature_sensor = Temperature()
    dht11_sensor = DHT11(13)
    #gyro_sensor = Gyro()
    ultrasonic_sensor = Ultrasonic(25, 33)
    rotary_encoder_sensor = RotaryEncoder(34, 26)
    co2_sensor = CO2(27)
    button_sensor = Button(14)

    sensor_manager = SensorManager(dummy_sensor, poti_sensor, hall_sensor, touch_sensor, temperature_sensor, dht11_sensor, ultrasonic_sensor, rotary_encoder_sensor, co2_sensor, button_sensor)

    server = Server(8090, sensor_manager)

    log("Server opened on port 8090")

    while True:
        server.update()


if __name__ == '__main__':
    run()
