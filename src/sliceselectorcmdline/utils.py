import os
import atexit
import datetime
import pydicom
import pydicom.errors
from pathlib import Path


def singleton(cls):
    _instances = {}

    def instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    
    return instance


@singleton
class Logger:
    def __init__(self) -> None:
        self._file = os.path.join(Path.home(), 'sliceselector.log')
        self._file_handle = open(self._file, 'w', buffering=1)
        atexit.register(self.close_file)

    def file(self) -> str:
        return self._file

    def log(self, message: str, level: str) -> None:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f'[{timestamp}] {level} : {message}'
        self._file_handle.write(message + '\n')
        print(message)

    def info(self, message: str) -> None:
        return self.log(message, 'INFO')

    def warning(self, message: str) -> None:
        return self.log(message, 'WARNING')

    def error(self, message: str) -> None:
        return self.log(message, 'ERROR')

    def close_file(self):
        if self._file_handle:
            self._file_handle.close()


def load_dicom(f_path, stop_before_pixels=False):
    try:
        return pydicom.dcmread(f_path, stop_before_pixels=stop_before_pixels)
    except pydicom.errors.InvalidDicomError:
        return None