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
        'assignment-kind': 'general',
        'input-sensors': {
            's1': {'name': 'rotary_encoder'}
        },
        'input-pipes': {},
        'output-pipe-id-list': ['p1'],
        'print-pipes': {},
        'sensor_processing': {
            's1': 'p1'
        },
        'pipeline-processing': {},
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
        'assignment-kind': 'general',
        'input-sensors': {},
        'input-pipes': {
            'p1': {'host': '192.168.2.177', 'port': 8090, 'time-frame': 100, 'values-per-time-frame': 0}
        },
        'output-pipe-id-list': ['p2'],
        'print-pipes': {},
        'sensor_processing': {},
        'pipeline-processing': {
            'p1': 'p2'
        },
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
        'assignment-kind': 'general',
        'input-sensors': {},
        'input-pipes': {
            'p2': {'host': 'localhost', 'port': 8091, 'time-frame': 100, 'values-per-time-frame': 0}
        },
        'output-pipe-id-list': [],
        'print-pipes': {
            'print1': {'time-frame': 100, 'values-per-time-frame': 0}
        },
        'sensor_processing': {},
        'pipeline-processing': {
            'p2': 'print1'
        },
    }
})
desktop_worker_conn.recv_acknowledgement()
desktop_worker_conn.socket.close()
