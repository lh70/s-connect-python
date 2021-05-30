try:
    import usys as sys
except ImportError:
    import sys

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if not RUNNING_MICROPYTHON:
    import os
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))


from lh_lib.network import Client


micropython_worker_conn = Client('192.168.2.177', 8090)
micropython_worker_conn.send({
    'remove-assignment': {
        'assignment-id': '1'
    }
})
micropython_worker_conn.recv_acknowledgement()
micropython_worker_conn.send({
    'processing-assignment': {
        'assignment-id': '1',
        'pipelines': {
            'sensor0': {'type': 'sensor', 'sensor-name': 'co2'},
            'pipe0': {'type': 'local'},
            'print0': {'type': 'print', 'time-frame': 0, 'values-per-time-frame': 0}
        },
        'processing': [
            {
                'method': 'pass_through',
                'kwargs': {'in0': 'sensor0', 'out0': 'pipe0'}
            },
            {
                'method': 'pass_through',
                'kwargs': {'in0': 'pipe0', 'out0': 'print0'}
            }
        ]
    }
})
micropython_worker_conn.recv_acknowledgement()
micropython_worker_conn.socket.close()
