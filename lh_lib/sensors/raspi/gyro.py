from smbus import SMBus

from lh_lib.sensors.sensor import AbstractSensor
from lh_lib.logging import log

MPU6050_ADDRESS = 0x68


class Gyro(AbstractSensor):
    """
    Initialises I2C communication to the gyro sensor.

    I2C setup (one time):
    enable I2C in raspi-config: sudo raspi-config -> Interface Options -> I2C
    reboot: sudo reboot
    install I2C python bindings: sudo apt-get install python3-smbus

    The sensor must be connected using the default I2C GPIO pins (I2C bus 1):
    SDA -> GPIO 2
    SCL -> GPIO 3
    (we do not support I2C bus 0 with GPIO 0 and 1 as they are typically used internally to interact with EEPROM)
        further information about the GPIO: https://pinout.xyz

    The following sensor pins must be connected: VCC, GND, SCL, SDA
    VCC can be 3.3-5V with the GY-521 breakout board (included voltage regulator) (The standalone sensor needs 3.3V)

    Frequency is kept at default 400000Hz which is the maximum rating for the MPU6050 sensor.
    """
    def __init__(self):
        super().__init__()
        self.i2c = SMBus(1)

        # MPU6050 stores 7 different values, with 2 registers == bytes per value
        self.buf = bytearray(14)

        self._init_sensor()

    """
    sets a 14 bytes long array. Every 2 bytes form a valid value.
    Values in order:
    Acceleration X
    Acceleration Y
    Acceleration Z
    Temperature
    Gyro X
    Gyro Y
    Gyro Z
    """
    def update(self):
        try:
            self.buf = self.i2c.read_i2c_block_data(MPU6050_ADDRESS, 0x3B, 14)
        except OSError:
            log("gyro sensor disconnected. reinitializing...")
            self._init_sensor()
            log("done.")
        else:
            self.value = self._convert(self.buf)

    """
    resets the gyro sensor
    """
    def _init_sensor(self):
        # write 0x00 == reset into the register 0x6B
        self.i2c.write_byte_data(MPU6050_ADDRESS, 0x6B, 0x00)

    """
    Utility for later which combines the the 14 bytes into a 7 items long list.
    Temperature is converted to degrees Celsius.
    Acceleration and gyro are not yet converted to g/degrees yet.
    """
    def _convert(self, buf):
        result = []
        for i in range(0, 14, 2):
            val = buf[i] << 8 | buf[i + 1]
            result.append(val if val < 0x8000 else -((65535 - val) + 1))

        result[3] = result[3] / 340 + 36.53

        return result
