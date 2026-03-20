import os
import time
import json
import pydicom
from pathlib import Path

ROOT_DIRECTORY = 'M:\\data\\emmymaas\\original'
# ROOT_DIRECTORY = 'M:\\data\\lauracools\\26-02-2026\\original_unzipped_nodots'
STATE_FILE = os.path.join(ROOT_DIRECTORY, 'state.json')


def load_state():
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def load_dicom(f_path):
    try:
        return pydicom.dcmread(f_path, stop_before_pixels=True)
    except pydicom.errors.InvalidDicomError:
        return None


def main():
    state = load_state()
    print(f'Nr. scans found: {len(state.keys())}')
    count = 0
    for root, dirs, files in os.walk(ROOT_DIRECTORY):
        for f in files:
            f_path = os.path.join(root, f)
            p = load_dicom(f_path)
            if p is not None:
                suid = getattr(p, 'SeriesInstanceUID', None)
                if suid is not None and suid not in state.keys():
                    state[suid] = {
                        'path': str(Path(f_path).parent),
                        'description': getattr(p, 'SeriesDescription', ''),
                        'rows': getattr(p, 'Rows', -1),
                        'columns': getattr(p, 'Columns', -1),
                        'files': [],
                    }
                    count += 1
    print(f'Nr. scans added after processing: {count}')
    save_state(state)


if __name__ == '__main__':
    main()