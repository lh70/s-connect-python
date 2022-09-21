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

    def __init__(self, device, user_class, inputs=(), **kwargs):
        Node.instances.append(self)

        self.device = device
        self.kwargs = kwargs
        self.user_class = user_class

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
            self.kwargs[param] = edge

            # find the next unused output parameter (of the other node)
            for param in StrFormatIter('out'):
                if param not in node.kwargs:
                    break

            # set linkage id into kwargs
            node.kwargs[param] = edge

    def get_serializable(self):
        kwargs = self.kwargs.copy()

        # iterate through all input edges
        for param in StrFormatIter('in'):
            if param in kwargs:
                kwargs[param] = kwargs[param].id
            else:
                break

        # iterate through all output edges
        for param in StrFormatIter('out'):
            if param in kwargs:
                kwargs[param] = kwargs[param].id
            else:
                break

        with open(inspect.getsourcefile(self.user_class), 'rt') as f:
            full_source_code = f.read()

        return {'class_name': self.user_class.__name__, 'kwargs': kwargs, 'code': full_source_code}

    def check_signature(self):
        signature = inspect.signature(self.user_class)

        malicious_kwargs = set(self.kwargs) - set(signature.parameters)
        if malicious_kwargs:
            raise Exception(f'Kwargs: {malicious_kwargs} are defined without being in function signature of function: {self.user_class.__name__}')

        for name, param in signature.parameters.items():
            if param.kind == param.POSITIONAL_ONLY:
                raise Exception(f'Parameter: {name} of function: {self.user_class.__name__} is POSITIONAL_ONLY, which is not allowed. All Parameters must allow for keyword style supply.')
            if name not in self.kwargs:
                if param.kind == param.VAR_POSITIONAL or param.kind == param.VAR_KEYWORD:
                    pass  # ignore for now or maybe raise exception, because unnecessary parameters should be left out of function signature
                elif param.default == param.empty:
                    raise Exception(f'Parameter: {name} of function: {self.user_class.__name__} has no default value, but is not supplied in kwargs.')


class Edge:
    instances = []
    id_counter = 0

    def __init__(self, node_from, node_to):
        Edge.instances.append(self)

        self.id = str(Edge.id_counter)
        Edge.id_counter += 1

        self.node_from = node_from
        self.node_to = node_to

    def get_serializable(self):
        if self.node_from.device == self.node_to.device:
            pipeline_from_device = {'type': 'local'}
            pipeline_to_device = {'type': 'local'}
        elif self.node_from.device.host == self.node_to.device.host:
            pipeline_from_device = {'type': 'output'}
            pipeline_to_device = {
                'type': 'input',
                'host': 'localhost',
                'port': self.node_from.device.port,
                'time_frame_ms': self.node_to.device.time_frame_ms,
                'heartbeat_ms': self.node_to.device.heartbeat_ms
            }
        else:
            pipeline_from_device = {'type': 'output'}
            pipeline_to_device = {
                'type': 'input',
                'host': self.node_from.device.host,
                'port': self.node_from.device.port,
                'time_frame_ms': self.node_to.device.time_frame_ms,
                'heartbeat_ms': self.node_to.device.heartbeat_ms
            }

        return self.node_from.device, pipeline_from_device, self.node_to.device, pipeline_to_device

