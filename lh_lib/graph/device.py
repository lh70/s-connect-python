import json

from lh_lib.base.network_stack.client import Client


class Device:

    instances = []
    device_counter = 0

    def __init__(self, host='localhost', port=8090, time_frame_ms=100, heartbeat_ms=100):
        self.id = str(Device.device_counter)
        Device.device_counter += 1

        for device in Device.instances:
            if device.host == host and device.port == port:
                raise Exception('Devices {} and {} has same host/port configuration'.format(device.id, self.id))

        Device.instances.append(self)
        self.host = host
        self.port = port
        self.time_frame_ms = time_frame_ms
        self.heartbeat_ms = heartbeat_ms

    def remove_assignment(self, assignment_id):
        conn = Client(self.host, self.port)
        conn.send({'type': 'remove_assignment', 'content': {'id': assignment_id}})
        conn.recv_acknowledgement()
        conn.close()

    def distribute_assignment(self, distribution):
        conn = Client(self.host, self.port)
        conn.send({'type': 'add_assignment', 'content': distribution[self]})
        conn.recv_acknowledgement()
        conn.close()

    def __repr__(self):
        return 'Device {} {}:{}'.format(self.id, self.host, self.port)

    def toJSON(self):
        return json.dumps({
            'host': self.host,
            'port': self.port,
            'time_frame_ms': self.time_frame_ms,
            'heartbeat_ms': self.heartbeat_ms
        })
