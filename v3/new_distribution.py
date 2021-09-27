import os
import sys

try:
    from lh_lib.user_processes import SensorRead
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.user_processes import SensorRead

from lh_lib.user_processes import SensorRead, PrintItems, Join, Map, Sum, Mean
from lh_lib.processing import Device


esp_32_1 = Device('192.168.2.177', 8090, 100, 0)
esp_32_2 = Device('192.168.2.146', 8090, 100, 0)
esp_32_3 = Device('192.168.2.182', 8090, 100, 0)
esp_32_4 = Device('192.168.2.162', 8090, 100, 0)
esp_32_5 = Device('192.168.2.124', 8090, 100, 0)
pc_local_0 = Device('192.168.2.163', 8090, 100, 0)

p0 = SensorRead(esp_32_3, 'rotary_encoder')
p1 = SensorRead(pc_local_0, 'dummy')
p2 = Join(pc_local_0, p0.out0, p1.out0)
p3 = Map(pc_local_0, p2.out0, 'x')
p4 = Sum(pc_local_0, p3.out0, 100)
p5 = Mean(pc_local_0, p4.out0)
p6 = PrintItems(pc_local_0, p5.out0, 'rotary values (100ms tf): {}', 100, 0)

distribution, assignment_order = p0.build_distribution('0')

for device in assignment_order:
    device.remove_assignment('0')
    device.distribute_assignment(distribution)
