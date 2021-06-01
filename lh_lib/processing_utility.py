"""
This module contains utility functions. To be used in processing functions.
"""


"""
Behaviour: 
First it removes old values if length_cap is met.
Then it returns the length of the smaller buffer.
Result:
One buffer will be 'out of sync' the time it takes to fill the buffer to length_cap

returns the maximum length to which both buffers can be safely processed
"""
def filter_combine_oldest(in0, in1, length_cap=1000):
    if len(in0) > length_cap:
        del in0[0:-length_cap]
    if len(in1) > length_cap:
        del in1[0:-length_cap]

    if len(in0) > len(in1):
        return len(in1)
    else:
        return len(in0)


def get_lists_from_filter_combine_oldest(in0, in1, filter_return_value):
    return in0[0:filter_return_value], in1[0:filter_return_value]


def clear_lists_from_filter_combine_oldest(in0, in1, filter_return_value):
    del in0[0:filter_return_value]
    del in1[0:filter_return_value]


"""
Behaviour:
First it removes old values if length_cap is met.
Then it checks if length_min is met and returns buffer lengths if not.
Then it returns list-slice start values for both buffers.
Result:
The newest length_min (sometimes maybe more) items of both buffers can be processed.
Older buffered values are discarded on each iteration with buffers > min_length, 
which results in one buffer probably losing many values.
Also the continuous stream may not be so continuous any more.

returns a 2-tuple of slice values in0-start, in1-start so lists can be sliced like: in0[ret[0]:]
"""
def filter_combine_newest_naive(in0, in1, length_min=50, length_cap=1000):
    if len(in0) > length_cap:
        del in0[0:-length_cap]
    if len(in1) > length_cap:
        del in1[0:-length_cap]

    if len(in0) < length_min:
        return len(in0), len(in1)
    if len(in1) < length_min:
        return len(in0), len(in1)

    if len(in0) > len(in1):
        return -len(in1), 0
    else:
        return 0, -len(in0)


def get_lists_from_filter_combine_newest_naive(in0, in1, filter_return_value):
    return in0[filter_return_value[0]:], in1[filter_return_value[1]:]


def clear_lists_from_filter_combine_newest_naive(in0, in1, filter_return_value):
    if filter_return_value[0] < len(in0):
        in0.clear()
        in1.clear()


"""
Behaviour:
First it removes old values if length_cap is met.
Then it checks if length_min is met and returns buffer lengths if not.
Then it returns indexes with start and end the smaller buffer length apart.
The start is 0 on larger buffer if it is bigger less than max_ahead_buffer.
Else the start is shifted until the buffer is only bigger + max_ahead_buffer.
Result:
a buffer is only maximum max_ahead_buffer items behind and after an iteration there maybe is a buffer left
which can potentially compensate network delays.

returns a 4-tuple of slice values in0-start, in0-end, in1-start, in1-end
"""
def filter_combine_newest(in0, in1, max_ahead_buffer=300, length_min=50, length_cap=1000):
    if len(in0) > length_cap:
        del in0[0:-length_cap]
    if len(in1) > length_cap:
        del in1[0:-length_cap]

    if len(in0) < length_min:
        return len(in0), len(in0), len(in1), len(in1)
    if len(in1) < length_min:
        return len(in0), len(in0), len(in1), len(in1)

    if len(in0) > len(in1):
        if len(in1)+max_ahead_buffer > len(in0):
            return 0, len(in1), 0, len(in1)
        else:
            return -len(in1)-max_ahead_buffer, -max_ahead_buffer, 0, len(in1)
    else:
        if len(in0)+max_ahead_buffer > len(in1):
            return 0, len(in0), 0, len(in0)
        else:
            return 0, len(in0), -len(in0)-max_ahead_buffer, -max_ahead_buffer


def get_lists_from_filter_combine_newest(in0, in1, filter_return_value):
    return in0[filter_return_value[0]:filter_return_value[1]], in1[filter_return_value[2]:filter_return_value[3]]


def clear_list_from_filter_combine_newest(in0, in1, filter_return_value):
    del in0[:filter_return_value[1]]
    del in1[:filter_return_value[3]]
