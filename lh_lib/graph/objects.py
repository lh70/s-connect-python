import re


class Node:
    instances = []

    def __init__(self, device, **kwargs):
        Node.instances.append(self)

        self.device = device
        self.kwargs = kwargs

        for kw, value in self.kwargs.items():
            if re.match('^in[0-9]+$', kw):
                # value is from_node, self is to_node
                edge = Edge(value, self)

                # replace node with equivalent edge id
                self.kwargs[kw] = edge.id

                # add edge id to kwargs of other node
                # add reference of self to other node to make a from -> to traversal possible
                if isinstance(value, SingleOutputNode):
                    if 'out0' in value.kwargs:
                        raise Exception(f'Node {value} has too many outputs assigned')
                    else:
                        value.kwargs['out0'] = edge.id
                        value.out0 = self
                elif isinstance(value, DualOutputNode):
                    if 'out0' not in value.kwargs:
                        value.kwargs['out0'] = edge.id
                        value.out0 = self
                    elif 'out1' not in value.kwargs:
                        value.kwargs['out1'] = edge.id
                        value.out1 = self
                    else:
                        raise Exception(f'Node {value} has too many outputs assigned')


class NoOutputNode(Node):
    pass


class SingleOutputNode(Node):

    def __init__(self, device, **kwargs):
        super().__init__(device, **kwargs)
        self.out0 = None


class DualOutputNode(Node):

    def __init__(self, device, **kwargs):
        super().__init__(device, **kwargs)
        self.out0 = None
        self.out1 = None


class Edge:
    instances = []
    id_counter = 0

    def __init__(self, node_from, node_to):
        Edge.instances.append(self)

        self.id = str(Edge.id_counter)
        Edge.id_counter += 1

        self.node_from = node_from
        self.node_to = node_to
