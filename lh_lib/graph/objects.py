import inspect


class StrFormatIter:
    def __init__(self, string):
        self.string = string

    def __iter__(self):
        self.idx = -1
        return self

    def __next__(self):
        self.idx += 1
        return self.string + str(self.idx)


class Node:
    instances = []

    def __init__(self, device, func, inputs=(), **kwargs):
        Node.instances.append(self)

        self.device = device
        self.kwargs = kwargs
        self.func = func

        for node in inputs:
            # node is from_node, self is to_node
            edge = Edge(node, self)

            # define param for out of loop usage
            param = None

            # find the next unused input parameter (of this node)
            for param in StrFormatIter('in'):
                if param not in self.kwargs:
                    break

            # set linkage id into kwargs
            self.kwargs[param] = edge.id

            # find the next unused output parameter (of the other node)
            for param in StrFormatIter('out'):
                if param not in node.kwargs:
                    break

            # set linkage id into kwargs
            node.kwargs[param] = edge.id
            # add direct reference for ordering traversal. todo: change ordering to use kwargs
            setattr(node, param, self)

    def check_signature(self):
        # checks if the keywords + storage are exactly the function signature
        keywords = set(self.kwargs)
        keywords.add('storage')

        assert keywords == set(inspect.signature(self.func).parameters)


class Edge:
    instances = []
    id_counter = 0

    def __init__(self, node_from, node_to):
        Edge.instances.append(self)

        self.id = str(Edge.id_counter)
        Edge.id_counter += 1

        self.node_from = node_from
        self.node_to = node_to
