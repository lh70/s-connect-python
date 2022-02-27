from lh_lib.graph.objects import Edge
from lh_lib.graph.ordering import topological_sort
from lh_lib.graph.user.device import Device

import inspect


def build_distribution(assignment_id):
    # get all device instances
    all_devices = Device.instances

    distribution = {device: {'assignment-id': assignment_id, 'pipelines': {}, 'processing': []} for device in all_devices}

    # distribution gets enriched
    ordered_devices = _build_processing(distribution)
    _build_pipelines(distribution)

    return ordered_devices, distribution


def _build_processing(distribution):
    # get a topological correct order of the nodes
    ordered_devices, ordered_nodes = topological_sort()

    for node in ordered_nodes:
        # distribution[node.device]['processing'].append({'class': type(node).__name__, 'kwargs': node.kwargs})
        distribution[node.device]['processing'].append({'class': type(node).__name__, 'kwargs': node.kwargs, 'code': inspect.getsource(node.__class__)})

    return ordered_devices


def _build_pipelines(distribution):
    """
    Builds the pipelines from edge information.
    Adds the information to the distribution dictionary (device -> assignment-dict()).
    Distribution dictionary ground structure must already exist. Adds just the pipeline part.
    """

    # get all edge instances
    all_edges = Edge.instances

    for edge in all_edges:
        if edge.node_from.device == edge.node_to.device:
            distribution[edge.node_from.device]['pipelines'][edge.id] = {'type': 'local'}
            distribution[edge.node_to.device]['pipelines'][edge.id] = {'type': 'local'}
        elif edge.node_from.device.host == edge.node_to.device.host:
            distribution[edge.node_from.device]['pipelines'][edge.id] = {'type': 'output'}
            distribution[edge.node_to.device]['pipelines'][edge.id] = {
                'type': 'input',
                'host': 'localhost',
                'port': edge.node_from.device.port,
                'time-frame': edge.node_to.device.max_time_frame,
                'values-per-time-frame': edge.node_to.device.max_values_per_time_frame
            }
        else:
            distribution[edge.node_from.device]['pipelines'][edge.id] = {'type': 'output'}
            distribution[edge.node_to.device]['pipelines'][edge.id] = {
                'type': 'input',
                'host': edge.node_from.device.host,
                'port': edge.node_from.device.port,
                'time-frame': edge.node_to.device.max_time_frame,
                'values-per-time-frame': edge.node_to.device.max_values_per_time_frame
            }
