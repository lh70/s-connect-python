from machine import I2C
from micropython import const

from sensors.sensor import AbstractSensor

MPU6050_ADDRESS = const(0x68)


class Gyro(AbstractSensor):

    communication_name = 'gyro'

    """
    Initialises I2C with one of the default hardware I2C peripherals:
    0 -> scl_pin:18, sda_pin:19
    1 -> scl_pin:25, sda_pin:26

    Comments:
    Other pins are possible, but sticking to the default pins allows for multiple I2C devices without advanced configuration.
    Frequency is also kept at default 400000Hz which is the maximum rating for the MPU6050 sensor.
    """
    def __init__(self, hw_i2c=0):
        super().__init__()
        self.i2c = I2C(hw_i2c)

        # MPU6050 stores 7 different values, with 2 registers == bytes per value
        self.value = bytearray(14)

        # write 0x00 == reset into the register 0x6B
        self.i2c.writeto_mem(MPU6050_ADDRESS, 0x6B, b'\x00')

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
        self.i2c.readfrom_mem_into(MPU6050_ADDRESS, 0x3B, self.value)

    """
    Utility for later which combines the the 14 bytes into a 7 items long integer list
    """
    def _to_int_list(self, buf):
        return [buf[i] << 8 | buf[i+1] for i in range(0, 14, 2)]
