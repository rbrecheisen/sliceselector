import os
import time
import json
from pathlib import Path
from sliceselector.processes.process import Process
from sliceselector.utils import load_dicom


class FindDicomSeriesProcess(Process):
    def __init__(self, inputs, output):
        super(FindDicomSeriesProcess, self).__init__(inputs, output)
        self._root_directory = inputs.get('root_directory', None)

    def load_completed_scans(self):
        state_file = os.path.join(self._root_directory, 'completed.json')
        if os.path.isfile(state_file):
            with open(state_file, 'r') as f:
                return list(json.load(f))
        return []
    
    def load_failed_scans(self):
        state_file = os.path.join(self._root_directory, 'failed.json')
        if os.path.isfile(state_file):
            with open(state_file, 'r') as f:
                return list(json.load(f))
        return []
    
    def update_completed_and_failed_scans(self, completed_scans, failed_scans):
        with open(os.path.join(self._root_directory, 'completed.json'), 'w') as f:
            json.dump(completed_scans, f, indent=2)
        with open(os.path.join(self._root_directory, 'failed.json'), 'w') as f:
            json.dump(failed_scans, f, indent=2)
    
    def execute(self):
        completed_scans = self.load_completed_scans()
        failed_scans = self.load_failed_scans()
        new_scans = {}

        print(f'Completed: {len(completed_scans)}, failed: {len(failed_scans)}')

        # Find scans
        for root, dirs, files in os.walk(self._root_directory):
            for f in files:
                f_path = os.path.join(root, f)
                p = load_dicom(f_path)
                if p is not None:
                    suid = getattr(p, 'SeriesInstanceUID', None)
                    if suid is not None and suid not in completed_scans and suid not in failed_scans:
                        new_scans[suid] = {
                            'path': str(Path(f_path).parent),
                            'description': getattr(p, 'SeriesDescription', ''),
                            'rows': getattr(p, 'Rows', -1),
                            'columns': getattr(p, 'Columns', -1),
                            'files': [],
                        }

        # Collect images for each new scan
        for suid in new_scans.keys():
            path = new_scans[suid]['path']
            for f in os.listdir(path):
                f_path = os.path.join(path, f)
                new_scans[suid]['files'].append(f_path)

        # Run slice selection
        nr_steps = len(new_scans.keys())
        step = 0
        for suid in new_scans.keys():
            if self.is_canceled():
                self.update_completed_and_failed_scans(completed_scans, failed_scans)
                return 'CANCELED'
            if step == 10 or step == 20:
                failed_scans.append(suid)
            else:
                completed_scans.append(suid)
            self.progress.emit(step, nr_steps)
            step += 1
            time.sleep(0.1)

        self.update_completed_and_failed_scans(completed_scans, failed_scans)
        return 'OK'