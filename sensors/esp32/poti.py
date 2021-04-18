from machine import ADC
from micropython import const

ATT1V = const(ADC.ATTN_0DB)
ATT1_3V = const(ADC.ATTN_2_5DB)
ATT2V = const(ADC.ATTN_6DB)
ATT3_6V = const(ADC.ATTN_11DB)


class Poti:

    communication_name = 'poti'

    """
    pin:integer          must be in range 32-39 inclusive

    attenuation:constant can be one of ADC.ATTN_0DB/ADC.ATTN_2_5DB/ADC.ATTN_6DB/ADC.ATTN_11DB
                         or one of poti.ATT1V/poti.ATT1_3V/poti.ATT2V/poti.ATT3_6V

                         The poti constants are synonyms and include the approximate mapped voltage range.

                         Important: MAX INPUT PIN RATING: 3.6V -> General good idea: Do not exceed 3.3V

    """
    def __init__(self, pin, attenuation=ATT1V):
        ADC.atten(attenuation)
        self.adc = ADC(pin)

    """
    returns values in range 0-4095
    """
    def get(self):
        return self.adc.read()
