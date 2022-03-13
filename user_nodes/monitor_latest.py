import os


def monitor_latest(in0, storage=None):
    if len(in0) > 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('MonitorLatest\n\nvalue: {}'.format(in0[-1]))

    in0.clear()
