class ProcessNoQt:
    def __init__(self, inputs, output, params=None, parent=None):
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