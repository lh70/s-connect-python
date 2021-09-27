from lh_lib.user_processes import Duplicate, ThroughputObserver, DelayObserver, Monitor, MonitorLatest, PrintQueue, CaseStudyDelayObserver


def observe_throughput(device, pipe):
    dup = Duplicate(pipe.process_out.device, pipe)
    ThroughputObserver(device, dup.out0)
    return dup.out1


class ObserveDelay:

    def __init__(self, device):
        self.device = device
        self.dup_input = None

    def input(self, pipe):
        self.dup_input = Duplicate(pipe.process_out.device, pipe)
        return self.dup_input.out1

    def output(self, pipe):
        dup_output = Duplicate(pipe.process_out.device, pipe)
        CaseStudyDelayObserver(self.device, self.dup_input.out0, dup_output.out0)
        return dup_output.out1


def monitor(device, pipe):
    dup = Duplicate(pipe.process_out.device, pipe)
    MonitorLatest(device, dup.out0)
    return dup.out1


def print_pipe(device, pipe):
    dup = Duplicate(pipe.process_out.device, pipe)
    PrintQueue(device, dup.out0, time_frame=100)
    return dup.out1
