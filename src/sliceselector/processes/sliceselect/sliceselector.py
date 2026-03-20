from sliceselector.processes.sliceselect.result import Result


class SliceSelector:
    def __init__(self, scan):
        self._scan = scan

    def run(self):
        data = '/path/to/slice'
        errors = []
        return Result(data, errors)