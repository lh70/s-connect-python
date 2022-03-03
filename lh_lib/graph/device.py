from lh_lib.network_stack.client import Client


class Device:

    instances = []
    device_counter = 0

    def __init__(self, host='localhost', port=8090, max_time_frame=100, max_values_per_time_frame=0):
        self.id = str(Device.device_counter)
        Device.device_counter += 1

        for device in Device.instances:
            if device.host == host and device.port == port:
                raise Exception("Devices {} and {} has same host/port configuration".format(device.id, self.id))

        Device.instances.append(self)
        self.host = host
        self.port = port
        self.max_time_frame = max_time_frame
        self.max_values_per_time_frame = max_values_per_time_frame

    def remove_assignment(self, assignment_id):
        conn = Client(self.host, self.port)
        conn.send({'remove-assignment': {'assignment-id': assignment_id}})
        conn.recv_acknowledgement()
        conn.close()

    def distribute_assignment(self, distribution):
        conn = Client(self.host, self.port)
        conn.send({'processing-assignment': distribution[self]})
        conn.recv_acknowledgement()
        conn.close()

    def __repr__(self):
        return f"Device {self.id}"
