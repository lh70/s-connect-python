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
        'sensors': {
            's1': {'name': 'co2'}
        },
        'pipelines': {
            'p1': {'type': 'output'}
        },
        'sensor-processing': {
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
        'sensors': {},
        'pipelines': {
            'p1': {'type': 'input', 'host': '192.168.2.177', 'port': 8090, 'time-frame': 0, 'values-per-time-frame': 0},
            'p2': {'type': 'output'}
        },
        'sensor-processing': {},
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
        'sensors': {},
        'pipelines': {
            'p2':     {'type': 'input', 'host': 'localhost', 'port': 8091, 'time-frame': 0, 'values-per-time-frame': 0},
            'print1': {'type': 'print', 'time-frame': 0, 'values-per-time-frame': 0}
        },
        'sensor-processing': {},
        'pipeline-processing': {
            'p2': 'print1'
        },
    }
})
desktop_worker_conn.recv_acknowledgement()
desktop_worker_conn.socket.close()
