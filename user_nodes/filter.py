def filter(in0, out0, eval_str='x > 0', storage=None):
    for x in in0:
        if eval(eval_str, {}, {'x': x}):
            out0.append(x)
    in0.clear()
