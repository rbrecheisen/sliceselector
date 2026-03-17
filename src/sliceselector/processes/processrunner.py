from sliceselector.utils import singleton


@singleton
class ProcessRunner:
    current_process = None

    def start(self, process):
        self.current_process = process
        self.current_process.start()

    def cancel(self):
        if self.current_process is not None:
            self.current_process.cancel()