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

from lh_lib.processing import NoOutputProcess, SingleOutputProcess, DualOutputProcess
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


class SensorRead(SingleOutputProcess):

    def __init__(self, device, sensor):
        super().__init__(device, sensor=sensor)

    @classmethod
    def run(cls, out0, sensor, storage):
        if sensor.value is not None:
            out0.append(sensor.value)


class PrintQueue(NoOutputProcess):

    def __init__(self, device, in0, format_str='{}', time_frame=0, values_per_time_frame=0):
        super().__init__(device, in0=in0, format_str=format_str, time_frame=time_frame, values_per_time_frame=values_per_time_frame)

    @classmethod
    def run(cls, in0, format_str, time_frame, values_per_time_frame, storage):
        if 'last_time_frame' not in storage:
            storage['last_time_frame'] = ticks_ms()

        if time_frame is 0 and in0:
            print(format_str.format(in0))
            in0.clear()
        elif time_frame is not 0 and ticks_ms_diff_to_current(storage['last_time_frame']) >= time_frame:
            print(format_str.format(in0))
            in0.clear()
            storage['last_time_frame'] = ticks_ms()


class PrintItems(NoOutputProcess):

    def __init__(self, device, in0, format_str='{}', time_frame=0, values_per_time_frame=0):
        super().__init__(device, in0=in0, format_str=format_str, time_frame=time_frame, values_per_time_frame=values_per_time_frame)

    @classmethod
    def run(cls, in0, format_str, time_frame, values_per_time_frame, storage):
        if 'last_time_frame' not in storage:
            storage['last_time_frame'] = ticks_ms()

        if time_frame is 0 and in0:
            for x in in0:
                if isinstance(x, (tuple, list)):
                    print(format_str.format(*x))
                else:
                    print(format_str.format(x))
            in0.clear()
        elif time_frame is not 0 and ticks_ms_diff_to_current(storage['last_time_frame']) >= time_frame:
            for x in in0:
                if isinstance(x, (tuple, list)):
                    print(format_str.format(*x))
                else:
                    print(format_str.format(x))
            in0.clear()
            storage['last_time_frame'] = ticks_ms()


class PassThrough(SingleOutputProcess):

    def __init__(self, device, in0):
        super().__init__(device, in0=in0)

    @classmethod
    def run(cls, in0, out0, storage):
        for val in in0:
            out0.append(val)
        in0.clear()


class Map(SingleOutputProcess):

    def __init__(self, device, in0, eval_str='x'):
        super().__init__(device, in0=in0, eval_str=eval_str)

    @classmethod
    def run(cls, in0, out0, eval_str, storage):
        for x in in0:
            out0.append(eval(eval_str, {}, {'x': x}))
        in0.clear()


class Filter(SingleOutputProcess):

    def __init__(self, device, in0, eval_str='x > 0'):
        super().__init__(device, in0=in0, eval_str=eval_str)

    @classmethod
    def run(cls, in0, out0, eval_str, storage):
        for x in in0:
            if eval(eval_str, {}, {'x': x}):
                out0.append(x)
        in0.clear()


class Join(SingleOutputProcess):

    def __init__(self, device, in0, in1, eval_str='x + y'):
        super().__init__(device, in0=in0, in1=in1, eval_str=eval_str)

    @classmethod
    def run(cls, in0, in1, out0, eval_str, storage):
        if 'last_in0' not in storage:
            storage['last_in0'] = None
            storage['last_in1'] = None

        if len(in0) > 0:
            storage['last_in0'] = in0[-1]
        if len(in1) > 0:
            storage['last_in1'] = in1[-1]
        if len(in0) == 0 and storage['last_in1'] is None:
            in1.clear()
            return
        if len(in1) == 0 and storage['last_in0'] is None:
            in0.clear()
            return

        for x, y in zip(in0, in1):
            out0.append(eval(eval_str, {}, {'x': x, 'y': y}))

        if len(in0) < len(in1):
            for y in in1[len(in0):]:
                out0.append(eval(eval_str, {}, {'x': storage['last_in0'], 'y': y}))
        else:
            for x in in0[len(in1):]:
                out0.append(eval(eval_str, {}, {'x': x, 'y': storage['last_in1']}))

        in0.clear()
        in1.clear()


class Sum(SingleOutputProcess):

    def __init__(self, device, in0, time_frame=0):
        super().__init__(device, in0=in0, time_frame=time_frame)

    @classmethod
    def run(cls, in0, out0, time_frame, storage):
        if time_frame is 0:
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


class Mean(SingleOutputProcess):

    def __init__(self, device, in0, time_frame=0):
        super().__init__(device, in0=in0, time_frame=time_frame)

    @classmethod
    def run(cls, in0, out0, time_frame, storage):
        if 'sum' not in storage:
            storage['sum'] = 0
            storage['size'] = 0
            storage['last_time_frame'] = ticks_ms()

        if time_frame is 0:
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


class Duplicate(DualOutputProcess):

    def __init__(self, device, in0):
        super().__init__(device, in0=in0)

    @classmethod
    def run(cls, in0, out0, out1, storage):
        for val in in0:
            out0.append(val)
            out1.append(val)
        in0.clear()


class ButtonFilter(SingleOutputProcess):

    def __init__(self, device, in0, flip_threshold=5, initial_state=False):
        super().__init__(device, in0=in0, flip_threshold=flip_threshold, initial_state=initial_state)

    @classmethod
    def run(cls, in0, out0, flip_threshold, initial_state, storage):
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


class ButtonToSingleEmit(SingleOutputProcess):

    def __init__(self, device, in0):
        super().__init__(device, in0=in0)

    @classmethod
    def run(cls, in0, out0, storage):
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


class ToggleState(SingleOutputProcess):

    def __init__(self, device, in0, eval_str="x > 0", initial_state=False):
        super().__init__(device, in0=in0, eval_str=eval_str, initial_state=initial_state)

    @classmethod
    def run(cls, in0, out0, eval_str, initial_state, storage):
        if 'out' not in storage:
            storage['out'] = initial_state

        for x in in0:
            if eval(eval_str, {}, {'x': x}):
                storage['out'] = not storage['out']

            out0.append(storage['out'])

        in0.clear()


class ThroughputObserver(NoOutputProcess):

    def __init__(self, device, in0):
        super().__init__(device, in0=in0)

    @classmethod
    def run(cls, in0, storage):
        if 'time' not in storage:
            storage['time'] = ticks_ms()
            storage['sum'] = 0

        storage['sum'] += len(in0)
        in0.clear()

        if ticks_ms_diff_to_current(storage['time']) >= 1000:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Throughput Observer\n\ncurrent throughput: {} values/second'.format(storage['sum']))
            storage['time'] = ticks_ms()
            storage['sum'] = 0


class DelayObserver(NoOutputProcess):

    def __init__(self, device, in0, in1):
        super().__init__(device, in0=in0, in1=in1)

    """
    This Node requires the 1-in-1-out rule for all nodes in between in0 and in1,
    which means for every input value all nodes must emit one output value.
    Also, in0 must be first in process, as the delay is measured like time(v-in1) - time(v-in0).
    """
    @classmethod
    def run(cls, in0, in1, storage):
        if 'queue' not in storage:
            storage['queue'] = []
            storage['elem_delays'] = []
            storage['time_delays'] = []

        if len(in1) > (len(in0) + len(storage['queue'])):
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Delay Observer\n\nERROR: receiving more output ({}) than input ({}) values'.format(len(in1), len(in0) + len(storage['queue'])))

            storage['queue'] = []
        else:
            for _ in in0:
                storage['queue'].append(ticks_ms())

                if len(in1) > 0:
                    storage['elem_delays'].append(len(storage['queue']))
                    storage['time_delays'].append(ticks_ms_diff_to_current(storage['queue'].pop(0)))
                    del in1[0]

            for _ in in1:
                storage['elem_delays'].append(len(storage['queue']))
                storage['time_delays'].append(ticks_ms_diff_to_current(storage['queue'].pop(0)))

            if len(storage['elem_delays']) >= 10:
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Delay Observer\n\naverage items apart: {}\naverage time delay: {}'.format(sum(storage['elem_delays'][:10])/10, sum(storage['time_delays'][:10])/10))
                del storage['elem_delays'][:10]
                del storage['time_delays'][:10]
        in0.clear()
        in1.clear()


class CaseStudyDelayObserver(NoOutputProcess):

    def __init__(self, device, in0, in1):
        super().__init__(device, in0=in0, in1=in1)

    @classmethod
    def run(cls, in0, in1, storage):
        if 'latest_in0' not in storage:
            storage['latest_in0'] = False
            storage['latest_in1'] = False
            storage['queue'] = []
            storage['time_delays'] = []

            os.system('cls' if os.name == 'nt' else 'clear')
            print('Case Study Delay Observer\n\nInit')

        for i in in0:
            if i and not storage['latest_in0']:
                storage['queue'].append(ticks_ms())
            storage['latest_in0'] = i

        for i in in1:
            if i != storage['latest_in1']:
                if len(storage['queue']) > 0:
                    delay = ticks_ms_diff_to_current(storage['queue'].pop(0))
                    while delay < 2000 and len(storage['queue']) > 0:
                        delay = ticks_ms_diff_to_current(storage['queue'].pop(0))
                    storage['time_delays'].append(delay)

            storage['latest_in1'] = i

        if len(storage['time_delays']) > 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Case Study Delay Observer\n\ntime delay: {}, queue: {}'.format(storage['time_delays'], storage['queue']))
            storage['time_delays'].clear()

        in0.clear()
        in1.clear()


class Monitor(NoOutputProcess):

    def __init__(self, device, in0, time_frame=100):
        super().__init__(device, in0=in0, time_frame=time_frame)

    @classmethod
    def run(cls, in0, time_frame, storage):
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


class MonitorLatest(NoOutputProcess):
    def __init__(self, device, in0):
        super().__init__(device, in0=in0)

    @classmethod
    def run(cls, in0, storage):
        if len(in0) > 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('MonitorLatest\n\nvalue: {}'.format(in0[-1]))

        in0.clear()
