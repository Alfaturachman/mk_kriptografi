import copy

import numpy as np
import pydicom

METADATA_TAGS = [
    "PatientID",
    "PatientName",
    "PatientSex",
    "PatientAge",
    "StudyDate",
    "StudyDescription",
    "SeriesDescription",
    "Modality",
    "StudyInstanceUID",
    "SeriesInstanceUID",
    "SOPInstanceUID",
]


def metadata_of(ds: pydicom.Dataset) -> bytes:
    parts = []
    for tag in METADATA_TAGS:
        parts.append(f"{tag}={ds.get(tag)}".encode("utf-8"))
    return b"|".join(parts)


def load(path) -> tuple:
    ds = pydicom.dcmread(path)
    return ds.pixel_array, ds


def save_watermarked(dest, ds: pydicom.Dataset, pixels: np.ndarray) -> None:
    if not str(ds.file_meta.TransferSyntaxUID).startswith("1.2.840.10008.1.2.1"):
        raise ValueError("prototipe hanya mendukung uncompressed little-endian DICOM")
    out = copy.deepcopy(ds)
    out.PixelData = np.ascontiguousarray(pixels).tobytes()
    out["PixelData"].VR = "OW"
    out.save_as(dest)


def preview_8bit(pixels: np.ndarray) -> np.ndarray:
    flat = pixels.astype(np.float64).ravel()
    lo, hi = np.percentile(flat, 1), np.percentile(flat, 99)
    if hi <= lo:
        hi = lo + 1
    normalized = np.clip((pixels.astype(np.float64) - lo) / (hi - lo), 0, 1)
    return (normalized * 255).astype(np.uint8)


def segment_roi(pixels: np.ndarray) -> np.ndarray:
    """Segementasi ROI/RONI sederhana: ROI = piksel non-background.

    `pixels == 0` dianggap background (RONI) - khas DICOM MRI.
    """
    return pixels > np.iinfo(pixels.dtype).min