"""
This module contains a list of processing functions


the functions have to implement tho following signature:

inNN: list of values ready to be processed
      list must be cleared by function

outNN: list of result values
       must be filled by function
       list gets cleared by framework:
            pipeline logic:
                list may not be empty on function call, so only append values to list, do not replace it

storage: dict(k->obj) semi-persistent storage that is empty on program start
                      and is kept persistent and unique for each processing function.
"""

from lh_lib.processing_utility import filter


def map_test(in0, out0, storage):
    for val in in0:
        out0.append(val + 1)
    in0.clear()


def filter_test(in0, out0, storage):
    for val in in0:
        out0.append(val > 0)
    in0.clear()


def pass_through(in0, out0, storage):
    for val in in0:
        out0.append(val)
    in0.clear()