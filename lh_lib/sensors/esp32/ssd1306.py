from micropython import const
from machine import Pin, SoftI2C

from lh_lib.sensors.sensor import AbstractSensor
from lh_lib.sensors.esp32.util.ssd1306 import SSD1306_I2C


WIDTH = const(128)
HEIGHT = const(64)


class SSD1306(AbstractSensor):
    communication_name = 'display'

    """
    Initialises a ssd1306 display output with I2C communication

    sda/scl:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
                
    for the esp32 lora + oled development board the configuration is as follows:
        sda: 4, scl: 15, rst: 16
    for newer esp32 lora + oled development boards the configuration might be:
        sda: 21, scl: 22, rst: -1
    
    rst=-1 if there is no rst pin connected
    """

    def __init__(self, sda=4, scl=15, rst=16):
        super().__init__()

        # rst pin powers the display
        if rst != -1:
            rst = Pin(rst, Pin.OUT)
            rst.value(1)

        i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
        self.display = SSD1306_I2C(WIDTH, HEIGHT, i2c)

    """
    update method needs rework
    """

    def update(self):
        self.display.text('Hello, World!', 0, 0, 1)
        self.display.show()
