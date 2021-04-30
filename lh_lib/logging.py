

ACTIVE = True


# Simple wrapper to be able to silence the program for increased performance on MicroPython
def log(msg, *objects):
    if ACTIVE:
        print(str(msg).format(*objects))
