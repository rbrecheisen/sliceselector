import time
from sliceselector.processes.process import Process


class SelectSliceProcess(Process):
    def __init__(self, inputs, output):
        super(SelectSliceProcess, self).__init__(inputs, output)
        self._scans = inputs.get('scans', {})

    def execute(self):
        nr_steps = len(self._scans.keys())
        step = 0
        for suid in self._scans.keys():
            if self.is_canceled():
                return 'CANCELED'
            self.progress.emit(step, nr_steps)
            step += 1
        return 'OK'