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
from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


def sensor_read(out0, sensor, storage):
    if sensor.value is not None:
        out0.append(sensor.value)


def print_out(in0, time_frame, values_per_time_frame, storage):
    if 'last_time_frame' not in storage:
        storage['last_time_frame'] = ticks_ms()

    if time_frame is 0 and in0:
        print(in0)
        in0.clear()
    elif time_frame is not 0 and ticks_ms_diff_to_current(storage['last_time_frame']) >= time_frame:
        print(in0)
        in0.clear()
        storage['last_time_frame'] = ticks_ms()


def map_test(in0, out0, storage):
    for val in in0:
        out0.append(val + 1)
    in0.clear()


def filter_test(in0, out0, storage):
    for val in in0:
        out0.append(val > 0)
    in0.clear()


def pass_through(in0, out0, storage):
    for val in in0:
        out0.append(val)
    in0.clear()
