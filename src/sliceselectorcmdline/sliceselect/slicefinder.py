import os
import math
import numpy as np
import nibabel as nib
import pydicom
from sliceselectorcmdline.sliceselect.slicefinderexception import SliceFinderException
from sliceselectorcmdline.utils import Logger

LOG = Logger()


class SliceFinder:
    def __init__(self, scan_dir: str, mask_file: str) -> None:
        self._scan_dir = scan_dir
        self._mask_file = mask_file
        self._errors = []

    def get_errors(self) -> list:
        return self._errors

    def run(self) -> str:
        # Find Z-positions of all DICOM images in CT scan
        z_positions = {}
        for f in os.listdir(self._scan_dir):
            f_path = os.path.join(self._scan_dir, f)
            try:
                p = pydicom.dcmread(f_path, stop_before_pixels=True)
                if p is not None and hasattr(p, "ImagePositionPatient"):
                    z_positions[p.ImagePositionPatient[2]] = f_path
                else:
                    self._errors.append(f'{self._scan_dir}: DICOM image has no attribute "ImagePositionPatient"')
                    raise SliceFinderException()
            except Exception as e:
                self._errors.append(f'{self._scan_dir}: Failed to load DICOM {f_path} ({e})')
                raise SliceFinderException()
        if len(z_positions.keys()) == 0:
            self._errors.append(f'{self._scan_dir}: No valid DICOM z-positions found')
            raise SliceFinderException()
        # Load mask file
        try:
            mask_obj = nib.load(self._mask_file)
            mask = mask_obj.get_fdata()
            affine_transform = mask_obj.affine
        except Exception as e:
            self._errors.append(f'{self._scan_dir}: Failed to load mask {self._mask_file} ({e})')
            raise SliceFinderException()
        # Find Z-coordinate
        indexes = np.array(np.where(mask == 1))
        if indexes.size == 0:
            self._errors.append(f'{self._scan_dir}: No voxels found in mask {self._mask_file}')
            raise SliceFinderException()
        index_min = indexes.min(axis=1)
        index_max = indexes.max(axis=1)
        world_min = nib.affines.apply_affine(affine_transform, index_min)
        world_max = nib.affines.apply_affine(affine_transform, index_max)
        z_direction = affine_transform[:3, 2][2]
        if z_direction == 0:
            self._errors.append(f'{self._scan_dir}: Affine z-direction is zero')
            raise SliceFinderException()
        z_sign = math.copysign(1, z_direction)
        z_delta = 0.5 * abs(world_max[2] - world_min[2]) # Just take middle slice
        z_pos = world_max[2] - z_sign * z_delta
        # Find closest L3 image in DICOM set
        positions = sorted(z_positions.keys())
        closest_file = None
        for z1, z2 in zip(positions[:-1], positions[1:]):
            if min(z1, z2) <= z_pos <= max(z1, z2):
                closest_z = min(z_positions.keys(), key=lambda z: abs(z - z_pos))
                closest_file = z_positions[closest_z]
                LOG.info(f'Closest image: {closest_file} at Z-position {z_pos}')
                break
        if closest_file is None:
            self._errors.append(f'{self._scan_dir}: No matching slice found')
            raise SliceFinderException()
        return closest_file, z_pos