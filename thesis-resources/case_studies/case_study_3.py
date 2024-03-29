from lh_lib.graph.objects import Node
from lh_lib.graph.device import Device
from lh_lib.graph.distribution import build_distribution
from user_nodes_utility import observe_throughput, CaseStudyDelayObserverBuilder
from user_nodes.sensor_read import SensorRead
from user_nodes.print_queue import PrintQueue
from user_nodes.join import Join
from user_nodes.join_with_dup_filter import JoinWithDupFilter
from user_nodes.map import Map
from user_nodes.button_filter import ButtonFilter
from user_nodes.button_to_single_emit import ButtonToSingleEmit
from user_nodes.duplicate import Duplicate
from user_nodes.toggle_state import ToggleState
from user_nodes.throttle import Throttle

DATA_LOG_PATH = 'D:/temp/' + 'CS1_SendVariable_100ms_JoinNoFilter' + '/'


def get_distribution():
    time_frame_ms = 0
    heartbeat_ms = 1000

    esp_32_1 = Device('192.168.2.177', 8090, time_frame_ms, heartbeat_ms)  # 0
    esp_32_2 = Device('192.168.2.124', 8090, time_frame_ms, heartbeat_ms)  # 1
    esp_32_3 = Device('192.168.2.182', 8090, time_frame_ms, heartbeat_ms)  # 2
    esp_32_4 = Device('192.168.2.162', 8090, time_frame_ms, heartbeat_ms)  # 3
    esp_32_5 = Device('192.168.2.146', 8090, time_frame_ms, heartbeat_ms)  # 4
    pc_local = Device('192.168.2.163', 8090, time_frame_ms, heartbeat_ms)  # 5

    pc_observer_0 = Device('192.168.2.163', 8100, time_frame_ms, heartbeat_ms)  # 6
    pc_observer_1 = Device('192.168.2.163', 8101, time_frame_ms, heartbeat_ms)  # 7
    pc_observer_2 = Device('192.168.2.163', 8102, time_frame_ms, heartbeat_ms)  # 8
    pc_observer_3 = Device('192.168.2.163', 8103, time_frame_ms, heartbeat_ms)  # 9
    pc_observer_4 = Device('192.168.2.163', 8104, time_frame_ms, heartbeat_ms)  # 10
    pc_observer_5 = Device('192.168.2.163', 8105, time_frame_ms, heartbeat_ms)  # 11
    pc_observer_6 = Device('192.168.2.163', 8106, time_frame_ms, heartbeat_ms)  # 12

    delay_observer = CaseStudyDelayObserverBuilder(pc_observer_0, DATA_LOG_PATH + 'delay.log')

    throttled_co2 = Node(esp_32_3, Throttle, [Node(esp_32_3, SensorRead, sensor_class_name='CO2')])
    observed_co2 = observe_throughput(pc_observer_1, throttled_co2, DATA_LOG_PATH + 'co2.log')

    throttled_dht11 = Node(esp_32_4, Throttle, [Node(esp_32_4, SensorRead, sensor_class_name='DHT11')])
    observed_dht11 = observe_throughput(pc_observer_2, throttled_dht11, DATA_LOG_PATH + 'dht11.log')

    throttled_ultrasonic = Node(esp_32_5, Throttle, [Node(esp_32_5, SensorRead, sensor_class_name='Ultrasonic')])
    observed_ultrasonic = observe_throughput(pc_observer_3, throttled_ultrasonic, DATA_LOG_PATH + 'ultrasonic.log')

    throttled_rotary_encoder = Node(esp_32_1, Throttle, [Node(esp_32_1, SensorRead, sensor_class_name='RotaryEncoder')])
    observed_rotary_encoder = observe_throughput(pc_observer_4, throttled_rotary_encoder, DATA_LOG_PATH + 'rotary_encoder.log')

    raw_button = delay_observer.input(observe_throughput(pc_observer_5,
                                                         Node(esp_32_2, SensorRead, sensor_class_name='Button'), DATA_LOG_PATH + 'button.log'))

    selection_int = Node(esp_32_1, Map, [observed_rotary_encoder], eval_str='int(x/2) % 3')

    button_filtered = Node(esp_32_2, ButtonFilter, [raw_button], flip_threshold=1)
    button_single_emit = Node(esp_32_2, ButtonToSingleEmit, [button_filtered])

    joined_selection = Node(esp_32_1, JoinWithDupFilter, [selection_int, button_single_emit], eval_str='(x, y)')

    duplicator_0 = Node(esp_32_3, Duplicate, [joined_selection])
    duplicator_1 = Node(esp_32_4, Duplicate, [duplicator_0])

    co2_toggle = Node(esp_32_3, ToggleState, [duplicator_0], eval_str='x[0]==0 and x[1]', initial_state=True)
    temperature_toggle = Node(esp_32_4, ToggleState, [duplicator_1], eval_str='x[0]==1 and x[1]', initial_state=True)
    distance_toggle = Node(esp_32_5, ToggleState, [duplicator_1], eval_str='x[0]==2 and x[1]', initial_state=True)

    co2_filtered = Node(esp_32_3, Map, [observed_co2], eval_str='x[2] > 0')
    temperature_filtered = Node(esp_32_4, Map, [observed_dht11], eval_str='x[0] > 45')
    distance_filtered = Node(esp_32_5, Map, [observed_ultrasonic], eval_str='x[0] is not -1 and x[1] < 10')

    co2_bool = Node(esp_32_3, JoinWithDupFilter, [co2_toggle, co2_filtered], eval_str='y if x else False')
    dht11_bool = Node(esp_32_4, JoinWithDupFilter, [temperature_toggle, temperature_filtered], eval_str='y if x else False')
    ultrasonic_bool = Node(esp_32_5, JoinWithDupFilter, [distance_toggle, distance_filtered], eval_str='False if x else False')  # y if x else False

    joined = Node(esp_32_4, JoinWithDupFilter, [co2_bool, dht11_bool], eval_str='x or y')
    alarm_ser = delay_observer.output(observe_throughput(pc_observer_6,
                                                         Node(esp_32_5, JoinWithDupFilter, [joined, ultrasonic_bool], eval_str='x or y'), DATA_LOG_PATH + 'total.log'))

    output = Node(pc_local, PrintQueue, [alarm_ser], time_frame=100)

    return build_distribution('0')
