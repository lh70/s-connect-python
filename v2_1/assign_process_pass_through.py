"""
Needs:
* one micropython worker ('192.168.2.177', 8090) with sensor 'rotary_encoder'
* one desktop worker ('localhost', 8090)
* one desktop worker ('localhost', 8091)
"""

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
            'pipe0': {'type': 'output'}
        },
        'processing': [
            {
                'method': 'pass_through',
                'kwargs': {'in0': 'sensor0', 'out0': 'pipe0'}
            }
        ],
    }
})
micropython_worker_conn.recv_acknowledgement()
micropython_worker_conn.socket.close()


desktop_worker_conn = Client('localhost', 8091)
desktop_worker_conn.send({
    'remove-assignment': {
        'assignment-id': '1'
    }
})
desktop_worker_conn.recv_acknowledgement()
desktop_worker_conn.send({
    'processing-assignment': {
        'assignment-id': '1',
        'pipelines': {
            'pipe0': {'type': 'input', 'host': '192.168.2.177', 'port': 8090, 'time-frame': 0, 'values-per-time-frame': 0},
            'pipe1': {'type': 'output'}
        },
        'processing': [
            {
                'method': 'pass_through',
                'kwargs': {'in0': 'pipe0', 'out0': 'pipe1'}
            }
        ],
    }
})
desktop_worker_conn.recv_acknowledgement()
desktop_worker_conn.socket.close()


desktop_worker_conn = Client('localhost', 8090)
desktop_worker_conn.send({
    'remove-assignment': {
        'assignment-id': '1'
    }
})
desktop_worker_conn.recv_acknowledgement()
desktop_worker_conn.send({
    'processing-assignment': {
        'assignment-id': '1',
        'pipelines': {
            'pipe1': {'type': 'input', 'host': 'localhost', 'port': 8091, 'time-frame': 0, 'values-per-time-frame': 0},
            'print0': {'type': 'print', 'time-frame': 0, 'values-per-time-frame': 0}
        },
        'processing': [
            {
                'method': 'pass_through',
                'kwargs': {'in0': 'pipe1', 'out0': 'print0'}
            }
        ],
    }
})
desktop_worker_conn.recv_acknowledgement()
desktop_worker_conn.socket.close()
