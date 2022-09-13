

class AbstractSensor:

    """
    Holds the minimum requirement a sensor has to fulfil
    
    value holds the most recent value generated by the sensor
     -> to be updated by the sensor which must implement an update() method
    """
    def __init__(self):
        self.value = None
        self.start_irq()

    def __del__(self):
        self.stop_irq()

    """
    can be used by the sensor to register interrupt handlers
    """
    def start_irq(self):
        pass

    """
    this method has to be implemented when a sensor implements start_irq() to remove the interrupt handlers
    """
    def stop_irq(self):
        pass
