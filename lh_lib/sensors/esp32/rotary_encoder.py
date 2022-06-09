from machine import Pin

from lh_lib.sensors.sensor import AbstractSensor


class RotaryEncoder(AbstractSensor):

    communication_name = 'rotary_encoder'

    """
    Reads an incremental rotary encoder.
    The callback functions look bulky, but they take the last state and reachable states in account to reduce jitter.
    
    clk_pin:integer, dt_pin:integer can be one of all available GPIO pins: 0-19, 21-23, 25-27, 32-39
                                    it is NOT recommended to pick one of the following pins: (1, 3) -> serial, (6, 7, 8, 11, 16, 17) -> embedded flash

    scale:float can be any float or integer. 
                Default is 0.5 -> 2 steps per resting state -> states between resting states are also valid states
                0.25 would also be reasonable -> 1 step per resting state
    """
    def __init__(self, clk_pin=34, dt_pin=26, scale=0.5):
        super().__init__()
        self.clk_pin = Pin(clk_pin, Pin.IN)
        self.dt_pin = Pin(dt_pin, Pin.IN)
        self.scale = scale
        self._pos = 0

        self.old_val = None

        self.val_old_clk_pin = self.clk_pin.value()
        self.val_old_dt_pin = self.dt_pin.value()

        # start_irq and stop_irq not used here, as this messes with state,
        # where changes in rotation are only measured if sensor is gets watched
        self.clk_pin.irq(handler=self.clk_callback, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)
        self.dt_pin.irq(handler=self.dt_callback, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

    """
    updates the readout value according to scale. Cuts value to integer, because we want to output whole ticks.
    """
    def update(self):
        self.value = int(self._pos * self.scale)

    """
    callback for clk pin, which only updates valid steps for the clk pin.
    
    this means:
        one step is only done once
        only steps which are reachable from the last step will happen
        only steps which are reachable from this pin changing state will happen
        
    this removes nearly all jitter.
    """
    def clk_callback(self, pin):
        clk_val = pin.value()
        dt_val = self.dt_pin.value()

        if self.val_old_clk_pin:
            if self.val_old_dt_pin:

                if not clk_val:
                    if dt_val:
                        self._pos += 1  # TT -> FT
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
            else:

                if not clk_val:
                    if not dt_val:
                        self._pos -= 1  # FF <- TF
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val

        else:
            if self.val_old_dt_pin:

                if clk_val:
                    if dt_val:
                        self._pos -= 1  # TT <- FT
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
            else:

                if clk_val:
                    if not dt_val:
                        self._pos += 1  # FF -> TF
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val

    """
    callback for dt pin, which only updates valid steps for the dt pin.
    
    this means:
        one step is only done once
        only steps which are reachable from the last step will happen
        only steps which are reachable from this pin changing state will happen
        
    this removes nearly all jitter.
    """
    def dt_callback(self, pin):
        clk_val = self.clk_pin.value()
        dt_val = pin.value()

        if self.val_old_clk_pin:
            if self.val_old_dt_pin:

                if clk_val:
                    if not dt_val:
                        self._pos -= 1  # TF <- TT
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
            else:

                if clk_val:
                    if dt_val:
                        self._pos += 1  # TF -> TT
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val

        else:
            if self.val_old_dt_pin:

                if not clk_val:
                    if not dt_val:
                        self._pos += 1  # FT -> FF
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
            else:

                if not clk_val:
                    if dt_val:
                        self._pos -= 1  # FT <- FF
                        self.val_old_clk_pin, self.val_old_dt_pin = clk_val, dt_val
