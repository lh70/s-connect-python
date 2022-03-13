from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


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
