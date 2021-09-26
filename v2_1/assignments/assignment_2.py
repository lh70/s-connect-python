import os
import sys

try:
    from lh_lib.distribution import Distributor
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.realpath(os.path.dirname(__file__)))))
    from lh_lib.distribution import Distributor


assignment = {
    'assignment-id': '2',
    'processing': {
        'proc0': {'method': 'sensor_read', 'kwargs': {'out0': 'pipe0', 'sensor': 'hall'}},
        #'proc1': {'method': 'map', 'kwargs': {'in0': 'pipe0', 'out0': 'pipe1', 'eval_str': '1'}},
        'proc1': {'method': 'map_1', 'kwargs': {'in0': 'pipe0', 'out0': 'pipe1'}},
        'proc2': {'method': 'summation', 'kwargs': {'in0': 'pipe1', 'out0': 'pipe2', 'time_frame': 100}},
        'proc3': {'method': 'mean', 'kwargs': {'in0': 'pipe2', 'out0': 'pipe3', 'time_frame': 0}},
        'proc4': {'method': 'print_out', 'kwargs': {'in0': 'pipe3', 'time_frame': 0, 'values_per_time_frame': 0}}
    }
}


devices = {
    'esp32': {'host': '192.168.2.177', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0},
    'pc-local0': {'host': '192.168.2.163', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0}
}

distribution = [
    ['esp32', ['proc0', 'proc1', 'proc2', 'proc3']],
    ['pc-local0', ['proc4']]
]

d = Distributor()
distribution_assignments, assignment_order = d.build_distributed_assignment(assignment, devices, distribution)
d.distribute_assignments(distribution_assignments, assignment_order, devices)
