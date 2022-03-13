from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


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
