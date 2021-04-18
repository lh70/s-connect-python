import esp32


class Temperature:

    """
    returns the internal temperature sensor reading in Fahrenheit as an integer
    """
    def get(self):
        return esp32.raw_temperature()
