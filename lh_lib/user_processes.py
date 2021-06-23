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
"""
from lh_lib.processing import Process
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.pipeline_utilities import delete_oldest, raise_on_full, zip_oldest_and_clear_lists, zip_newest_and_clear_lists, zip_newest_naive_and_clear_lists


class SensorRead(Process):

    def __init__(self, device, sensor):
        super().__init__(device, out0='out0', sensor=sensor)

    @classmethod
    def run(cls, out0, sensor, storage):
        if sensor.value is not None:
            out0.append(sensor.value)


class PrintOut(Process):

    def __init__(self, device, in0, time_frame, values_per_time_frame):
        super().__init__(device, in0=in0, time_frame=time_frame, values_per_time_frame=values_per_time_frame)

    @classmethod
    def run(cls, in0, time_frame, values_per_time_frame, storage):
        if 'last_time_frame' not in storage:
            storage['last_time_frame'] = ticks_ms()

        if time_frame is 0 and in0:
            print(in0)
            in0.clear()
        elif time_frame is not 0 and ticks_ms_diff_to_current(storage['last_time_frame']) >= time_frame:
            print(in0)
            in0.clear()
            storage['last_time_frame'] = ticks_ms()


class PassThrough(Process):

    def __init__(self, device, in0):
        super().__init__(device, in0=in0, out0='out0')

    @classmethod
    def run(cls, in0, out0, storage):
        for val in in0:
            out0.append(val)
        in0.clear()


class Map(Process):

    def __init__(self, device, in0, eval_str='x'):
        super().__init__(device, in0=in0, out0='out0', eval_str=eval_str)

    @classmethod
    def run(cls, in0, out0, eval_str, storage):
        for x in in0:
            out0.append(eval(eval_str))
        in0.clear()


class Filter(Process):

    def __init__(self, device, in0, eval_str='x > 0'):
        super().__init__(device, in0=in0, out0='out0', eval_str=eval_str)

    @classmethod
    def run(cls, in0, out0, eval_str, storage):
        for x in in0:
            if eval(eval_str):
                out0.append(x)
        in0.clear()


class Join(Process):

    def __init__(self, device, in0, in1, eval_str='x + y'):
        super().__init__(device, in0=in0, in1=in1, out0='out0', eval_str=eval_str)

    @classmethod
    def run(cls, in0, in1, out0, eval_str, storage):
        delete_oldest(in0, in1)
        for x, y in zip_oldest_and_clear_lists(in0, in1):
            out0.append(eval(eval_str))


class Sum(Process):

    def __init__(self, device, in0, time_frame=0):
        super().__init__(device, in0=in0, out0='out0', time_frame=time_frame)

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


class Mean(Process):

    def __init__(self, device, in0, time_frame=0):
        super().__init__(device, in0=in0, out0='out0', time_frame=time_frame)

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
