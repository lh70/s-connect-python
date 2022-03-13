def duplicate(in0, out0, out1, storage=None):
    for val in in0:
        out0.append(val)
        out1.append(val)
    in0.clear()
