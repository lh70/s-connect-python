from lh_lib.graph.objects import Node
from user_nodes.duplicate import duplicate
from user_nodes.throughput_observer import throughput_observer
from user_nodes.case_study_delay_observer import case_study_delay_observer
from user_nodes.monitor_latest import monitor_latest
from user_nodes.print_queue import print_queue


def observe_throughput(device, node, filepath=False):
    dup = Node(device, duplicate, [node])
    Node(device, throughput_observer, [dup], filepath=filepath)

    return dup


class CaseStudyDelayObserverBuilder:

    def __init__(self, device, filepath=False):
        self.device = device
        self.filepath = filepath
        self.dup = None

    def input(self, node):
        self.dup = Node(node.device, duplicate, [node])
        return self.dup

    def output(self, node):
        dup_2 = Node(node.device, duplicate, [node])
        Node(self.device, case_study_delay_observer, [self.dup, dup_2], filepath=self.filepath)
        return dup_2


def monitor_latest_drop_in(device, node):
    dup = Node(node.device, duplicate, [node])
    Node(device, monitor_latest, [dup])
    return dup


def print_queue_drop_in(device, node, time_frame=1000):
    dup = Node(node.device, duplicate, [node])
    Node(device, print_queue, [dup], time_frame=time_frame)
    return dup
