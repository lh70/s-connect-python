import os
import sys

try:
    from lh_lib.user_processes import SensorRead
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.user_nodes import SensorRead

from lh_lib.user_nodes import PrintQueue, Join, Map, ButtonFilter, ButtonToSingleEmit, Duplicate, ToggleState
from lh_lib.user_distribution import Device
from lh_lib.exceptions import AcknowledgementException

from lh_lib.user_nodes_utility import observe_throughput, CaseStudyDelayObserverBuilder

time_frame = 50

esp_32_1 = Device('192.168.2.177', 8090, time_frame)
esp_32_2 = Device('192.168.2.146', 8090, time_frame)
esp_32_3 = Device('192.168.2.182', 8090, time_frame)
esp_32_4 = Device('192.168.2.162', 8090, time_frame)
esp_32_5 = Device('192.168.2.124', 8090, time_frame)
pc_local = Device('192.168.2.163', 8090, time_frame)

pc_observer_0 = Device('192.168.2.163', 8100, time_frame)
pc_observer_1 = Device('192.168.2.163', 8101, time_frame)
pc_observer_2 = Device('192.168.2.163', 8102, time_frame)
pc_observer_3 = Device('192.168.2.163', 8103, time_frame)
pc_observer_4 = Device('192.168.2.163', 8104, time_frame)
pc_observer_5 = Device('192.168.2.163', 8105, time_frame)

delay_observer = CaseStudyDelayObserverBuilder(pc_observer_0)

raw_co2 = observe_throughput(pc_observer_1,
                             SensorRead(esp_32_2, 'co2'))
raw_dht11 = observe_throughput(pc_observer_2,
                               SensorRead(esp_32_2, 'dht11'))
raw_ultrasonic = observe_throughput(pc_observer_3,
                                    SensorRead(esp_32_2, 'ultrasonic'))
raw_rotary_encoder = observe_throughput(pc_observer_4,
                                        SensorRead(esp_32_3, 'rotary_encoder'))
raw_button = delay_observer.input(observe_throughput(pc_observer_5,
                                                     SensorRead(esp_32_4, 'button')))

selection_int = Map(pc_local, raw_rotary_encoder.out0, eval_str='int(x/2) % 3')

button_filtered = ButtonFilter(pc_local, raw_button.out0, flip_threshold=1)
button_single_emit = ButtonToSingleEmit(pc_local, button_filtered.out0)

joined_selection = Join(pc_local, selection_int.out0, button_single_emit.out0, eval_str='(x, y)')

duplicator_0 = Duplicate(pc_local, joined_selection.out0)
duplicator_1 = Duplicate(pc_local, duplicator_0.out0)

co2_toggle = ToggleState(pc_local, duplicator_0.out1, eval_str='x[0]==0 and x[1]', initial_state=True)
temperature_toggle = ToggleState(pc_local, duplicator_1.out0, eval_str='x[0]==1 and x[1]', initial_state=True)
distance_toggle = ToggleState(pc_local, duplicator_1.out1, eval_str='x[0]==2 and x[1]', initial_state=True)

co2_filtered = Map(pc_local, raw_co2.out0, eval_str='x[2] > 0')
temperature_filtered = Map(pc_local, raw_dht11.out0, eval_str='x[0] > 45')
distance_filtered = Map(pc_local, raw_ultrasonic.out0, eval_str='x[0] is not -1 and x[1] < 10')

co2_bool = Join(pc_local, co2_toggle.out0, co2_filtered.out0, eval_str='y if x else False')
dht11_bool = Join(pc_local, temperature_toggle.out0, temperature_filtered.out0, eval_str='y if x else False')
ultrasonic_bool = Join(pc_local, distance_toggle.out0, distance_filtered.out0, eval_str='False if x else False')  # y if x else False

joined = Join(pc_local, co2_bool.out0, dht11_bool.out0, eval_str='x or y')
alarm_ser = delay_observer.output(
    Join(pc_local, joined.out0, ultrasonic_bool.out0, eval_str='x or y'))

output = PrintQueue(pc_local, alarm_ser.out0, time_frame=100)

distribution, assignment_order = output.build_distribution('0')


if len(sys.argv) == 2:
    if sys.argv[1] == 'order':
        for device in assignment_order:
            print(f'{device.host}:{device.port}')
    elif sys.argv[1] == 'clear':
        print('clearing assignment')
        for device in assignment_order:
            try:
                device.remove_assignment('0')
            except (AcknowledgementException, TimeoutError, ConnectionRefusedError):
                raise Exception(
                    f'Fatal Error: device {device.host}:{device.port} is not reachable. Please check if Framework is running.')
    else:
        raise Exception(f'unknown command: {sys.argv[1]}')
else:
    print('removing old assignments')
    for device in assignment_order:
        try:
            device.remove_assignment('0')
        except (AcknowledgementException, TimeoutError, ConnectionRefusedError):
            raise Exception(f'Fatal Error: device {device.host}:{device.port} is not reachable. Please check if Framework is running.')

    print('assigning new assignment')
    for device in assignment_order:
        try:
            device.distribute_assignment(distribution)
        except AcknowledgementException:
            raise Exception(f'Fatal Error: device {device.host}:{device.port} is not answering. Probably a fatal error occurred on the device. Please check.')