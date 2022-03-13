def pass_through(in0, out0, storage=None):
    for val in in0:
        out0.append(val)
    in0.clear()
