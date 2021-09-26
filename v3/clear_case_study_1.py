import os
import sys

try:
    from lh_lib.processing import Device
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.processing import Device

esp_32_1 = Device('192.168.2.177', 8090, 100)
esp_32_2 = Device('192.168.2.146', 8090, 100)
esp_32_3 = Device('192.168.2.182', 8090, 100)
esp_32_4 = Device('192.168.2.162', 8090, 100)
esp_32_5 = Device('192.168.2.124', 8090, 100)
pc_local_0 = Device('192.168.2.163', 8090, 100)
pc_local_1 = Device('192.168.2.163', 8091, 100)
pc_local_2 = Device('192.168.2.163', 8092, 100)
pc_local_3 = Device('192.168.2.163', 8093, 100)
pc_local_4 = Device('192.168.2.163', 8094, 100)

for device in (esp_32_3, pc_local_0, pc_local_1, pc_local_2, pc_local_3, pc_local_4):
    device.remove_assignment('0')
