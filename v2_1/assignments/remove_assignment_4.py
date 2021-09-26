import os
import sys

try:
    from lh_lib.distribution import Distributor
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.realpath(os.path.dirname(__file__)))))
    from lh_lib.distribution import Distributor

devices = {
    'esp32': {'host': '192.168.2.177', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0},
    'pc-local0': {'host': '192.168.2.163', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0}
}

Distributor().remove_assignments('4', devices)
