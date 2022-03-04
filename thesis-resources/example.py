"""
the example computational setup and assignment
"""

import os
import sys

try:
    from lh_lib.graph.objects import Node
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.graph.objects import Node


from lh_lib.graph.device import Device
from lh_lib.graph.distribution import build_distribution
from user_nodes import sensor_read, print_items, join


esp_32 = Device('192.168.2.182', 8090)
pc = Device('192.168.2.163', 8090)

p0 = Node(esp_32, sensor_read, sensor='rotary_encoder')
# output: current position: 0..1..2..3..4..3..2..

p1 = Node(esp_32, sensor_read, sensor='dht11')
# output: current temperature + humidity: (25, 70)..(24, 85)..

p2 = Node(esp_32, join, [p0, p1], eval_str='(y[0] > x, x)')
# output: temperature > rotary value, rotary value: (True, 10)..(False, 35)..

p3 = Node(pc, print_items, [p2], format_str='temperature is greater than {1} degrees Celsius: {0}', time_frame=100)

ordered_devices, distribution = build_distribution('0')


for device in ordered_devices:
    device.remove_assignment('0')
    device.distribute_assignment(distribution)
