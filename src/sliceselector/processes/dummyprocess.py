import time
from sliceselector.processes.process import Process


class DummyProcess(Process):
    def __init__(self):
        super(DummyProcess, self).__init__(inputs=None, output=None)
        self._n = 10

    def execute(self):
        out = []
        for i in range(self._n):
            if self.is_canceled():
                return out
            time.sleep(0.25)
            out.append(i)
            self.progress.emit(i, self._n)
        return out
