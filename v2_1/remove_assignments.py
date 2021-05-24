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
micropython_worker_conn.socket.close()

micropython_worker_conn = Client('localhost', 8090)
micropython_worker_conn.send({
    'remove-assignment': {
        'assignment-id': '1'
    }
})
micropython_worker_conn.recv_acknowledgement()
micropython_worker_conn.socket.close()

micropython_worker_conn = Client('localhost', 8091)
micropython_worker_conn.send({
    'remove-assignment': {
        'assignment-id': '1'
    }
})
micropython_worker_conn.recv_acknowledgement()
micropython_worker_conn.socket.close()
