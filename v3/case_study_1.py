import os
import sys

try:
    from lh_lib.user_processes import SensorRead
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.user_processes import SensorRead

from lh_lib.user_processes import Print, Join, Map, Sum, Mean, ButtonFilter, ButtonToSingleEmit, Duplicate, ToggleState
from lh_lib.processing import Device


esp_32_1 = Device('192.168.2.177', 8090, 100, 0)
esp_32_2 = Device('192.168.2.146', 8090, 100, 0)
esp_32_3 = Device('192.168.2.182', 8090, 100, 0)
esp_32_4 = Device('192.168.2.162', 8090, 100, 0)
esp_32_5 = Device('192.168.2.124', 8090, 100, 0)
pc_local_0 = Device('192.168.2.163', 8090, 100, 0)
pc_local_1 = Device('192.168.2.163', 8091, 100, 0)

raw_co2 = SensorRead(esp_32_3, 'co2')
raw_dht11 = SensorRead(esp_32_3, 'dht11')
raw_ultrasonic = SensorRead(esp_32_3, 'ultrasonic')
raw_rotary_encoder = SensorRead(esp_32_3, 'rotary_encoder')
raw_button = SensorRead(esp_32_3, 'button')

selection_int = Map(esp_32_3, raw_rotary_encoder.out0, eval_str='int(x/2) % 3')

button_filtered = ButtonFilter(esp_32_3, raw_button.out0, flip_threshold=1)
button_single_emit = ButtonToSingleEmit(esp_32_3, button_filtered.out0)

joined_selection = Join(esp_32_3, selection_int.out0, button_single_emit.out0, eval_str='(x, y)')

duplicator_0 = Duplicate(esp_32_3, joined_selection.out0)
duplicator_1 = Duplicate(esp_32_3, duplicator_0.out0)

co2_toggle = ToggleState(esp_32_3, duplicator_0.out1, eval_str='x[0]==0 and x[1]', initial_state=True)
temperature_toggle = ToggleState(esp_32_3, duplicator_1.out0, eval_str='x[0]==1 and x[1]', initial_state=True)
distance_toggle = ToggleState(esp_32_3, duplicator_1.out1, eval_str='x[0]==2 and x[1]', initial_state=True)

sel_dup = Duplicate(esp_32_3, co2_toggle.out0)
sel_out = Print(pc_local_1, sel_dup.out1, time_frame=500)

co2_filtered = Map(esp_32_3, raw_co2.out0, eval_str='x[2] > 800')
temperature_filtered = Map(esp_32_3, raw_dht11.out0, eval_str='x[0] > 45')
distance_filtered = Map(esp_32_3, raw_ultrasonic.out0, eval_str='x[0] is not -1 and x[1] < 10')

co2_bool = Join(esp_32_3, sel_dup.out0, co2_filtered.out0, eval_str='y if x else False', zip_oldest=False)
dht11_bool = Join(esp_32_3, temperature_toggle.out0, temperature_filtered.out0, eval_str='y if x else False')
ultrasonic_bool = Join(esp_32_3, distance_toggle.out0, distance_filtered.out0, eval_str='y if x else False')

test_dup = Duplicate(esp_32_3, co2_bool.out0)
test_out = Print(pc_local_1, test_dup.out1, time_frame=500)

joined = Join(esp_32_3, test_dup.out0, dht11_bool.out0, eval_str='x or y', zip_oldest=False)
alarm_ser = Join(esp_32_3, joined.out0, ultrasonic_bool.out0, eval_str='x or y', zip_oldest=False)

output = Print(pc_local_0, alarm_ser.out0, time_frame=100)


distribution, assignment_order = output.build_distribution('0')

#import json
#print(json.dumps(distribution, sort_keys=True, indent=4))

for device in assignment_order:
    device.remove_assignment('0')
    device.distribute_assignment(distribution)

