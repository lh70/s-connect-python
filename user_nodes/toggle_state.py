def toggle_state(in0, out0, eval_str='x > 0', initial_state=False, storage=None):
    if 'out' not in storage:
        storage['out'] = initial_state

    for x in in0:
        if eval(eval_str, {}, {'x': x}):
            storage['out'] = not storage['out']

        out0.append(storage['out'])

    in0.clear()
