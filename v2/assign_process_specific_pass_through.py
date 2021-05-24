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
        'assignment-kind': 'raw-sensor-data',
        'output-pipe-id-list': ['1'],
        'sensor': 'rotary_encoder'
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
        'assignment-kind': 'pass-through',
        'output-pipe-id-list': ['2'],
        'input-pipe-host': '192.168.2.177',
        'input-pipe-port': 8090,
        'input-pipe-id': '1',
        'input-pipe-time-frame': 100,
        'input-pipe-values-per-time-frame': 0
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
        'assignment-kind': 'sensor-printout',
        'output-pipe-id-list': [],
        'input-pipe-host': 'localhost',
        'input-pipe-port': 8091,
        'input-pipe-id': '2',
        'input-pipe-time-frame': 100,
        'input-pipe-values-per-time-frame': 0
    }
})
desktop_worker_conn.recv_acknowledgement()
desktop_worker_conn.socket.close()


'''
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
        'assignment-kind': 'sensor-printout',
        'output-pipe-id-list': [],
        'input-pipe-host': '192.168.2.177',
        'input-pipe-port': 8090,
        'input-pipe-id': '1',
        'input-pipe-time-frame': 10,
        'input-pipe-values-per-time-frame': 0
    }
})
desktop_worker_conn.recv_acknowledgement()
desktop_worker_conn.socket.close()
'''
