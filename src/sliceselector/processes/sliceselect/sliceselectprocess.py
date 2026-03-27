import os
import time
import json
import warnings
from pathlib import Path
from sliceselector.processes.process import Process
from sliceselector.utils import load_dicom
from sliceselector.processes.sliceselect.sliceselector import SliceSelector
from sliceselector.utils import LogManager

warnings.filterwarnings(
    'ignore', message=r'Invalid value for VR UI:.*', category=UserWarning, module=r"pydicom\.valuerep")

LOG = LogManager()


class SliceSelectProcess(Process):
    def __init__(self, inputs, output, vertebra):
        super(SliceSelectProcess, self).__init__(inputs, output)
        self._root_directory = inputs.get('root_directory', None)
        self._vertebra = vertebra
        LOG.info(f'Running SliceSelectProcess from root directory {self._root_directory}')

    def load_completed_scans(self):
        """
        Loads dictionary with scan info for scans that were succesfully processed.
        These scans can be skipped in case the tool needs to resume.
        """
        state_file = os.path.join(self._root_directory, 'completed.json')
        if os.path.isfile(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_failed_scans(self):
        """
        Loads dictionary of failed scans. When the tool tries to resume it will skip the
        failed scans. No need to try again.
        """
        state_file = os.path.join(self._root_directory, 'failed.json')
        if os.path.isfile(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def update_completed_and_failed_scans(self, completed_scans, failed_scans):
        """
        Update dictionary info for completed and failed scans. This info is written to 
        JSON format in the root directory.
        """
        with open(os.path.join(self._root_directory, 'completed.json'), 'w') as f:
            json.dump(completed_scans, f, indent=2)
        with open(os.path.join(self._root_directory, 'failed.json'), 'w') as f:
            json.dump(failed_scans, f, indent=2)

    def find_new_scans(self, completed_scans, failed_scans):
        """
        Finds new scans to process, skipping any completed or failed scans. Returns a
        dictionary of candidate scans to process.
        """
        LOG.info(f'Found {len(completed_scans)} completed and {len(failed_scans)} failed scans')
        new_scans = {}
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
        for suid in new_scans.keys():
            path = new_scans[suid]['path']
            for f in os.listdir(path):
                f_path = os.path.join(path, f)
                new_scans[suid]['files'].append(f_path)
        LOG.info(f'Found {len(new_scans)} new scans')
        return new_scans
    
    def select_slices_from_scans(self, scans, completed_scans, failed_scans):
        """
        Processes given scans. If scan is successfully processed, i.e., the slice selection
        worked, then the scan is added to the completed scans. If not, it is added to the 
        failed scans. The selected slices will be returned as a list of file paths.
        """
        nr_steps = len(scans.keys())
        step = 0
        selected_slices = []
        for suid in scans.keys():
            if self.is_canceled():
                LOG.info('Slice selection was canceled')
                self.update_completed_and_failed_scans(completed_scans, failed_scans)
                break
            try:
                selector = SliceSelector(scan=scans[suid], vertebra=self._vertebra, output_dir=self.output())
                result = selector.run()
                if result.has_errors():
                    failed_scans[suid] = scans[suid]
                    failed_scans[suid]['errors'] = result.errors()
                    LOG.info(f'Error processing scan {suid} ({result.errors()}). Skipping...')
                else:
                    completed_scans[suid] = scans[suid]
                    selected_slices.append(result.data())
            except Exception as e:
                failed_scans[suid] = scans[suid]
                failed_scans[suid]['errors'] = str(e)
                LOG.info(f'Exception processing scan {suid} ({str(e)}). Skipping...')
            self.progress.emit(step, nr_steps)
            step += 1
        self.update_completed_and_failed_scans(completed_scans, failed_scans)
        return selected_slices
    
    def execute(self):
        completed_scans = self.load_completed_scans()
        failed_scans = self.load_failed_scans()
        new_scans = self.find_new_scans(completed_scans, failed_scans)
        slices = self.select_slices_from_scans(new_scans, completed_scans, failed_scans)
        for slice in slices:
            print(f'Found slice: {slice}')
        return 'OK'