try:
    import usys as sys
except ImportError:
    import sys

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if not RUNNING_MICROPYTHON:
    import os
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))

from lh_lib.distribution import Distributor


assignment = {
    'assignment-id': '1',
    'pipelines': {
        'sensor0': {'type': 'sensor', 'sensor-name': 'co2'},
        'print0': {'type': 'print', 'time-frame': 0, 'values-per-time-frame': 0}
    },
    'processing': {
        'proc0': {'method': 'pass_through', 'kwargs': {'in0': 'sensor0', 'out0': 'pipe0'}},
        'proc1': {'method': 'pass_through', 'kwargs': {'in0': 'pipe0', 'out0': 'print0'}},
    }
}

devices = {
    'esp32': {'host': '192.168.2.177', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0}
}

distribution = [
    ['esp32', ['proc0', 'proc1']]
]

d = Distributor()
distribution_assignments, assignment_order = d.build_distributed_assignment(assignment, devices, distribution)
d.distribute_assignments(distribution_assignments, assignment_order, devices)
