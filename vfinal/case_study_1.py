import os
import sys

try:
    from lh_lib.user_processes import SensorRead
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.user_processes import SensorRead

from lh_lib.user_processes import PrintItems, PrintQueue, Join, Map, ButtonFilter, ButtonToSingleEmit, Duplicate, ToggleState
from lh_lib.processing import Device

from testing import monitor, print_pipe


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

raw_co2 = SensorRead(esp_32_3, 'co2')
raw_dht11 = SensorRead(esp_32_3, 'dht11')
raw_ultrasonic = SensorRead(esp_32_3, 'ultrasonic')
raw_rotary_encoder = SensorRead(esp_32_3, 'rotary_encoder')
raw_button = SensorRead(esp_32_3, 'button')

selection_int = Map(pc_local_0, raw_rotary_encoder.out0, eval_str='int(x/2) % 3')

button_filtered = ButtonFilter(pc_local_0, raw_button.out0, flip_threshold=1)
button_single_emit = ButtonToSingleEmit(pc_local_0, button_filtered.out0)

joined_selection = Join(pc_local_0, selection_int.out0, button_single_emit.out0, eval_str='(x, y)')

duplicator_0 = Duplicate(pc_local_0, monitor(pc_local_4, joined_selection.out0))
duplicator_1 = Duplicate(pc_local_0, duplicator_0.out0)

co2_toggle = ToggleState(pc_local_0, duplicator_0.out1, eval_str='x[0]==0 and x[1]', initial_state=True)
temperature_toggle = ToggleState(pc_local_0, duplicator_1.out0, eval_str='x[0]==1 and x[1]', initial_state=True)
distance_toggle = ToggleState(pc_local_0, duplicator_1.out1, eval_str='x[0]==2 and x[1]', initial_state=True)

co2_filtered = Map(pc_local_0, monitor(pc_local_2, raw_co2.out0), eval_str='x[2] > 500')
temperature_filtered = Map(pc_local_0, raw_dht11.out0, eval_str='x[0] > 45')
distance_filtered = Map(pc_local_0, raw_ultrasonic.out0, eval_str='x[0] is not -1 and x[1] < 10')

co2_bool = Join(pc_local_0, co2_toggle.out0, co2_filtered.out0, eval_str='y if x else False')
dht11_bool = Join(pc_local_0, temperature_toggle.out0, temperature_filtered.out0, eval_str='y if x else False')
ultrasonic_bool = Join(pc_local_0, distance_toggle.out0, distance_filtered.out0, eval_str='y if x else False')

joined = Join(pc_local_0, monitor(pc_local_1, co2_bool.out0), dht11_bool.out0, eval_str='x or y')
alarm_ser = Join(pc_local_0, joined.out0, ultrasonic_bool.out0, eval_str='x or y')

output = PrintQueue(pc_local_0, alarm_ser.out0, time_frame=100)

distribution, assignment_order = output.build_distribution('0')

for device in assignment_order:
    device.remove_assignment('0')
    device.distribute_assignment(distribution)

