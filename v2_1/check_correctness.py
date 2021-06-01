try:
    import usys as sys
except ImportError:
    import sys

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if not RUNNING_MICROPYTHON:
    import os
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))

import lh_lib.processing


class Checker:

    """
    This checks if an assignment is correctly formatted or
    has any (theoretically) invalid pipelines.

    pipelines must use 'local' if ip and port are the same.
    pipelines should use localhost and port if the ip is the same, but the port differs.
    pipelines can use full ip and port if ip is the same, but the port differs, which will result in an optimisation warning.
    pipelines must use full ip and port if ip differs.

    no unused pipelines.
    no undefined, but used pipelines. (may be a circular dependency)

    no circular dependency,
        because it will crash on assignment (input pipelines are not yet defined on the output side)
        list order is assignment order, which makes the check easy: any used input pipeline must either be sensor or
        already defined as an output pipeline earlier.

    configurations:list((ip, port, configuration-dictionary))
    """
    @classmethod
    def check(cls, configurations):
        cls.check_static_integrity(configurations)
        cls.check_dynamic_integrity(configurations)
        return True

    @classmethod
    def check_dynamic_integrity(cls, configurations):
        known_configurations = {}
        pipeline_usages = {}
        assignment_id = None

        for ip, port, configuration in configurations:
            # one configuration per device
            assert (ip, port) not in known_configurations

            # expand comparing structures
            known_configurations[(ip, port)] = configuration
            pipeline_usages[(ip, port)] = {}

            # first assignment-id is reference
            if assignment_id is None:
                assignment_id = configuration['assignment-id']
            # all other assignment-ids must be equal to first
            else:
                assert assignment_id == configuration['assignment-id']

            # add all pipelines before counting usages to catch unused pipelines (usages==0) and undefined pipelines (usage add fails)
            for pipe_id in configuration['pipelines']:
                pipeline_usages[(ip, port)][pipe_id] = 0

            # check each processing step
            for process in configuration['processing']:
                # check each pipe used by the processing step
                for kw, pipe_id in process['kwargs'].items():
                    # load pipeline configuration
                    pipe_config = configuration['pipelines'][pipe_id]

                    if pipe_config['type'] == 'input':
                        # check input pipeline has correct output pipeline in remote device configuration
                        host = pipe_config['host']
                        if host == 'localhost':
                            host = ip

                        assert known_configurations[(host, pipe_config['port'])]['pipelines'][pipe_id]['type'] == 'output'

                    # count usages of pipeline
                    pipeline_usages[(ip, port)][pipe_id] += 1

            for device, pipelines in pipeline_usages.items():
                for pipe_id, usages in pipelines.items():
                    pipe_type = known_configurations[device]['pipelines'][pipe_id]['type']

                    # local pipelines are referenced exactly twice in one device configuration
                    if pipe_type == 'local':
                        assert usages == 2
                    # all other pipelines are used exactly once
                    else:
                        assert usages == 1

    @classmethod
    def check_static_integrity(cls, configurations):
        for ip, port, configuration in configurations:
            # check if configuration only has known properties
            assert set(configuration.keys()) == {'assignment-id', 'pipelines', 'processing'}

            # check each processing step
            for process in configuration['processing']:
                # check if process only has known properties
                assert set(process.keys()) == {'method', 'kwargs'}

                # check if processing method exists (args signature not checked because micropython does not support inspect module)
                assert hasattr(lh_lib.processing, process['method'])

                # check each pipe used by the processing step
                for kw, pipe_id in process['kwargs'].items():
                    # load pipeline configuration
                    pipe_config = configuration['pipelines'][pipe_id]

                    # check pipeline configuration attributes
                    assert pipe_config['type'] in ('local', 'output', 'sensor', 'print', 'input')
                    if pipe_config['type'] == 'local' or pipe_config['type'] == 'output':
                        assert set(pipe_config.keys()) == {'type'}
                    elif pipe_config['type'] == 'sensor':
                        assert set(pipe_config.keys()) == {'type', 'sensor-name'}
                        assert isinstance(pipe_config['sensor-name'], str)
                    elif pipe_config['type'] == 'print':
                        assert set(pipe_config.keys()) == {'type', 'time-frame', 'values-per-time-frame'}
                        assert isinstance(pipe_config['time-frame'], int)
                        assert isinstance(pipe_config['values-per-time-frame'], int)
                    else:
                        assert set(pipe_config.keys()) == {'type', 'host', 'port', 'time-frame', 'values-per-time-frame'}
                        assert isinstance(pipe_config['host'], str)
                        assert isinstance(pipe_config['port'], int)
                        assert isinstance(pipe_config['time-frame'], int)
                        assert isinstance(pipe_config['values-per-time-frame'], int)

                    # check for correct pipeline type for parameter
                    if kw.startswith('in'):
                        assert pipe_config['type'] in ('sensor', 'local', 'input')
                    else:
                        assert pipe_config['type'] in ('output', 'local', 'print')

                    if pipe_config['type'] == 'input':
                        # check if input pipeline is local, which is illegal and there should be used a local pipeline instead
                        if pipe_config['host'] == ip or pipe_config['host'] == 'localhost':
                            assert not pipe_config['port'] == port


Checker.check([
    ['192.168.2.177', 8090, {
        'assignment-id': '1',
        'pipelines': {
            'sensor0': {'type': 'sensor', 'sensor-name': 'co2'},
            'pipe0': {'type': 'output'}
        },
        'processing': [
            {
                'method': 'pass_through',
                'kwargs': {'in0': 'sensor0', 'out0': 'pipe0'}
            }
        ],
    }],
    ['192.168.2.163', 8091, {
        'assignment-id': '1',
        'pipelines': {
            'pipe0': {'type': 'input', 'host': '192.168.2.177', 'port': 8090, 'time-frame': 0,
                      'values-per-time-frame': 0},
            'pipe1': {'type': 'output'}
        },
        'processing': [
            {
                'method': 'pass_through',
                'kwargs': {'in0': 'pipe0', 'out0': 'pipe1'}
            }
        ],
    }],
    ['192.168.2.163', 8090, {
        'assignment-id': '1',
        'pipelines': {
            'pipe1': {'type': 'input', 'host': 'localhost', 'port': 8091, 'time-frame': 0,
                      'values-per-time-frame': 0},
            'print0': {'type': 'print', 'time-frame': 0, 'values-per-time-frame': 0}
        },
        'processing': [
            {
                'method': 'pass_through',
                'kwargs': {'in0': 'pipe1', 'out0': 'print0'}
            }
        ],
    }]
])
