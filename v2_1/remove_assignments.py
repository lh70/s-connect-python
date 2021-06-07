"""
Needs:
* one micropython worker ('192.168.2.177', 8090) with sensor 'rotary_encoder'
* one desktop worker ('localhost', 8090)
* one desktop worker ('localhost', 8091)
"""

try:
    import usys as sys
except ImportError:
    import sys

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if not RUNNING_MICROPYTHON:
    import os
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))

from lh_lib.distribution import Distributor


devices = {
    'esp32': {'host': '192.168.2.177', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0},
    'pc-local0': {'host': '192.168.2.163', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0},
    'pc-local1': {'host': '192.168.2.163', 'port': 8091, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0}
}

d = Distributor()
d.remove_assignments('1', devices)
