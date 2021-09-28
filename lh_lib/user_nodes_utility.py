from lh_lib.user_nodes import Duplicate, ThroughputObserver, CaseStudyDelayObserver, MonitorLatest, PrintQueue


"""
Only SingleOutputNodes are currently observable
"""


def observe_throughput(device, node, filepath=False):
    dup = Duplicate(node.device, node.out0)
    ThroughputObserver(device, dup.out1, filepath)
    return dup


class CaseStudyDelayObserverBuilder:

    def __init__(self, device, filepath=False):
        self.device = device
        self.filepath = filepath
        self.dup = None

    def input(self, node):
        self.dup = Duplicate(node.device, node.out0)
        return self.dup

    def output(self, node):
        dup_2 = Duplicate(node.device, node.out0)
        CaseStudyDelayObserver(self.device, self.dup.out1, dup_2.out1, self.filepath)
        return dup_2


def monitor_latest(device, node):
    dup = Duplicate(node.device, node.out0)
    MonitorLatest(device, dup.out1)
    return dup


def print_queue(device, node, time_frame=1000):
    dup = Duplicate(node.device, node.out0)
    PrintQueue(device, dup.out1, time_frame=time_frame)
    return dup
