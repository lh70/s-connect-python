import os
import sys

try:
    from lh_lib.user_processes import SensorRead
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.user_processes import SensorRead

from lh_lib.user_processes import SensorRead, PrintOut, Join, Map, Sum, Mean
from lh_lib.network import Client

devices = {
    'esp32': {'host': '192.168.2.177', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0},
    'pc-local0': {'host': '192.168.2.163', 'port': 8090, 'max-input-time-frame': 100, 'max-input-values-per-time-frame': 0}
}

p0 = SensorRead('esp32', 'rotary_encoder')
p1 = SensorRead('pc-local0', 'dummy')
p2 = Join('pc-local0', p0.out0, p1.out0)
p3 = Map('pc-local0', p2.out0, '1')
p4 = Sum('pc-local0', p3.out0, 100)
p5 = Mean('pc-local0', p4.out0)
p6 = PrintOut('pc-local0', p5.out0, 100, 0)

distribution, assignment_order = p0.build_distribution('0', devices)

for device_id in assignment_order:
    assignment = distribution[device_id]
    device = devices[device_id]
    conn = Client(device['host'], device['port'])
    conn.send({'remove-assignment': {'assignment-id': assignment['assignment-id']}})
    conn.recv_acknowledgement()
    conn.send({'processing-assignment': assignment})
    conn.recv_acknowledgement()
    conn.socket.close()
