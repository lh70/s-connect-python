from lh_lib.time import ticks_ms, ticks_ms_diff_to_current


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
