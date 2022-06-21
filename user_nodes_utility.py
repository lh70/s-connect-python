from lh_lib.graph.objects import Node
from user_nodes.duplicate import Duplicate
from user_nodes.throughput_observer import ThroughputObserver
from user_nodes.case_study_delay_observer import CaseStudyDelayObserver
from user_nodes.monitor_latest import MonitorLatest
from user_nodes.print_queue import PrintQueue


def observe_throughput(device, node, filepath=False):
    dup = Node(device, Duplicate, [node])
    Node(device, ThroughputObserver, [dup], filepath=filepath)

    return dup


class CaseStudyDelayObserverBuilder:

    def __init__(self, device, filepath=False):
        self.device = device
        self.filepath = filepath
        self.dup = None

    def input(self, node):
        self.dup = Node(node.device, Duplicate, [node])
        return self.dup

    def output(self, node):
        dup_2 = Node(node.device, Duplicate, [node])
        Node(self.device, CaseStudyDelayObserver, [self.dup, dup_2], filepath=self.filepath)
        return dup_2


def monitor_latest_drop_in(device, node):
    dup = Node(node.device, Duplicate, [node])
    Node(device, MonitorLatest, [dup])
    return dup


def print_queue_drop_in(device, node, time_frame=1000):
    dup = Node(node.device, Duplicate, [node])
    Node(device, PrintQueue, [dup], time_frame=time_frame)
    return dup
