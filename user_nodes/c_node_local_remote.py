from lh_lib.user_node_types import DualInputSingleOutputUserNode


class CNodeLocalRemote(DualInputSingleOutputUserNode):

    def __init__(self, in0, in1, out0, module):
        super().__init__(in0, in1, out0)

        if '.' in module:
            self.module = __import__(module, fromlist=[''])
        else:
            self.module = __import__(module)

        self.module.startup()

    def run(self):
        self._run_zip()
        self._run_rest()
        self.in0.clear()
        self.in1.clear()

    def _run_zip(self):
        for x, y in zip(self.in0, self.in1):
            out = self.module.local_graph(x)

            if out is not None:
                self.out0.append(out)

            out = self.module.remote_graph(y)

            if out is not None:
                self.out0.append(out)

    def _run_rest(self):
        if len(self.in0) > len(self.in1):
            del self.in0[:len(self.in1)]

            for x in self.in0:
                out = self.module.local_graph(x)

                if out is not None:
                    self.out0.append(out)

        elif len(self.in1) > len(self.in0):
            del self.in1[:len(self.in0)]

            for y in self.in1:
                out = self.module.remote_graph(y)

                if out is not None:
                    self.out0.append(out)
