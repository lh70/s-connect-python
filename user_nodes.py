"""
This module contains a list of processing functions


the functions have to implement tho following signature:

inNN: list of values ready to be processed
      list must be cleared by function

outNN: list of result values
       must be filled by function
       list gets cleared by framework:
            pipeline logic:
                list may not be empty on function call, so only append values to list, do not replace it

storage: dict(k->obj) semi-persistent storage that is empty on program start
                      and is kept persistent and unique for each processing function.

IMPORTANT: eval() is used extensively on the generic functions. Micropython does not use local variables, which means
           eval(exp) is equal to eval(exp, globals(), globals()) and as a result we must provide all variables we need
           explicitly. This also enhances security ;)
           https://docs.micropython.org/en/latest/genrst/core_language.html?highlight=eval#code-running-in-eval-function-doesn-t-have-access-to-local-variables
"""
import os

from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.logging import DataLogger


def sensor_read(out0, sensor, read_delay_ms=0, storage=None):
    if 'last_valid' not in storage:
        storage['last_valid'] = None
        storage['last_read'] = 0

    if read_delay_ms == 0:  # old behaviour. read is faster than the sensor can provide values.
        if sensor.value is not None:
            out0.append(sensor.value)
    else:  # new behaviour. sensor is faster than the framework can process the values further down the line.
        if sensor.value is not None:
            storage['last_valid'] = sensor.value

        if ticks_ms_diff_to_current(storage['last_read']) > read_delay_ms and storage['last_valid'] is not None:
            storage['last_read'] = ticks_ms()
            out0.append(storage['last_valid'])


"""
Standard Nodes
"""
def pass_through(in0, out0, storage=None):
    for val in in0:
        out0.append(val)
    in0.clear()


def map(in0, out0, eval_str='x', storage=None):
    for x in in0:
        out0.append(eval(eval_str, {}, {'x': x}))
    in0.clear()


def filter(in0, out0, eval_str='x > 0', storage=None):
    for x in in0:
        if eval(eval_str, {}, {'x': x}):
            out0.append(x)
    in0.clear()


def join(in0, in1, out0, eval_str='x + y', storage=None):
    if 'latest_x' not in storage:
        storage['latest_x'] = None
        storage['latest_y'] = None
        storage['last_z'] = None

    length = len(in0) if len(in0) > len(in1) else len(in1)
    for i in range(length):
        x = in0[i] if i < len(in0) else storage['latest_x']
        y = in1[i] if i < len(in1) else storage['latest_y']

        if x is not None and y is not None:
            out0.append(eval(eval_str, {}, {'x': x, 'y': y}))

        storage['latest_x'] = x
        storage['latest_y'] = y

    in0.clear()
    in1.clear()


def toggle_state(in0, out0, eval_str='x > 0', initial_state=False, storage=None):
    if 'out' not in storage:
        storage['out'] = initial_state

    for x in in0:
        if eval(eval_str, {}, {'x': x}):
            storage['out'] = not storage['out']

        out0.append(storage['out'])

    in0.clear()


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
