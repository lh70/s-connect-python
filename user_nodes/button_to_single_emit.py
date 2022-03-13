def button_to_single_emit(in0, out0, storage=None):
    if 'emitted' not in storage:
        storage['emitted'] = False

    for is_pressed in in0:
        if is_pressed and not storage['emitted']:
            out0.append(True)
            out0.append(False)  # join copies old values of input. We just want one True value, so make sure only one True gets passed on.
            storage['emitted'] = True
        elif not is_pressed and storage['emitted']:
            storage['emitted'] = False
#            else:
#                out0.append(False)

    in0.clear()
