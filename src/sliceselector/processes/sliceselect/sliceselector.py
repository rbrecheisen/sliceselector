from sliceselector.processes.sliceselect.result import Result
from sliceselector.utils import LogManager

LOG = LogManager()


class SliceSelector:
    def __init__(self, scan):
        self._scan = scan

    def run(self):
        data = '/path/to/slice'
        errors = []
        return Result(data, errors)