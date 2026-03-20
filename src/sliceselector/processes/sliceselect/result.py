class Result:
    def __init__(self, data, errors):
        self._data = data
        self._errors = errors

    def data(self):
        return self._data

    def has_errors(self):
        return len(self._errors) > 0
    
    def errors(self):
        return self._errors