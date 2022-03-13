from lh_lib.graph.objects import Edge
from lh_lib.graph.ordering import topological_sort
from lh_lib.graph.device import Device


def build_distribution(assignment_id):
    # get all device instances
    all_devices = Device.instances

    distribution = {device: {'id': assignment_id, 'pipelines': {}, 'processing': []} for device in all_devices}

    # distribution gets enriched
    ordered_devices = _build_processing(distribution)
    _build_pipelines(distribution)

    return ordered_devices, distribution


def _build_processing(distribution):
    # get a topological correct order of the nodes
    ordered_devices, ordered_nodes = topological_sort()

    for node in ordered_nodes:
        # check function signature of nodes once before adding them to distribution
        node.check_signature()
        distribution[node.device]['processing'].append(node.get_serializable())

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
        device_from, pipeline_from, device_to, pipeline_to = edge.get_serializable()

        distribution[device_from]['pipelines'][edge.id] = pipeline_from
        distribution[device_to]['pipelines'][edge.id] = pipeline_to
