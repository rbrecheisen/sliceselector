import traceback
from PySide6.QtCore import (
    QObject, 
    QThread, 
    Signal, 
    Slot,
    QCoreApplication,
)


class Process(QObject):
    progress = Signal(int, int)
    finished = Signal(object)
    failed = Signal(Exception)
    started = Signal()
    canceled = Signal()

    def __init__(self, inputs, output, params=None, parent=None):
        super(Process, self).__init__(parent)
        self._inputs = inputs
        self._output = output
        self._params = params
        self._cancel = False
        self._thread = None
        self._main_thread = None

    # GETTERS

    def inputs(self):
        return self._inputs

    def input(self, name):
        return self._inputs[name]
    
    def output(self):
        return self._output
    
    def params(self):
        return self._params
    
    def param(self, name):
        return self._params[name]

    def cancel(self):
        self._cancel = True

    def is_canceled(self) -> bool:
        return self._cancel

    def execute(self):
        raise NotImplementedError

    def start(self):
        if self._thread is not None:
            raise RuntimeError("Process already started")
        self._main_thread = QCoreApplication.instance().thread()
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self._run_internal)
        self.finished.connect(self._thread.quit)
        self.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup)
        self._thread.start()

    @Slot()
    def _run_internal(self):
        self.started.emit()
        try:
            if self._cancel:
                self.canceled.emit()
                self.finished.emit(None)
                return
            result = self.execute()
            self.finished.emit(result)
        except Exception as e:
            self.failed.emit(traceback.format_exc())

    @Slot()
    def _cleanup(self):
        self.moveToThread(self._main_thread)
        self._thread.deleteLater()
        self._thread = None