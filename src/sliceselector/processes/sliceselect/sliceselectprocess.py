import os
import time
import json
import traceback
from pathlib import Path
from sliceselector.processes.process import Process
from sliceselector.utils import load_dicom
from sliceselector.processes.sliceselect.sliceselector import SliceSelector


class SliceSelectProcess(Process):
    def __init__(self, inputs, output):
        super(SliceSelectProcess, self).__init__(inputs, output)
        self._root_directory = inputs.get('root_directory', None)

    def load_completed_scans(self):
        state_file = os.path.join(self._root_directory, 'completed.json')
        if os.path.isfile(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_failed_scans(self):
        state_file = os.path.join(self._root_directory, 'failed.json')
        if os.path.isfile(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
        return {}
    
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
                    if suid is not None and suid not in completed_scans.keys() and suid not in failed_scans.keys():
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
        selected_slices = []
        for suid in new_scans.keys():

            # Check for cancelation of task
            if self.is_canceled():
                self.update_completed_and_failed_scans(completed_scans, failed_scans)
                return 'CANCELED'
            
            # Run slice selection and update completed/failed lists
            try:
                selector = SliceSelector(scan=new_scans[suid])
                result = selector.run()
                if result.has_errors():
                    failed_scans[suid]['errors'] = result.errors()
                    print(f'Error processing scan {suid} ({result.errors()}). Skipping...')
                else:
                    completed_scans[suid] = new_scans[suid]
                    selected_slices.append(result.data())
            except Exception as e:
                failed_scans[suid] = new_scans[suid]
                failed_scans[suid]['errors'] = str(e)
                print(f'Exception processing scan {suid} ({str(e)}). Skipping...')
            
            # Update progress
            self.progress.emit(step, nr_steps)
            step += 1
            time.sleep(0.1)

        self.update_completed_and_failed_scans(completed_scans, failed_scans)
        return 'OK'