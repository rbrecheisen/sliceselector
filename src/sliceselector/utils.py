import time
import os
import math
import pendulum
import atexit
import datetime
import pydicom
import pydicom.errors
from pathlib import Path


def create_name_with_timestamp(prefix: str='') -> str:
    tz = pendulum.local_timezone()
    timestamp = pendulum.now(tz).strftime('%Y%m%d%H%M%S%f')[:17]
    if prefix != '' and not prefix.endswith('-'):
        prefix = prefix + '-'
    name = f'{prefix}{timestamp}'
    return name


def current_time_in_milliseconds():
    return int(round(time.time() * 1000))


def current_time_in_seconds() -> int:
    return int(round(current_time_in_milliseconds() / 1000.0))


def elapsed_time_in_milliseconds(start_time_in_milliseconds):
    return current_time_in_milliseconds() - start_time_in_milliseconds


def elapsed_time_in_seconds(start_time_in_seconds):
    return current_time_in_seconds() - start_time_in_seconds


def duration(seconds):
    h = int(math.floor(seconds/3600.0))
    remainder = seconds - h * 3600
    m = int(math.floor(remainder/60.0))
    remainder = remainder - m * 60
    s = int(math.floor(remainder))
    return '{} hours, {} minutes, {} seconds'.format(h, m, s)


def singleton(cls):
    _instances = {}
    def instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    return instance


def load_dicom(f_path, stop_before_pixels=False):
    try:
        return pydicom.dcmread(f_path, stop_before_pixels=stop_before_pixels)
    except pydicom.errors.InvalidDicomError:
        return None


@singleton
class LogManager:
    def __init__(self):
        self._listeners = []
        self._file_path = os.path.join(Path.home(), 'sliceselector.log')
        self._file_handle = open(self._file_path, 'a', buffering=1)
        atexit.register(self.close_file)

    def _log(self, level, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f'[{timestamp}] {level} : {message}'
        print(message)
        self._file_handle.write(message + '\n')
        self.notify_listeners(message)
        return message

    def info(self, message):
        return self._log('INFO', message)

    def warning(self, message):
        return self._log('WARNING', message)

    def error(self, message):
        return self._log('ERROR', message)
    
    def add_listener(self, listener):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def notify_listeners(self, message):
        for listener in self._listeners:
            listener.new_message(message)

    def close_file(self):
        if self._file_handle:
            self._file_handle.close()