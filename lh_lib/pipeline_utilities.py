"""
This module contains utility functions. To be used in processing functions.
"""


"""
Removes the oldest values from two input buffers if they are bigger than specified length_cap
"""
def delete_oldest(in0, in1, length_cap=1000):
    if len(in0) > length_cap:
        del in0[0:-length_cap]
    if len(in1) > length_cap:
        del in1[0:-length_cap]

def raise_on_full(in0, in1, length_cap=1000):
    if len(in0) > length_cap:
        raise Exception("length cap met on in0")
    if len(in1) > length_cap:
        raise Exception("length cap met on in1")


"""
Behaviour: 
Yields zipped values until shorter list is empty.
Finally all yielded values are deleted from the lists.
Result:
One buffer will be 'out of sync' the time it takes to fill the buffer to length_cap

returns the maximum length to which both buffers can be safely processed
"""
def zip_oldest_and_clear_lists(in0, in1):
    length_read = len(in1) if len(in0) > len(in1) else len(in0)

    for i in zip(in0, in1):
        yield i

    del in0[0:length_read]
    del in1[0:length_read]


"""
Behaviour:
Checks if length minimum is met on both lists.
Only if met, the method yields the newest values from both lists,
discarding the oldest values from the longer list.
Result:
The newest length_min (sometimes maybe more) items of both buffers can be processed.
Older buffered values are discarded on each iteration with buffers > min_length, 
which results in one buffer probably losing many values.
Also the continuous stream may not be so continuous any more.

returns a 2-tuple of slice values in0-start, in1-start so lists can be sliced like: in0[ret[0]:]
"""
def zip_newest_naive_and_clear_lists(in0, in1, length_min=20):
    if len(in0) < length_min or len(in1) < length_min:
        return

    if len(in0) > len(in1):
        del in0[0:-len(in1)]
    else:
        del in1[0:-len(in0)]

    for i in zip(in0, in1):
        yield i

    in0.clear()
    in1.clear()


"""
Behaviour:
Checks if length minimum is met on both lists.
Only if met, the method yields the newest values from both lists,
leaving max_ahead_buffer headroom in the longer list if possible.
Discards all old values and values read.
Result:
a buffer is only maximum max_ahead_buffer items behind and after an iteration there maybe is a buffer left
which can potentially compensate network delays.

returns a 4-tuple of slice values in0-start, in0-end, in1-start, in1-end
"""
def zip_newest_and_clear_lists(in0, in1, max_ahead_buffer=300, length_min=20):
    if len(in0) < length_min or len(in1) < length_min:
        return

    if len(in0) - len(in1) > max_ahead_buffer:
        del in0[0:-len(in1)-max_ahead_buffer]
    elif len(in1) - len(in0) > max_ahead_buffer:
        del in1[0:-len(in0)-max_ahead_buffer]

    length_read = len(in1) if len(in0) > len(in1) else len(in0)

    for i in zip(in0, in1):
        yield i

    del in0[0:length_read]
    del in1[0:length_read]


def zip_slow_duplicate(in0, in1):
    if len(in0) == 0:
        if len(in1) > 2:
            in1.clear()
        return
    if len(in1) == 0:
        if len(in0) > 2:
            in0.clear()
        return

    for i in zip(in0, in1):
        yield i

    if len(in0) == len(in1):
        in0.clear()
        in1.clear()
    if len(in0) > len(in1):
        for i0 in in0[len(in1):]:
            yield i0, in1[-1]

        in0.clear()
        del in1[:-1]
    else:
        for i1 in in1[len(in0):]:
            yield in0[-1], i1

        del in0[:-1]
        in1.clear()
