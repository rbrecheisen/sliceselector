import os
import json
import shutil
from pathlib import Path
from sliceselectorcmdline.sliceselect.sliceselector import SliceSelector
from sliceselectorcmdline.utils import load_dicom
from sliceselectorcmdline.utils import Logger

LOG = Logger()


class SliceSelectRunner:
    def __init__(self, root_dir: str, patient_dir: str, output_dir: str, vertebra: str, resume: bool=True) -> None:
        self._root_dir = root_dir
        self._patient_dir = patient_dir
        self._output_dir = output_dir
        self._vertebra = vertebra
        self._resume = resume
        self._cache_dir = os.path.join(Path.home(), '.sliceselector')
        os.makedirs(self._cache_dir, exist_ok=True)

    def load_completed(self, resume: bool) -> dict:
        completed = os.path.join(self._cache_dir, 'completed.json')
        if os.path.isfile(completed) and resume:
            with open(completed, 'r') as f:
                return json.load(f)
        return {}
    
    def load_failed(self, resume: bool) -> dict:
        failed = os.path.join(self._cache_dir, 'failed.json')
        if os.path.isfile(failed) and resume:
            with open(failed, 'r') as f:
                return json.load(f)
        return {}
    
    def update_completed_and_failed(self, completed: dict, failed: dict) -> None:
        with open(os.path.join(self._cache_dir, 'completed.json'), 'w') as f:
            json.dump(completed, f, indent=2)
        with open(os.path.join(self._cache_dir, 'failed.json'), 'w') as f:
            json.dump(failed, f, indent=2)

    def find_new_scans(self, completed: dict, failed: dict) -> dict:
        LOG.info(f'Found {len(completed)} completed and {len(failed)} failed scans')
        new_scans = {}
        for root, dirs, files in os.walk(self._root_dir):
            for f in files:
                f_path = os.path.join(root, f)
                p = load_dicom(f_path)
                if p is not None:
                    suid = getattr(p, 'SeriesInstanceUID', None)
                    if suid is not None and suid not in completed.keys() and suid not in failed.keys():
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

    def get_closest_file(self, scan_dir: str, output_dir: str, vertebra: str, patient_id: str) -> tuple[str, list]:
        selector = SliceSelector(scan_dir=scan_dir, output_dir=output_dir, vertebra=vertebra, patient_id=patient_id)
        closest_file, errors = selector.run()
        return closest_file, errors

    def get_patient_id_from_file_path(self, file_path: str, patient_dir: str) -> str:
        return Path(file_path).relative_to(Path(patient_dir)).parts[0]
    
    def select_slices_from_scans(self, scans: dict, completed: dict, failed: dict) -> list:
        selected_slices = []
        try:
            for suid in scans.keys():
                scan_dir = scans[suid]['path']
                patient_id = self.get_patient_id_from_file_path(scan_dir, self._patient_dir)
                closest_file, errors = self.get_closest_file(scan_dir, self._output_dir, self._vertebra, patient_id)
                if closest_file is None:
                    failed[suid] = scans[suid]
                    failed[suid]['errors'] = errors
                else:
                    completed[suid] = scans[suid]
                    selected_slices.append(closest_file)
            return selected_slices
        finally:
            LOG.info(f'Updating completed and failed')
            self.update_completed_and_failed(completed, failed)


    def run(self) -> None:
        # scan_dir = self._root_dir
        # patient_id = self.get_patient_id_from_file_path(scan_dir, self._patient_dir)
        # closest_file = self.get_closest_file_and_z_pos(scan_dir, self._output_dir, self._vertebra, patient_id)
        # output_file = f'{patient_id}_{self._vertebra}.dcm'
        # os.makedirs(self._output_dir, exist_ok=True)
        # shutil.copy(closest_file, os.path.join(self._output_dir, output_file))
        # LOG.info(f'Copied {output_file} to {self._output_dir}')
        completed = self.load_completed(self._resume)
        failed = self.load_failed(self._resume)
        new_scans = self.find_new_scans(completed, failed)
        slices = self.select_slices_from_scans(new_scans, completed, failed)
        for slice in slices:
            print(f'Found slice: {slice}')