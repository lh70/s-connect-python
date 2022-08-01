from lh_lib.graph.objects import Node
from lh_lib.graph.device import Device
from lh_lib.graph.distribution import build_distribution
from user_nodes_utility import observe_throughput, CaseStudyDelayObserverBuilder
from user_nodes.sensor_read import SensorRead
from user_nodes.print_queue import PrintQueue
from user_nodes.join import Join
from user_nodes.map import Map
from user_nodes.button_filter import ButtonFilter
from user_nodes.button_to_single_emit import ButtonToSingleEmit
from user_nodes.duplicate import Duplicate
from user_nodes.toggle_state import ToggleState

DATA_LOG_PATH = 'D:/temp/' + 'CS1_SendVariable_100ms_JoinNoFilter' + '/'


def get_distribution():
    time_frame = 100

    esp_32_1 = Device('192.168.2.177', 8090, time_frame)  # 0
    esp_32_2 = Device('192.168.2.124', 8090, time_frame)  # 1
    esp_32_3 = Device('192.168.2.182', 8090, time_frame)  # 2
    esp_32_4 = Device('192.168.2.162', 8090, time_frame)  # 3
    esp_32_5 = Device('192.168.2.146', 8090, time_frame)  # 4
    pc_local = Device('192.168.2.163', 8090, time_frame)  # 5

    pc_observer_0 = Device('192.168.2.163', 8100, time_frame)  # 6
    pc_observer_1 = Device('192.168.2.163', 8101, time_frame)  # 7
    pc_observer_2 = Device('192.168.2.163', 8102, time_frame)  # 8
    pc_observer_3 = Device('192.168.2.163', 8103, time_frame)  # 9
    pc_observer_4 = Device('192.168.2.163', 8104, time_frame)  # 10
    pc_observer_5 = Device('192.168.2.163', 8105, time_frame)  # 11
    pc_observer_6 = Device('192.168.2.163', 8106, time_frame)  # 12

    delay_observer = CaseStudyDelayObserverBuilder(pc_observer_0, DATA_LOG_PATH + 'delay.log')

    raw_co2 = observe_throughput(pc_observer_1,
                                 Node(esp_32_3, SensorRead, sensor_class_name='CO2'), DATA_LOG_PATH + 'co2.log')
    raw_dht11 = observe_throughput(pc_observer_2,
                                   Node(esp_32_4, SensorRead, sensor_class_name='DHT11'), DATA_LOG_PATH + 'dht11.log')
    raw_ultrasonic = observe_throughput(pc_observer_3,
                                        Node(esp_32_5, SensorRead, sensor_class_name='Ultrasonic'), DATA_LOG_PATH + 'ultrasonic.log')
    raw_rotary_encoder = observe_throughput(pc_observer_4,
                                            Node(esp_32_1, SensorRead, sensor_class_name='RotaryEncoder'), DATA_LOG_PATH + 'rotary_encoder.log')
    raw_button = delay_observer.input(observe_throughput(pc_observer_5,
                                                         Node(esp_32_2, SensorRead, sensor_class_name='Button'), DATA_LOG_PATH + 'button.log'))

    selection_int = Node(esp_32_1, Map, [raw_rotary_encoder], eval_str='int(x/2) % 3')

    button_filtered = Node(esp_32_2, ButtonFilter, [raw_button], flip_threshold=1)
    button_single_emit = Node(esp_32_2, ButtonToSingleEmit, [button_filtered])

    joined_selection = Node(pc_local, Join, [selection_int, button_single_emit], eval_str='(x, y)')

    duplicator_0 = Node(pc_local, Duplicate, [joined_selection])
    duplicator_1 = Node(pc_local, Duplicate, [duplicator_0])

    co2_toggle = Node(pc_local, ToggleState, [duplicator_0], eval_str='x[0]==0 and x[1]', initial_state=True)
    temperature_toggle = Node(pc_local, ToggleState, [duplicator_1], eval_str='x[0]==1 and x[1]', initial_state=True)
    distance_toggle = Node(pc_local, ToggleState, [duplicator_1], eval_str='x[0]==2 and x[1]', initial_state=True)

    co2_filtered = Node(esp_32_3, Map, [raw_co2], eval_str='x[2] > 0')
    temperature_filtered = Node(esp_32_4, Map, [raw_dht11], eval_str='x[0] > 45')
    distance_filtered = Node(esp_32_5, Map, [raw_ultrasonic], eval_str='x[0] is not -1 and x[1] < 10')

    co2_bool = Node(pc_local, Join, [co2_toggle, co2_filtered], eval_str='y if x else False')
    dht11_bool = Node(pc_local, Join, [temperature_toggle, temperature_filtered], eval_str='y if x else False')
    ultrasonic_bool = Node(pc_local, Join, [distance_toggle, distance_filtered], eval_str='False if x else False')  # y if x else False

    joined = Node(pc_local, Join, [co2_bool, dht11_bool], eval_str='x or y')
    alarm_ser = delay_observer.output(observe_throughput(pc_observer_6,
                                                         Node(pc_local, Join, [joined, ultrasonic_bool], eval_str='x or y'), DATA_LOG_PATH + 'total.log'))

    output = Node(pc_local, PrintQueue, [alarm_ser], time_frame=100)

    return build_distribution('0')
