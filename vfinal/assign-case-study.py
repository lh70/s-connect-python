"""
utility script to clear or assign case study assignments
"""

import os
import sys

try:
    from lh_lib.exceptions import AcknowledgementException
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.exceptions import AcknowledgementException


def run():
    if len(sys.argv) < 2:
        raise Exception('please provide a case study selector!')

    if sys.argv[1] == '1':
        from case_studies.case_study_1 import get_distribution
    elif sys.argv[1] == '2':
        from case_studies.case_study_2 import get_distribution
    elif sys.argv[1] == '3':
        from case_studies.case_study_3 import get_distribution
    else:
        raise Exception(f'unknown case study selector {sys.argv[1]}')

    ordered_devices, distribution = get_distribution()

    if len(sys.argv) == 3:
        if sys.argv[2] == 'order':
            for device in ordered_devices:
                print(f'{device.host}:{device.port}')
        elif sys.argv[2] == 'clear':
            print('clearing assignment')
            for device in ordered_devices:
                try:
                    device.remove_assignment('0')
                except (AcknowledgementException, TimeoutError, ConnectionRefusedError):
                    raise Exception(
                        f'Fatal Error: device {device.host}:{device.port} is not reachable. Please check if Framework is running.')
        else:
            raise Exception(f'unknown command: {sys.argv[1]}')
    else:
        print('removing old assignments')
        for device in ordered_devices:
            try:
                device.remove_assignment('0')
            except (AcknowledgementException, TimeoutError, ConnectionRefusedError):
                raise Exception(
                    f'Fatal Error: device {device.host}:{device.port} is not reachable. Please check if Framework is running.')

        print('assigning new assignment')
        for device in ordered_devices:
            try:
                device.distribute_assignment(distribution)
            except AcknowledgementException:
                raise Exception(
                    f'Fatal Error: device {device.host}:{device.port} is not answering. Probably a fatal error occurred on the device. Please check.')


if __name__ == "__main__":
    run()
