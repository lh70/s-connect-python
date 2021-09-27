import os

ACTIVE = True


# Simple wrapper to be able to silence the program for increased performance on MicroPython
def log(msg, *objects):
    if ACTIVE:
        print(str(msg).format(*objects))


class DataLogger:

    def __init__(self, fp, data_plot=False, distance=1):
        self.data_plot = data_plot
        self.distance = distance
        self.data_point = 0

        self.file = open(fp, mode='w')

    def __del__(self):
        self.file.flush()
        self.file.close()

    def add(self, value):
        if self.data_plot:
            self.file.write('({},{})'.format(self.data_point * self.distance, value))
            self.data_point += 1
        else:
            self.file.write('{} '.format(value))
