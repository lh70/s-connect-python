from lh_lib.network import Client

class Distributor:

    def build_distributed_assignment(self, assignment, devices, distribution):
        assignment_order = []
        pipeline_exchange = {}
        distribution_assignments = {}
        for device_id in devices:
            distribution_assignments[device_id] = {'assignment-id': assignment['assignment-id'], 'pipelines': {}, 'processing': []}

        for device_id, proc_list in distribution:
            assignment_order.append(device_id)
            device_attrs = devices[device_id]

            for proc_id in proc_list:
                proc = assignment['processing'][proc_id]
                proc_kwargs = proc['kwargs']

                distribution_assignments[device_id]['processing'].append(proc)

                for kw, pipe_id in proc_kwargs.items():
                    if pipe_id in assignment['pipelines']:
                        # currently no check for double usage
                        distribution_assignments[device_id]['pipelines'][pipe_id] = assignment['pipelines'][pipe_id]
                        # del assignment['pipelines'][pipe_id] possible but needs check for side effects
                    elif kw.startswith('out'):
                        assert pipe_id not in pipeline_exchange
                        pipeline_exchange[pipe_id] = device_id
                    else:
                        assert pipe_id in pipeline_exchange
                        output_device_id = pipeline_exchange[pipe_id]
                        output_device_attrs = devices[output_device_id]
                        if device_attrs['host'] == output_device_attrs['host'] and device_attrs['port'] == output_device_attrs['port']:
                            distribution_assignments[device_id]['pipelines'][pipe_id] = {'type': 'local'}
                            distribution_assignments[output_device_id]['pipelines'][pipe_id] = {'type': 'local'}
                        elif device_attrs['host'] == output_device_attrs['host']:
                            distribution_assignments[device_id]['pipelines'][pipe_id] = {
                                'type': 'input',
                                'host': 'localhost',
                                'port': output_device_attrs['port'],
                                'time-frame': device_attrs['max-input-time-frame'],
                                'values-per-time-frame': device_attrs['max-input-values-per-time-frame']
                            }
                            distribution_assignments[output_device_id]['pipelines'][pipe_id] = {'type': 'output'}
                            del pipeline_exchange[pipe_id]
                        else:
                            distribution_assignments[device_id]['pipelines'][pipe_id] = {
                                'type': 'input',
                                'host': output_device_attrs['host'],
                                'port': output_device_attrs['port'],
                                'time-frame': device_attrs['max-input-time-frame'],
                                'values-per-time-frame': device_attrs['max-input-values-per-time-frame']
                            }
                            distribution_assignments[output_device_id]['pipelines'][pipe_id] = {'type': 'output'}
                            del pipeline_exchange[pipe_id]
        return distribution_assignments, assignment_order

    def distribute_assignments(self, distribution_assignments, assignment_order, devices):
        for device_id in assignment_order:
            assignment = distribution_assignments[device_id]
            host, port = devices[device_id]['host'], devices[device_id]['port']
            conn = Client(host, port)
            conn.send({'remove-assignment': {'assignment-id': assignment['assignment-id']}})
            conn.recv_acknowledgement()
            conn.send({'processing-assignment': assignment})
            conn.recv_acknowledgement()
            conn.socket.close()

    def remove_assignments(self, assignment_id, devices):
        for device_attrs in devices.values():
            conn = Client(device_attrs['host'], device_attrs['port'])
            conn.send({'remove-assignment': {'assignment-id': assignment_id}})
            conn.recv_acknowledgement()
            conn.socket.close()
