from machine import Pin

from lh_lib.sensors.sensor import AbstractSensor


class RotaryEncoder(AbstractSensor):

    communication_name = 'rotary_encoder'

    """
    Reads an incremental rotary encoder.
    This implementation is very simple and not accurate.
    Needs additional logic or filtering to account for jitter.
    
    clk_pin:integer, dt_pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                                    it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash

    scale:float can be any float or integer. 
                Default is 0.25 because one tick in any direction ideally triggers both interrupts two times.
    """
    def __init__(self, clk_pin, dt_pin, scale=0.25):
        super().__init__()
        self.clk_pin = Pin(clk_pin, Pin.IN)
        self.dt_pin = Pin(dt_pin, Pin.IN)
        self.forward = True
        self.scale = scale
        self._pos = 0
        self.clk_interrupt = self.clk_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.clk_callback)
        self.dt_interrupt = self.dt_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.dt_callback)

    """
    updates the readout value according to scale. Cuts value to integer, because we want to output whole ticks.
    """
    def update(self):
        self.value = int(self._pos * self.scale)

    """
    callback for the clk pin interrupt
    """
    def clk_callback(self, pin):
        self.forward = self.clk_pin.value() ^ self.dt_pin.value()
        self._pos += 1 if self.forward else -1

    """
    callback for the dt pin interrupt
    """
    def dt_callback(self, pin):
        self.forward = self.clk_pin.value() ^ self.dt_pin.value() ^ 1
        self._pos += 1 if self.forward else -1
