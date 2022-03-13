def join_with_dup_filter(in0, in1, out0, eval_str='x + y', storage=None):
    if 'latest_x' not in storage:
        storage['latest_x'] = None
        storage['latest_y'] = None
        storage['last_z'] = None

    length = len(in0) if len(in0) > len(in1) else len(in1)
    for i in range(length):
        x = in0[i] if i < len(in0) else storage['latest_x']
        y = in1[i] if i < len(in1) else storage['latest_y']

        if x is not None and y is not None:
            z = eval(eval_str, {}, {'x': x, 'y': y})

            if z != storage['last_z']:
                out0.append(z)
                storage['last_z'] = z

        storage['latest_x'] = x
        storage['latest_y'] = y

    in0.clear()
    in1.clear()
