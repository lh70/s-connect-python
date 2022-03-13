def map(in0, out0, eval_str='x', storage=None):
    for x in in0:
        out0.append(eval(eval_str, {}, {'x': x}))
    in0.clear()
