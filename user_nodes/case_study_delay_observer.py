import os

from lh_lib.time import ticks_ms, ticks_ms_diff_to_current
from lh_lib.logging import DataLogger


def case_study_delay_observer(in0, in1, filepath=False, storage=None):
    if 'latest_in0' not in storage:
        storage['latest_in0'] = False
        storage['latest_in1'] = False
        storage['queue'] = []
        storage['time_delays'] = []
        if filepath:
            storage['file'] = DataLogger(filepath)

        os.system('cls' if os.name == 'nt' else 'clear')
        print('Case Study Delay Observer\n\nInit')

    for i in in0:
        if i and not storage['latest_in0']:  # on rising edge <==> False->True <==> button pressed
            if len(storage['queue']) == 0 or ticks_ms_diff_to_current(storage['queue'][-1]) > 10:  # filter flickering
                storage['queue'].append(ticks_ms())
        storage['latest_in0'] = i

    for i in in1:
        if i != storage['latest_in1']:  # on flipped state <==> True->False or False->True
            if len(storage['queue']) > 0:  # should be always true at this moment, if not: ignore this flip
                '''
                # old approach
                delay = ticks_ms_diff_to_current(storage['queue'].pop(0))
                while delay > 1000 and len(storage['queue']) > 0:  # case study presses button about every 2 seconds. if flickering got through, it should not pass this test
                    delay = ticks_ms_diff_to_current(storage['queue'].pop(0))
                storage['time_delays'].append(delay)
                '''
                # new approach. delay is < 2 seconds, so only one item should be in list, every other item is flickering, so take the first and delete the others
                storage['time_delays'].append(ticks_ms_diff_to_current(storage['queue'][0]))
                storage['queue'].clear()

        storage['latest_in1'] = i

    if len(storage['time_delays']) > 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Case Study Delay Observer\n\ntime delay: {}, queue: {}'.format(storage['time_delays'], storage['queue']))

        if filepath:
            file = storage['file']
            for delay in storage['time_delays']:
                file.add(delay)

        storage['time_delays'].clear()

    in0.clear()
    in1.clear()
