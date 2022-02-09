from lh_lib.graph.user.nodes import Duplicate, ThroughputObserver, CaseStudyDelayObserver, MonitorLatest, PrintQueue


"""
Only SingleOutputNodes are currently observable
"""


def observe_throughput(device, node, filepath=False):
    dup = Duplicate(node.device, node)
    ThroughputObserver(device, dup, filepath)
    return dup


class CaseStudyDelayObserverBuilder:

    def __init__(self, device, filepath=False):
        self.device = device
        self.filepath = filepath
        self.dup = None

    def input(self, node):
        self.dup = Duplicate(node.device, node)
        return self.dup

    def output(self, node):
        dup_2 = Duplicate(node.device, node)
        CaseStudyDelayObserver(self.device, self.dup, dup_2, self.filepath)
        return dup_2


def monitor_latest(device, node):
    dup = Duplicate(node.device, node)
    MonitorLatest(device, dup)
    return dup


def print_queue(device, node, time_frame=1000):
    dup = Duplicate(node.device, node)
    PrintQueue(device, dup, time_frame=time_frame)
    return dup
