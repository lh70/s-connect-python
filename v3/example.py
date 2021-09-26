import os
import sys

try:
    from lh_lib.user_processes import SensorRead
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.user_processes import SensorRead

from lh_lib.user_processes import SensorRead, PrintItems, Join
from lh_lib.processing import Device


esp_32 = Device('192.168.2.182', 8090)
pc = Device('192.168.2.163', 8090)

p0 = SensorRead(esp_32, 'rotary_encoder')
# output: current position: 0..1..2..3..4..3..2..

p1 = SensorRead(esp_32, 'dht11')
# output: current temperature + humidity: (25, 70)..(24, 85)..

p2 = Join(esp_32, p0.out0, p1.out0, eval_str='(y[0] > x, x)')
# output: temperature > rotary value, rotary value: (True, 10)..(False, 35)..

p3 = PrintItems(pc, p2.out0, format_str='temperature is greater than {1} degrees Celsius: {0}', time_frame=100)

distribution, assignment_order = p0.build_distribution('0')

for device in assignment_order:
    device.remove_assignment('0')
    device.distribute_assignment(distribution)
