import os
import shutil
import tempfile
from totalsegmentator.python_api import totalsegmentator
from sliceselectorcmdline.sliceselect.segmentatorexception import SegmentatorException
from sliceselectorcmdline.utils import Logger

LOG = Logger()


class Segmentator:
    def __init__(self, scan_dir: str, vertebra: str) -> None:
        self._scan_dir = scan_dir
        self._vertebra = vertebra
        self._temp_dir = os.path.join(tempfile.gettempdir(), 'total_segmentator')
        
    def run(self) -> str:
        mask_file = self.extract_mask(self._scan_dir, self._vertebra, self._temp_dir)
        if mask_file is None:
            raise SegmentatorException()
        return mask_file

    def extract_mask(self, scan_dir: str, vertebra: str, temp_dir: str) -> str:
        LOG.info(f'Extracting mask for {vertebra} from CT scan in {scan_dir}. Writing temporary output to {temp_dir}')
        os.makedirs(temp_dir, exist_ok=True)
        totalsegmentator(input=scan_dir, output=temp_dir, fast=True)
        mask_file = os.path.join(temp_dir, f'vertebrae_{vertebra}.nii.gz')
        if not os.path.isfile(mask_file):
            LOG.error(f'Could not find mask file {mask_file}')
            return None
        return mask_file

    def cleanup(self) -> None:
        if os.path.exists(self._temp_dir):
            LOG.info(f'Deleting temporary output in {self._temp_dir}')
            shutil.rmtree(self._temp_dir)
