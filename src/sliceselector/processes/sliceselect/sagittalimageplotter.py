import os
import math
import tempfile
import shutil
import nibabel as nib
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt


class SagittalSlicePlotter:
    def __init__(self, scan_dir, mask_file, z_vert, output_png):
        self._scan_dir = scan_dir
        self._mask_file = mask_file
        self._z_vert = z_vert
        self._output_png = output_png

    def read_ct_series_sitk(self, scan_dir):
        reader = sitk.ImageSeriesReader()
        series_ids = reader.GetGDCMSeriesIDs(scan_dir)
        if not series_ids:
            raise ValueError(f'No DICOM series found in {scan_dir}')
        file_names = reader.GetGDCMSeriesFileNames(scan_dir, series_ids[0])
        reader.SetFileNames(file_names)
        img = reader.Execute()
        return img
    
    def resample_to_reference(self, moving: sitk.Image, reference: sitk.Image, is_label: bool) -> sitk.Image:
        interp = sitk.sitkNearestNeighbor if is_label else sitk.sitkLinear
        return sitk.Resample(
            moving,
            reference,
            sitk.Transform(),
            interp,
            0,  # default value
            moving.GetPixelID()
        )
    
    def centroid_x_index_from_mask(self, mask_ref: sitk.Image) -> int:
        # mask_ref must already be on the CT grid
        arr = sitk.GetArrayFromImage(mask_ref)  # shape: [z, y, x]
        idx = np.argwhere(arr > 0)
        if idx.size == 0:
            # fallback to true mid-sagittal
            size_x = mask_ref.GetSize()[0]
            return size_x // 2
        x_mean = int(round(idx[:, 2].mean()))
        return x_mean
    
    def z_index_from_physical_z(self, ct_img: sitk.Image, z_phys: float, x_index: int) -> int:
        # pick a y roughly mid (or better: y centroid of mask if you want)
        size = ct_img.GetSize()  # (x, y, z)
        y_index = size[1] // 2
        # Convert chosen (x_index, y_index, any z_index) -> physical, then replace z
        p = ct_img.TransformIndexToPhysicalPoint((x_index, y_index, size[2] // 2))
        phys_point = (p[0], p[1], z_phys)
        try:
            ix, iy, iz = ct_img.TransformPhysicalPointToIndex(phys_point)
        except RuntimeError:
            # if z_phys is slightly out of range, clamp later
            iz = None
        if iz is None:
            # clamp using physical bounds
            # safest crude clamp: convert all slice centers to physical z and find closest
            z_centers = []
            for k in range(size[2]):
                pk = ct_img.TransformIndexToPhysicalPoint((x_index, y_index, k))
                z_centers.append(pk[2])
            z_centers = np.array(z_centers)
            iz = int(np.argmin(np.abs(z_centers - z_phys)))
        iz = int(np.clip(iz, 0, size[2]-1))
        return iz

    def plot(self):
        ct = self.read_ct_series_sitk(self._scan_dir)
        vert_mask = sitk.ReadImage(self._mask_file)
        vert_mask_ref = self.resample_to_reference(vert_mask, ct, is_label=True)
        x_idx = self.centroid_x_index_from_mask(vert_mask_ref)
        z_idx = self.z_index_from_physical_z(ct, self._z_vert, x_idx)
        ct_arr = sitk.GetArrayFromImage(ct).astype(np.float32)
        mk_arr = sitk.GetArrayFromImage(vert_mask_ref).astype(np.uint8)
        sag_ct = ct_arr[:, :, x_idx]
        sag_mk = mk_arr[:, :, x_idx]
        vmin, vmax = np.percentile(sag_ct, (1, 99))
        sy = ct.GetSpacing()[1]  # y spacing (mm)
        sz = ct.GetSpacing()[2]  # z spacing (mm)
        aspect = sz / sy
        plt.figure(figsize=(7, 9))
        plt.imshow(sag_ct, cmap="gray", vmin=vmin, vmax=vmax, origin="lower", aspect=aspect)
        plt.imshow(sag_mk, alpha=0.35, origin="lower", aspect=aspect)
        plt.axhline(z_idx, linewidth=2)  # line across the vertebra axial slice position
        plt.title("Sagittal view with vertebral mask overlay + selected vertebra axial slice")
        plt.axis("off")
        plt.savefig(self._output_png, bbox_inches="tight", dpi=200)