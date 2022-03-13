import os

from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


def monitor(in0, time_frame=100, storage=None):
    if 'values' not in storage:
        storage['time'] = ticks_ms()
        storage['values'] = []

    storage['values'] += in0
    in0.clear()

    if ticks_ms_diff_to_current(storage['time']) >= time_frame:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Monitor\n\ntimeframe: {}ms\nvalues: {}'.format(time_frame, storage['values']))
        storage['time'] = ticks_ms()
        storage['values'] = []
