import numpy as np
import pydicom
from PIL import Image


class ImagePlotter:
    def __init__(self, dcm_file, output_png):
        self._dcm_file = dcm_file
        self._output_png = output_png

    def plot(self):
        p = pydicom.dcmread(self._dcm_file)
        pixels = p.pixel_array.astype(np.float32)
        slope = float(getattr(p, "RescaleSlope", 1))
        intercept = float(getattr(p, "RescaleIntercept", 0))
        pixels = pixels * slope + intercept
        # Windowing: use DICOM window if available, otherwise min/max
        if hasattr(p, 'WindowCenter') and hasattr(p, 'WindowWidth'):
            wc = p.WindowCenter
            ww = p.WindowWidth
            # Handle MultiValue
            if isinstance(wc, pydicom.multival.MultiValue):
                wc = wc[0]
            if isinstance(ww, pydicom.multival.MultiValue):
                ww = ww[0]
            wc = float(wc)
            ww = float(ww)
            lower = wc - ww / 2
            upper = wc + ww / 2
            arr = np.clip(arr, lower, upper)
        else:
            arr = np.clip(arr, np.percentile(arr, 1), np.percentile(arr, 99))
        # Normalize to 8-bit
        arr = arr - arr.min()
        arr = arr / arr.max()
        arr = (arr * 255).astype(np.uint8)
        # Invert if MONOCHROME1
        if getattr(p, 'PhotometricInterpretation', '') == 'MONOCHROME1':
            arr = 255 - arr
        img = Image.fromarray(arr)
        img.save(self._output_png)