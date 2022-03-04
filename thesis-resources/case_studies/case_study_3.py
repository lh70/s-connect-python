from lh_lib.graph.objects import Node
from lh_lib.graph.device import Device
from lh_lib.graph.distribution import build_distribution
from user_nodes import sensor_read, print_queue, join, map, button_filter, button_to_single_emit, duplicate, toggle_state
from user_nodes_utility import observe_throughput, CaseStudyDelayObserverBuilder

DATA_LOG_PATH = 'D:/temp/' + 'CS1_SendVariable_100ms_JoinNoFilter' + '/'


def get_distribution():
    time_frame = 100

    esp_32_1 = Device('192.168.2.177', 8090, time_frame)  # 0
    esp_32_2 = Device('192.168.2.146', 8090, time_frame)  # 1
    esp_32_3 = Device('192.168.2.182', 8090, time_frame)  # 2
    esp_32_4 = Device('192.168.2.162', 8090, time_frame)  # 3
    esp_32_5 = Device('192.168.2.124', 8090, time_frame)  # 4
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
                                 Node(esp_32_3, sensor_read, sensor='co2'), DATA_LOG_PATH + 'co2.log')
    raw_dht11 = observe_throughput(pc_observer_2,
                                   Node(esp_32_4, sensor_read, sensor='dht11'), DATA_LOG_PATH + 'dht11.log')
    raw_ultrasonic = observe_throughput(pc_observer_3,
                                        Node(esp_32_5, sensor_read, sensor='ultrasonic'), DATA_LOG_PATH + 'ultrasonic.log')
    raw_rotary_encoder = observe_throughput(pc_observer_4,
                                            Node(esp_32_1, sensor_read, sensor='rotary_encoder'), DATA_LOG_PATH + 'rotary_encoder.log')
    raw_button = delay_observer.input(observe_throughput(pc_observer_5,
                                                         Node(esp_32_2, sensor_read, sensor='button'), DATA_LOG_PATH + 'button.log'))

    selection_int = Node(esp_32_1, map, [raw_rotary_encoder], eval_str='int(x/2) % 3')

    button_filtered = Node(esp_32_2, button_filter, [raw_button], flip_threshold=1)
    button_single_emit = Node(esp_32_2, button_to_single_emit, [button_filtered])

    joined_selection = Node(esp_32_1, join, [selection_int, button_single_emit], eval_str='(x, y)')

    duplicator_0 = Node(esp_32_3, duplicate, [joined_selection])
    duplicator_1 = Node(esp_32_4, duplicate, [duplicator_0])

    co2_toggle = Node(esp_32_3, toggle_state, [duplicator_0], eval_str='x[0]==0 and x[1]', initial_state=True)
    temperature_toggle = Node(esp_32_4, toggle_state, [duplicator_1], eval_str='x[0]==1 and x[1]', initial_state=True)
    distance_toggle = Node(esp_32_5, toggle_state, [duplicator_1], eval_str='x[0]==2 and x[1]', initial_state=True)

    co2_filtered = Node(esp_32_3, map, [raw_co2], eval_str='x[2] > 0')
    temperature_filtered = Node(esp_32_4, map, [raw_dht11], eval_str='x[0] > 45')
    distance_filtered = Node(esp_32_5, map, [raw_ultrasonic], eval_str='x[0] is not -1 and x[1] < 10')

    co2_bool = Node(esp_32_3, join, [co2_toggle, co2_filtered], eval_str='y if x else False')
    dht11_bool = Node(esp_32_4, join, [temperature_toggle, temperature_filtered], eval_str='y if x else False')
    ultrasonic_bool = Node(esp_32_5, join, [distance_toggle, distance_filtered], eval_str='False if x else False')  # y if x else False

    joined = Node(esp_32_4, join, [co2_bool, dht11_bool], eval_str='x or y')
    alarm_ser = delay_observer.output(observe_throughput(pc_observer_6,
                                                         Node(esp_32_5, join, [joined, ultrasonic_bool], eval_str='x or y'), DATA_LOG_PATH + 'total.log'))

    output = Node(pc_local, print_queue, [alarm_ser], time_frame=100)

    return build_distribution('0')
