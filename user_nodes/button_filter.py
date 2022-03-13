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
