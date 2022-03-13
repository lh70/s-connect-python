import os

from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.logging import DataLogger


def throughput_observer(in0, filepath=False, storage=None):
    if 'time' not in storage:
        storage['time'] = ticks_ms()
        storage['sum'] = 0
        if filepath:
            storage['file'] = DataLogger(filepath)

    storage['sum'] += len(in0)
    in0.clear()

    if ticks_ms_diff_to_current(storage['time']) >= 1000:
        storage['time'] = ticks_ms()

        os.system('cls' if os.name == 'nt' else 'clear')
        print('Throughput Observer\n\ncurrent throughput: {} values/second'.format(storage['sum']))

        if filepath:
            storage['file'].add(storage['sum'])

        storage['sum'] = 0
