

OUT = True


# Simple wrapper to be able to silence the program for increased performance on MicroPython
def log(msg, *objects):
    if OUT:
        print(msg.format(objects), flush=True)
