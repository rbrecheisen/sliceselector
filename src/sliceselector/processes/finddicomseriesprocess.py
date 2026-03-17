"""
FindDicomSeriesProcess
Searches root directory for DICOM series and creates a dictionary with:
{
    'suid': {
        'suid': '',
        'description': '',
        'rows': '',
        'cols': '',
        'nr_slices': '',
    }
}
"""
import os
import json
import time
import pydicom
from sliceselector.processes.process import Process
from sliceselector.utils import is_dicom


class FindDicomSeriesProcess(Process):
    def __init__(self, inputs, output):
        super(FindDicomSeriesProcess, self).__init__(inputs, output)
        self._root_direcory = inputs.get('root_directory', None)
        assert self._root_direcory is not None
        self._done = self.load_done()
        print(self._done)

    def load_done(self):
        if os.path.isfile('done.json'):
            with open('done.json', 'r') as f:
                return json.load(f)
        return []
    
    def save_done(self, done):
        with open('done.json', 'w') as f:
            json.dump(done, f, indent=2)
    
    def is_done(self, suid):
        if self._done is not None:
            return suid in self._done
        return False
    
    def execute(self):
        scans = {}
        done = []
        count = 0
        for root, dirs, files in os.walk(self._root_direcory):
            for f in files:
                if self.is_canceled():
                    self.save_done(done)
                    return scans
                f_path = os.path.join(root, f)
                if os.path.isfile(f_path) and is_dicom(f_path):
                    p = pydicom.dcmread(f_path)
                    suid = getattr(p, 'SeriesInstanceUID', None)
                    if suid is not None and not self.is_done(suid):
                        if suid not in scans.keys():
                            scans[suid] = {'description': '', 'rows': -1, 'cols': -1, 'files': []}
                        scans[suid]['description'] = getattr(p, 'SeriesDescription', '')
                        scans[suid]['rows'] = getattr(p, 'Rows', -1)
                        scans[suid]['cols'] = getattr(p, 'Columns', -1)
                        scans[suid]['files'].append(f_path)
                        done.append(suid)
                        self.progress.emit(count+1, 0)
                        count += 1
        self.save_done(done)
        return scans