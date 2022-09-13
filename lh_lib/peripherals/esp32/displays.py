from micropython import const
from machine import Pin, SoftI2C

from lh_lib.included_submodules_files.ssd1306 import SSD1306_I2C
from lh_lib.included_submodules_files.esp32_gpio_lcd import GpioLcd


class SSD1306(SSD1306_I2C):

    WIDTH = const(128)
    HEIGHT = const(64)

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
        # rst pin powers the display
        if rst != -1:
            self.rst = Pin(rst, Pin.OUT)
            self.rst.value(1)

        i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
        super().__init__(SSD1306.WIDTH, SSD1306.HEIGHT, i2c)

    def __del__(self):
        self.rst.value(0)


class ESP32GpioLcd(GpioLcd):

    """
    We do not need a special wrapper behavior yet and simply expose the provided API

    Initialises a lcd display output with gpio communication

    pin:Pin(integer) can be one of the following GPIO pins: 0-19, 21-23, 25-27, 32-33
                it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash
                34-39 cannot be used because they are input only

    LCD pins:
    VSS/GND -> ground
    VDD/VCC -> 5 volts
    V0 -> display contrast setting, ground==max-contrast (0.5V seems like a solid contrast setting), options are:
        potentiometer(GND,V0,5V)
        a fixed voltage via a voltage-divider
        todo: adc pin to set a voltage -> add this as a init option
    RS -> register select, selects which registers are written
    RW -> read/write, ground
    E -> enable, enables/disables writing the registers
    (D0-D3 -> second 4 data bits, can be connected for double the update rate)
    D4-D7 -> first 4 data bits, must be connected. On 4 Pin mode the 8 ascii data bits are split and send serially
    A -> anode, 5 volts, for lcd display to work
    K -> cathode, ground, for lcd display to work
    """
    pass
