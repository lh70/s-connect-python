import time

from lh_lib.base.constants import RUNNING_MICROPYTHON


def ticks_ms():
    if RUNNING_MICROPYTHON:
        return time.ticks_ms()
    # on CPython we cannot use ticks, but it is assumed fast enough to use time_ns()
    # time_ns() is converted to milliseconds with rounding using only integer arithmetic
    return (time.perf_counter_ns() + 500000) // 1000000


def ticks_ms_diff_to_current(old_ticks):
    if RUNNING_MICROPYTHON:
        return time.ticks_diff(time.ticks_ms(), old_ticks)
    # on CPython we cannot use ticks, but it is assumed fast enough to use time_ns()
    # time_ns() is converted to milliseconds with rounding using only integer arithmetic
    return (time.perf_counter_ns() + 500000) // 1000000 - old_ticks


def ticks_us():
    if RUNNING_MICROPYTHON:
        return time.ticks_us()
    # on CPython we cannot use ticks, but it is assumed fast enough to use time_ns()
    # time_ns() is converted to microseconds with rounding using only integer arithmetic
    return (time.perf_counter_ns() + 500) // 1000


def ticks_us_diff_to_current(old_ticks):
    if RUNNING_MICROPYTHON:
        return time.ticks_diff(time.ticks_us(), old_ticks)
    # on CPython we cannot use ticks, but it is assumed fast enough to use time_ns()
    # time_ns() is converted to microseconds with rounding using only integer arithmetic
    return (time.perf_counter_ns() + 500) // 1000 - old_ticks


def sleep_us(us):
    if RUNNING_MICROPYTHON:
        time.sleep_us(us)
    else:
        # CPython has no dedicated microseconds sleep method
        time.sleep(us/1000000.0)
