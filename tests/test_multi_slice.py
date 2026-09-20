import glob
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.dicom import load, metadata_of, segment_roi
from crypto.tamper import protect_image_rev, verify_image_rev
from crypto import reversible as rev

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DCM_DIR = os.path.join(BASE, "dataset", "BrainTumorMRI")
PASSPHRASE = "kunci-multi-2026"
METRO = b"MET=5E;Kategori=multi-slice-MRI;"

rows = []


def main() -> bool:
    files = sorted(glob.glob(os.path.join(DCM_DIR, "*.dcm")))
    print(f"dataset: {len(files)} file DICOM di {DCM_DIR}")
    print(f"{'slice':>4} | {'ROI%':>5} | {'kap(bit)':>8} | {'kap(B)':>6} | {'PSNR(dB)':>8} | {'recovery':>8} | {'t(s)':>5}")
    t0 = time.perf_counter()
    failures = []

    for f in files:
        name = os.path.basename(f)[:16]
        pixels, ds = load(f)
        meta = metadata_of(ds)
        roi = float(segment_roi(pixels).mean()) * 100

        t = time.perf_counter()
        try:
            wm = protect_image_rev(pixels, meta, passphrase=PASSPHRASE)
            ver = verify_image_rev(wm, meta, passphrase=PASSPHRASE)
            dt = time.perf_counter() - t
        except ValueError as exc:
            rows.append((name, roi, 0, 0, 0.0, "OVERFLOW", 0.0))
            failures.append(name)
            continue

        ok = (ver["error"] is None) and (not ver["pixel_tamper"]) and ver["metadata_ok"]
        region = pixels.shape[0] - 16
        exact = np.array_equal(ver["original_recovered"][:region], pixels[:region])
        psnr = rev.psnr(pixels, wm)
        cap = 0
        for r in rev.pee_capacity_multi(pixels, 12):
            cap += r

        rows.append((name, roi, cap, cap // 8, psnr, "OK" if ok else "FAIL", dt))
        if not (ok and exact):
            failures.append(name)

    for name, roi, cap, capb, psnr, status, dt in rows:
        print(f"{name:>4} | {roi:5.1f} | {cap:8d} | {capb:6d} | {psnr:8.2f} | {status:>8} | {dt:5.2f}")

    psnrs = [r[4] for r in rows]
    caps = [r[2] for r in rows]
    rois = [r[1] for r in rows]
    ok_count = sum(1 for r in rows if r[5] == "OK")
    total = len(rows)
    print(f"\nRingkasan ({total} slice):")
    print(f"  OK (verifikasi+recovery eksak) : {ok_count}/{total}")
    print(f"  ROI %        : min={min(rois):.1f}  max={max(rois):.1f}  mean={sum(rois)/total:.1f}")
    print(f"  kapasitas bit: min={min(caps)}  max={max(caps)}  mean={sum(caps)//total}  total={sum(caps)}")
    print(f"  PSNR dB      : min={min(psnrs):.2f}  max={max(psnrs):.2f}  mean={sum(psnrs)/total:.2f}")
    print(f"\nCatatan jurnal: dataset lokal hanya MR (24 slice, ROI tinggi). "
          f"Klaim 'multi-modality' butuh CT/CR -> gap tercatat D-6/5E.")

    dur = time.perf_counter() - t0
    print(f"waktu total: {dur:.1f}s")
    return len(failures) == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)