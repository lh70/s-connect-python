from lh_lib.user_nodes import SensorRead, PrintQueue, Join, Map, ButtonFilter, ButtonToSingleEmit, Duplicate, ToggleState
from lh_lib.user_distribution import Device

from lh_lib.user_nodes_utility import observe_throughput, CaseStudyDelayObserverBuilder, monitor_latest, print_queue


def get_distribution():
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
    pc_observer_6 = Device('192.168.2.163', 8106, time_frame)

    delay_observer = CaseStudyDelayObserverBuilder(pc_observer_0, 'D:/temp/delay.log')

    raw_co2 = observe_throughput(pc_observer_1,
                                 SensorRead(esp_32_1, 'co2'), 'D:/temp/co2.log')
    raw_dht11 = observe_throughput(pc_observer_2,
                                   SensorRead(esp_32_2, 'dht11'), 'D:/temp/dht11.log')
    raw_ultrasonic = observe_throughput(pc_observer_3,
                                        SensorRead(esp_32_3, 'ultrasonic'), 'D:/temp/ultrasonic.log')
    raw_rotary_encoder = observe_throughput(pc_observer_4,
                                            SensorRead(esp_32_4, 'rotary_encoder'), 'D:/temp/rotary_encoder.log')
    raw_button = delay_observer.input(observe_throughput(pc_observer_5,
                                                         SensorRead(esp_32_5, 'button'), 'D:/temp/button.log'))

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
    alarm_ser = delay_observer.output(observe_throughput(pc_observer_6,
                                                         Join(pc_local, joined.out0, ultrasonic_bool.out0, eval_str='x or y'), 'D:/temp/total.log'))

    output = PrintQueue(pc_local, alarm_ser.out0, time_frame=100)

    return output.build_distribution('0')
