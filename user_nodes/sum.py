from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


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
