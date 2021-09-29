from lh_lib.user_nodes import SensorRead, PrintQueue, Join, Map, ButtonFilter, ButtonToSingleEmit, Duplicate, ToggleState, JoinWithDupFilter
from lh_lib.user_distribution import Device

from lh_lib.user_nodes_utility import observe_throughput, CaseStudyDelayObserverBuilder, monitor_latest, print_queue

DATA_LOG_PATH = 'D:/temp/' + 'CS2_SendFixed_100ms_JoinDupFilter' + '/'


def get_distribution():
    time_frame = 100

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
    pc_observer_6 = Device('192.168.2.163', 8106, time_frame)

    delay_observer = CaseStudyDelayObserverBuilder(pc_observer_0, DATA_LOG_PATH + 'delay.log')

    raw_co2 = observe_throughput(pc_observer_1,
                                 SensorRead(esp_32_3, 'co2'), DATA_LOG_PATH + 'co2.log')
    raw_dht11 = observe_throughput(pc_observer_2,
                                   SensorRead(esp_32_4, 'dht11'), DATA_LOG_PATH + 'dht11.log')
    raw_ultrasonic = observe_throughput(pc_observer_3,
                                        SensorRead(esp_32_5, 'ultrasonic'), DATA_LOG_PATH + 'ultrasonic.log')
    raw_rotary_encoder = observe_throughput(pc_observer_4,
                                            SensorRead(esp_32_1, 'rotary_encoder'), DATA_LOG_PATH + 'rotary_encoder.log')
    raw_button = delay_observer.input(observe_throughput(pc_observer_5,
                                                         SensorRead(esp_32_2, 'button'), DATA_LOG_PATH + 'button.log'))

    selection_int = Map(esp_32_1, raw_rotary_encoder.out0, eval_str='int(x/2) % 3')

    button_filtered = ButtonFilter(esp_32_2, raw_button.out0, flip_threshold=1)
    button_single_emit = ButtonToSingleEmit(esp_32_2, button_filtered.out0)

    joined_selection = JoinWithDupFilter(pc_local, selection_int.out0, button_single_emit.out0, eval_str='(x, y)')

    duplicator_0 = Duplicate(pc_local, joined_selection.out0)
    duplicator_1 = Duplicate(pc_local, duplicator_0.out0)

    co2_toggle = ToggleState(pc_local, duplicator_0.out1, eval_str='x[0]==0 and x[1]', initial_state=True)
    temperature_toggle = ToggleState(pc_local, duplicator_1.out0, eval_str='x[0]==1 and x[1]', initial_state=True)
    distance_toggle = ToggleState(pc_local, duplicator_1.out1, eval_str='x[0]==2 and x[1]', initial_state=True)

    co2_filtered = Map(esp_32_3, raw_co2.out0, eval_str='x[2] > 0')
    temperature_filtered = Map(esp_32_4, raw_dht11.out0, eval_str='x[0] > 45')
    distance_filtered = Map(esp_32_5, raw_ultrasonic.out0, eval_str='x[0] is not -1 and x[1] < 10')

    co2_bool = JoinWithDupFilter(pc_local, co2_toggle.out0, co2_filtered.out0, eval_str='y if x else False')
    dht11_bool = JoinWithDupFilter(pc_local, temperature_toggle.out0, temperature_filtered.out0, eval_str='y if x else False')
    ultrasonic_bool = JoinWithDupFilter(pc_local, distance_toggle.out0, distance_filtered.out0, eval_str='False if x else False')  # y if x else False

    joined = JoinWithDupFilter(pc_local, co2_bool.out0, dht11_bool.out0, eval_str='x or y')
    alarm_ser = delay_observer.output(observe_throughput(pc_observer_6,
                                                         JoinWithDupFilter(pc_local, joined.out0, ultrasonic_bool.out0, eval_str='x or y'), DATA_LOG_PATH + 'total.log'))

    output = PrintQueue(pc_local, alarm_ser.out0, time_frame=100)

    return output.build_distribution('0')
