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
Standard Nodes """


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


def join_with_dup_filter(in0, in1, out0, eval_str='x + y', storage=None):
    if 'latest_x' not in storage:
        storage['latest_x'] = None
        storage['latest_y'] = None
        storage['last_z'] = None

    length = len(in0) if len(in0) > len(in1) else len(in1)
    for i in range(length):
        x = in0[i] if i < len(in0) else storage['latest_x']
        y = in1[i] if i < len(in1) else storage['latest_y']

        if x is not None and y is not None:
            z = eval(eval_str, {}, {'x': x, 'y': y})

            if z != storage['last_z']:
                out0.append(z)
                storage['last_z'] = z

        storage['latest_x'] = x
        storage['latest_y'] = y

    in0.clear()
    in1.clear()


def sum(in0, out0, time_frame=0, storage=None):
    if time_frame == 0:
        if 'sum' not in storage:
            storage['sum'] = 0

        for val in in0:
            storage['sum'] += val
            out0.append(storage['sum'])
    else:
        if 'sum' not in storage:
            storage['last_time_frame'] = ticks_ms()
            storage['sum'] = 0

        for val in in0:
            storage['sum'] += val

        if ticks_ms_diff_to_current(storage['last_time_frame']) >= time_frame:
            out0.append(storage['sum'])
            storage['last_time_frame'] = ticks_ms()
            storage['sum'] = 0

    in0.clear()


def mean(in0, out0, time_frame=0, storage=None):
    if 'sum' not in storage:
        storage['sum'] = 0
        storage['size'] = 0
        storage['last_time_frame'] = ticks_ms()

    if time_frame == 0:
        for val in in0:
            storage['sum'] += val
            storage['size'] += 1
            out0.append(storage['sum'] / float(storage['size']))
    else:
        for val in in0:
            storage['sum'] += val
        storage['size'] += len(in0)

        if ticks_ms_diff_to_current(storage['last_time_frame']) >= time_frame:
            out0.append(storage['sum'] / float(storage['size']))
            storage['sum'] = 0
            storage['size'] = 0
            storage['last_time_frame'] = ticks_ms()

    in0.clear()


def duplicate(in0, out0, out1, storage=None):
    for val in in0:
        out0.append(val)
        out1.append(val)
    in0.clear()


def print_queue(in0, format_str='{}', time_frame=0, values_per_time_frame=0, storage=None):
    if 'last_time_frame' not in storage:
        storage['last_time_frame'] = ticks_ms()

    if time_frame == 0 and in0:
        print(format_str.format(in0))
        in0.clear()
    elif time_frame != 0 and ticks_ms_diff_to_current(storage['last_time_frame']) >= time_frame:
        print(format_str.format(in0))
        in0.clear()
        storage['last_time_frame'] = ticks_ms()


def print_items(in0, format_str='{}', time_frame=0, values_per_time_frame=0, storage=None):
    if 'last_time_frame' not in storage:
        storage['last_time_frame'] = ticks_ms()

    if time_frame == 0 and in0:
        for x in in0:
            if isinstance(x, (tuple, list)):
                print(format_str.format(*x))
            else:
                print(format_str.format(x))
        in0.clear()
    elif time_frame != 0 and ticks_ms_diff_to_current(storage['last_time_frame']) >= time_frame:
        for x in in0:
            if isinstance(x, (tuple, list)):
                print(format_str.format(*x))
            else:
                print(format_str.format(x))
        in0.clear()
        storage['last_time_frame'] = ticks_ms()


"""
Specific Case Study Nodes """


def button_filter(in0, out0, flip_threshold=5, initial_state=False, storage=None):
    if 'pressed' not in storage:
        storage['pressed'] = initial_state
        storage['pressed-count'] = 0
        storage['out-state'] = initial_state

    for is_pressed in in0:
        if is_pressed == storage['pressed']:
            storage['pressed-count'] += 1
        else:
            storage['pressed'] = is_pressed
            storage['pressed-count'] = 0

        if storage['pressed-count'] > flip_threshold:
            storage['out-state'] = storage['pressed']

        out0.append(storage['out-state'])

    in0.clear()


def button_to_single_emit(in0, out0, storage=None):
    if 'emitted' not in storage:
        storage['emitted'] = False

    for is_pressed in in0:
        if is_pressed and not storage['emitted']:
            out0.append(True)
            out0.append(False)  # join copies old values of input. We just want one True value, so make sure only one True gets passed on.
            storage['emitted'] = True
        elif not is_pressed and storage['emitted']:
            storage['emitted'] = False
#            else:
#                out0.append(False)

    in0.clear()


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


def case_study_delay_observer(in0, in1, filepath=False, storage=None):
    if 'latest_in0' not in storage:
        storage['latest_in0'] = False
        storage['latest_in1'] = False
        storage['queue'] = []
        storage['time_delays'] = []
        if filepath:
            storage['file'] = DataLogger(filepath)

        os.system('cls' if os.name == 'nt' else 'clear')
        print('Case Study Delay Observer\n\nInit')

    for i in in0:
        if i and not storage['latest_in0']:  # on rising edge <==> False->True <==> button pressed
            if len(storage['queue']) == 0 or ticks_ms_diff_to_current(storage['queue'][-1]) > 10:  # filter flickering
                storage['queue'].append(ticks_ms())
        storage['latest_in0'] = i

    for i in in1:
        if i != storage['latest_in1']:  # on flipped state <==> True->False or False->True
            if len(storage['queue']) > 0:  # should be always true at this moment, if not: ignore this flip
                '''
                # old approach
                delay = ticks_ms_diff_to_current(storage['queue'].pop(0))
                while delay > 1000 and len(storage['queue']) > 0:  # case study presses button about every 2 seconds. if flickering got through, it should not pass this test
                    delay = ticks_ms_diff_to_current(storage['queue'].pop(0))
                storage['time_delays'].append(delay)
                '''
                # new approach. delay is < 2 seconds, so only one item should be in list, every other item is flickering, so take the first and delete the others
                storage['time_delays'].append(ticks_ms_diff_to_current(storage['queue'][0]))
                storage['queue'].clear()

        storage['latest_in1'] = i

    if len(storage['time_delays']) > 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Case Study Delay Observer\n\ntime delay: {}, queue: {}'.format(storage['time_delays'], storage['queue']))

        if filepath:
            file = storage['file']
            for delay in storage['time_delays']:
                file.add(delay)

        storage['time_delays'].clear()

    in0.clear()
    in1.clear()


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


def monitor_latest(in0, storage=None):
    if len(in0) > 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('MonitorLatest\n\nvalue: {}'.format(in0[-1]))

    in0.clear()
