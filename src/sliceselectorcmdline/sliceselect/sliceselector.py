import os
from sliceselectorcmdline.sliceselect.segmentator import Segmentator
from sliceselectorcmdline.sliceselect.segmentatorexception import SegmentatorException
from sliceselectorcmdline.sliceselect.slicefinder import SliceFinder
from sliceselectorcmdline.sliceselect.slicefinderexception import SliceFinderException
from sliceselectorcmdline.sagittalplotter import SagittalPlotter
from sliceselectorcmdline.utils import Logger

LOG = Logger()


class SliceSelector:
    """
    SliceSelector
    -------------
    Takes single CT scan and extracts the image slice running through the middle of the
    selected vertebra and saves it to the given output directory.
    """
    def __init__(self, scan_dir: str, output_dir: str, vertebra: str, patient_id: str) -> None:
        self._scan_dir = scan_dir
        self._output_dir = output_dir
        self._vertebra = vertebra
        self._vertebra_file_name = f'vertebrae_{self._vertebra}.nii.gz'
        self._patient_id = patient_id

    def run(self) -> str:
        errors = []
        try:
            segmentator = Segmentator(self._scan_dir, self._vertebra)
            try:
                mask_file = segmentator.run()
            except SegmentatorException as e:
                errors.append(f'Segmentator(Failed to extract {self._vertebra} mask from {self._scan_dir})')
                return None, errors
            finder = SliceFinder(self._scan_dir, mask_file)
            try:
                closest_file, z_pos = finder.run()
                output_png = os.path.join(self._output_dir, f'{self._patient_id}_{self._vertebra}_sagittal.png')
                plotter = SagittalPlotter(self._scan_dir, mask_file, z_pos, output_png)
                plotter.run()
                return closest_file, errors
            except SliceFinderException as e:
                errors.extend(finder.get_errors())
                return None, errors
        finally:
            segmentator.cleanup()