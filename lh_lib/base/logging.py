from lh_lib.base.time import ticks_ms

ACTIVE = True


# Simple wrapper to be able to silence the program for increased performance on MicroPython
def log(msg, *objects):
    if ACTIVE:
        print(str(msg).format(*objects))


class DataLogger:

    def __init__(self, fp):
        self.file = open(fp, mode='w')

    def __del__(self):
        self.file.flush()
        self.file.close()

    def add(self, value):
        self.file.write('({},{})'.format(ticks_ms(), value))
