from lh_lib.graph.objects import Node, Edge, StrFormatIter
from lh_lib.user_node_types import NoInputSingleOutputUserNode


def topological_sort_old():
    # get all node and device instances
    all_nodes = Node.instances

    # holds sorted node list in reverse order
    node_stack = []
    # dict to store visited information about each node
    visited = {node: False for node in all_nodes}

    # recursive function for depth first behaviour
    def recursive_util(n):
        visited[n] = True

        for param in StrFormatIter('out'):
            if param in n.kwargs:
                if not visited[n.kwargs[param].node_to]:
                    recursive_util(n.kwargs[param].node_to)
            else:
                break

        # add node after each following node is already added
        node_stack.append(n)

    # simply iterate over all nodes. Gives one possible topologically correct order.
    for node in all_nodes:
        if not visited[node]:
            recursive_util(node)

    # reversed stack is correct order where input nodes to the graph are first
    return get_device_list(node_stack[::-1]), node_stack[::-1]


def topological_sort():
    # start with all source nodes
    node_list = [n for n in Node.instances if issubclass(n.user_class, NoInputSingleOutputUserNode)]

    # edge set to remove visited edges
    edge_set = set(Edge.instances)

    # final node list in a topologically correct order
    result_node_list = []

    while len(node_list) > 0:
        node = node_list.pop(0)
        result_node_list.append(node)

        for out_param in StrFormatIter('out'):
            if out_param not in node.kwargs:
                break

            next_edge = node.kwargs[out_param]

            if next_edge in edge_set:
                edge_set.remove(next_edge)

                next_node = next_edge.node_to

                no_incoming_edges = True
                for in_param in StrFormatIter('in'):
                    if in_param not in next_node.kwargs:
                        break

                    if next_node.kwargs[in_param] in edge_set:
                        no_incoming_edges = False
                        break

                if no_incoming_edges:
                    node_list.append(next_node)

    if not edge_set:
        return get_device_list(result_node_list), result_node_list
    else:
        raise Exception("circular dependencies in graph")


def get_device_list(sorted_node_list):
    device_result_list = []

    def is_device_in_sources_of(node, device):
        if node.device == device:
            return True

        is_device_in_sources = False

        for in_param in StrFormatIter('in'):
            if in_param not in node.kwargs:
                break

            is_device_in_sources |= is_device_in_sources_of(node.kwargs[in_param].node_from, device)

        return is_device_in_sources

    for node in sorted_node_list:
        if node.device in device_result_list:
            devices_in_front = []
            devices_in_back = []

            for device in device_result_list[device_result_list.index(node.device)+1:]:
                if is_device_in_sources_of(node, device):
                    devices_in_front.append(device)
                else:
                    devices_in_back.append(device)

            device_result_list = \
                device_result_list[:device_result_list.index(node.device)] + \
                devices_in_front + \
                [node.device] + \
                devices_in_back
        else:
            device_result_list.append(node.device)

    return device_result_list
