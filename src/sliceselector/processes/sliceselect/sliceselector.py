import os
import shutil
import math
import tempfile
import nibabel as nib
import numpy as np
from totalsegmentator.python_api import totalsegmentator
from sliceselector.processes.sliceselect.result import Result
from sliceselector.processes.sliceselect.sagittalimageplotter import SagittalSlicePlotter
from sliceselector.processes.sliceselect.imageplotter import ImagePlotter
from sliceselector.utils import LogManager, load_dicom

TOTAL_SEGMENTATOR_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'total_segmentator_output')
TOTAL_SEGMENTATOR_TASK = 'total'

LOG = LogManager()


class SliceSelector:
    def __init__(self, scan, vertebra, patient_dir_idx, output_dir):
        self._scan = scan
        self._vertebra = vertebra
        self._patient_dir_idx = patient_dir_idx
        self._vertebra_file = f'vertebrae_{vertebra}.nii.gz'
        self._output_dir = output_dir
        self._errors = []

    def extract_masks(self, scan_dir):
        os.makedirs(TOTAL_SEGMENTATOR_OUTPUT_DIR, exist_ok=True)
        totalsegmentator(input=scan_dir, output=TOTAL_SEGMENTATOR_OUTPUT_DIR, fast=True)
        if not os.path.isfile(os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, self._vertebra_file)):
            raise Exception(f'{scan_dir}: vertebrae_L3.nii.gz does not exist')

    def delete_total_segmentator_output(self):
        if os.path.exists(TOTAL_SEGMENTATOR_OUTPUT_DIR):
            shutil.rmtree(TOTAL_SEGMENTATOR_OUTPUT_DIR)

    def find_slice(self, scan_dir, vertebra):
        vertebral_level = f'vertebrae_{vertebra}'
        # Find Z-positions DICOM images
        z_positions = {}
        for f in os.listdir(scan_dir):
            f_path = os.path.join(scan_dir, f)
            try:
                p = load_dicom(f_path, stop_before_pixels=True)
                if p is not None and hasattr(p, "ImagePositionPatient"):
                    z_positions[p.ImagePositionPatient[2]] = f_path
            except Exception as e:
                self._errors.append(f"{scan_dir}: Failed to load DICOM {f_path}: {e}")
                break
        if not z_positions:
            self._errors.append(f"{scan_dir}: No valid DICOM z-positions found.")
            return None, None
        # Find Z-position vertebral image
        mask_file = os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, f'{vertebral_level}.nii.gz')
        if not os.path.exists(mask_file):
            self._errors.append(f"{scan_dir}: Mask file not found: {mask_file}")
            return None, None
        try:
            mask_obj = nib.load(mask_file)
            mask = mask_obj.get_fdata()
            affine_transform = mask_obj.affine
        except Exception as e:
            self._errors.append(f"{scan_dir}: Failed to load mask {mask_file}: {e}")
            return None, None
        indexes = np.array(np.where(mask == 1))
        if indexes.size == 0:
            self._errors.append(f"{scan_dir}: No voxels found in mask {mask_file} for {vertebral_level}")
            return None, None        
        index_min = indexes.min(axis=1)
        index_max = indexes.max(axis=1)
        world_min = nib.affines.apply_affine(affine_transform, index_min)
        world_max = nib.affines.apply_affine(affine_transform, index_max)
        z_direction = affine_transform[:3, 2][2]
        if z_direction == 0:
            self._errors.append(f"{scan_dir}: Affine z-direction is zero.")
            return None, None
        z_sign = math.copysign(1, z_direction)
        z_delta = 0.5 * abs(world_max[2] - world_min[2]) # Just take middle slice
        z_l3 = world_max[2] - z_sign * z_delta
        # Find closest L3 image in DICOM set
        positions = sorted(z_positions.keys())
        closest_file = None
        for z1, z2 in zip(positions[:-1], positions[1:]):
            if min(z1, z2) <= z_l3 <= max(z1, z2):
                closest_z = min(z_positions.keys(), key=lambda z: abs(z - z_l3))
                closest_file = z_positions[closest_z]
                LOG.info(f'Closest image: {closest_file}')
                break
        if closest_file is None:
            self._errors.append(f"{scan_dir}: No matching slice found.")
        return closest_file, z_l3

    def run(self):
        path_to_slice = None
        self._errors = []
        try:
            self.extract_masks(self._scan['path'])
            path_to_slice, z_vert = self.find_slice(self._scan['path'], self._vertebra)
            if path_to_slice is not None:
                # Do not take name of scan directory because it may not be unique across scans
                # Take the patient identifying directory name
                dir_names = self._scan['path'].split(os.path.sep)
                if self._patient_dir_idx >= len(dir_names):
                    raise Exception(f'patient_dir_idx is larger than length directory names: ({self._patient_dir_idx} -> {len(dir_names)})')
                patient_id = dir_names[self._patient_dir_idx] 
                extension = '' if path_to_slice.endswith('.dcm') else '.dcm'
                target_file_path = os.path.join(self._output_dir, self._vertebra + '_' + patient_id + extension)
                LOG.info(f'Writing to L3 file: {target_file_path}')
                shutil.copyfile(path_to_slice, target_file_path)
                # Create sagittal image
                mask_file = os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, f'vertebrae_{self._vertebra}.nii.gz')
                output_png = os.path.join(self._output_dir, f"{self._vertebra}_{patient_id}_sagittal.png")
                plotter = SagittalSlicePlotter(
                    scan_dir=self._scan['path'],
                    mask_file=mask_file,
                    z_vert=z_vert,
                    output_png=output_png,
                )
                plotter.plot()
                # Create PNG image of the DICOM slice as well, for easier manual review
                png_output = os.path.join(self._output_dir, f'{self._vertebra}_{patient_id}_axial.png')
                png_plotter = ImagePlotter(dcm_file=path_to_slice, output_png=png_output)
                png_plotter.plot()
            return Result(path_to_slice, self._errors)
        except Exception as e:
            raise e
        finally:
            self.delete_total_segmentator_output()