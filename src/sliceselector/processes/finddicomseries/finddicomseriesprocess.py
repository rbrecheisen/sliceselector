import os
import json
from sliceselector.processes.process import Process
from sliceselector.utils import load_dicom
from sliceselector.utils import LogManager

LOG = LogManager()


class FindDicomSeriesProcess(Process):
    def __init__(self, inputs, output, params):
        super(FindDicomSeriesProcess, self).__init__(inputs, output, params)
        self._root_directory = inputs.get('root_directory', None)
        LOG.info(f'Running SliceSelectProcess from root directory {self._root_directory}')

    def execute(self):
        scans = {}
        for patient_id in os.listdir(self._root_directory):
            patient_id_path = os.path.join(self._root_directory, patient_id)
            if os.path.isdir(patient_id_path):
                scans[patient_id] = {}
                for root, dirs, files in os.walk(patient_id_path):
                    for f in files:
                        f_path = os.path.join(root, f)
                        p = load_dicom(f_path, stop_before_pixels=True)
                        if p is not None:
                            suid = getattr(p, 'SeriesInstanceUID', None)
                            if suid is not None and suid not in scans[patient_id].keys():
                                scans[patient_id][suid] = []
                            scans[patient_id][suid].append(f_path)
                print(f'Processed directory: {patient_id}')
        return scans