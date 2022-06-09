from machine import Pin, ADC

from lh_lib.sensors.sensor import AbstractSensor

ATT1V = ADC.ATTN_0DB
ATT1_3V = ADC.ATTN_2_5DB
ATT2V = ADC.ATTN_6DB
ATT3_6V = ADC.ATTN_11DB


class Poti(AbstractSensor):

    """
    pin:integer          must be in range 32-39 inclusive

    attenuation:constant can be one of ADC.ATTN_0DB/ADC.ATTN_2_5DB/ADC.ATTN_6DB/ADC.ATTN_11DB
                         or one of poti.ATT1V/poti.ATT1_3V/poti.ATT2V/poti.ATT3_6V

                         The poti constants are synonyms and include the approximate mapped voltage range.

                         Important: MAX INPUT PIN RATING: 3.6V -> General good idea: Do not exceed 3.3V

    """
    def __init__(self, pin=32, attenuation=ATT3_6V):
        super().__init__()
        self.adc = ADC(Pin(pin, Pin.IN))
        self.adc.atten(attenuation)

    """
    sets values in range 0-4095
    """
    def update(self):
        self.value = self.adc.read()
