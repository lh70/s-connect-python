from lh_lib.graph.objects import Node, StrFormatIter


def topological_sort():
    # get all node and device instances
    all_nodes = Node.instances

    # holds sorted node list in reverse order
    node_stack = []
    # device order is inherited from the node order
    device_stack = []
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

        # a device may be the same for multiple nodes, so only add device if not already in stack
        # warning: currently there is no check for circular device dependencies
        if n.device not in device_stack:
            device_stack.append(n.device)

    # simply iterate over all nodes. Gives one possible topologically correct order.
    for node in all_nodes:
        if not visited[node]:
            recursive_util(node)

    # reversed stack is correct order where input nodes to the graph are first
    return device_stack[::-1], node_stack[::-1]
