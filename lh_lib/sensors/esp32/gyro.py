from machine import Pin, SoftI2C
from micropython import const

from lh_lib.sensors.sensor import AbstractSensor
from lh_lib.base.logging import log

MPU6050_ADDRESS = const(0x68)


class Gyro(AbstractSensor):

    """
    Initialises I2C communication to the gyro sensor.

    The following sensor pins must be connected: VCC, GND, SCL, SDA
    VCC can be 3.3-5V with the GY-521 breakout board (included voltage regulator) (The standalone sensor needs 3.3V)
    
    sda/scl:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
    
    Frequency is kept at default 400000Hz which is the maximum rating for the MPU6050 sensor.
    """
    def __init__(self, sda=21, scl=22):
        super().__init__()
        self.i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))

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
            self.i2c.readfrom_mem_into(MPU6050_ADDRESS, 0x3B, self.buf)
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
        self.i2c.writeto_mem(MPU6050_ADDRESS, 0x6B, bytearray(1))

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
