import esp32


class Hall:

    """
    returns and integer of range +- unknown representing the current internal hall sensor reading
    """
    def get(self):
        return esp32.hall_sensor()
