def join(in0, in1, out0, eval_str='x + y', storage=None):
    if 'latest_x' not in storage:
        storage['latest_x'] = None
        storage['latest_y'] = None
        storage['last_z'] = None

    length = len(in0) if len(in0) > len(in1) else len(in1)
    for i in range(length):
        x = in0[i] if i < len(in0) else storage['latest_x']
        y = in1[i] if i < len(in1) else storage['latest_y']

        if x is not None and y is not None:
            out0.append(eval(eval_str, {}, {'x': x, 'y': y}))

        storage['latest_x'] = x
        storage['latest_y'] = y

    in0.clear()
    in1.clear()
