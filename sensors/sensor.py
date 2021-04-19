

class AbstractSensor:

    def __init__(self):
        self.leases = 0
        self.value = 0

    def get(self):
        return self.value
