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
            pixels = np.clip(pixels, lower, upper)
        else:
            pixels = np.clip(pixels, np.percentile(pixels, 1), np.percentile(pixels, 99))
        # Normalize to 8-bit
        pixels = pixels - pixels.min()
        pixels = pixels / pixels.max()
        pixels = (pixels * 255).astype(np.uint8)
        # Invert if MONOCHROME1
        if getattr(p, 'PhotometricInterpretation', '') == 'MONOCHROME1':
            pixels = 255 - pixels
        img = Image.fromarray(pixels)
        img.save(self._output_png)