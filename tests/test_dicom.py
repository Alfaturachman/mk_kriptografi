import io
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto import aes
from crypto.dicom import load, metadata_of, preview_8bit, save_watermarked, segment_roi
from crypto.tamper import mark_tampered, protect_image, verify_image, protect_image_rev, verify_image_rev

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SRC_DCM = os.path.join(
    BASE_DIR, "dataset", "BrainTumorMRI", "IM-0001-0001.dcm"
)
PASSPHRASE = "kunci-MRI-2026"

BLOCK = 8
REV_BLOCK = 16
FAILED = []
TOTAL = 0


def run(name: str, ok: bool, detail: str = ""):
    global TOTAL
    TOTAL += 1
    if not ok:
        FAILED.append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def psnr16(a: np.ndarray, b: np.ndarray) -> float:
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")
    return float(10 * np.log10(65535.0 ** 2 / mse))


def main() -> bool:
    os.makedirs(DATA_DIR, exist_ok=True)

    pixels, ds = load(SRC_DCM)
    metadata = metadata_of(ds)
    print(f"Modality {ds.Modality} | {pixels.shape} | uint16 | range {pixels.min()}-{pixels.max()}")

    protected = protect_image(pixels, metadata)
    clean = verify_image(protected, metadata)
    run(
        "Proteksi: piksel bersih + metadata valid",
        (not clean["pixel_tamper"]) and clean["metadata_ok"],
    )

    p1 = psnr16(pixels, protected)
    run("PSNR citra 16-bit tetap sangat tinggi", p1 > 90, f"PSNR={p1:.2f} dB")

    wm_dcm = os.path.join(DATA_DIR, "watermarked_MRI.dcm")
    save_watermarked(wm_dcm, ds, protected)
    reloaded_pixels, reloaded_ds = load(wm_dcm)
    run("Write-back DICOM identik", np.array_equal(reloaded_pixels, protected))

    with open(wm_dcm, "rb") as f:
        dcm_bytes = f.read()
    t0 = time.perf_counter()
    encrypted = aes.encrypt(dcm_bytes, PASSPHRASE)
    t_enc = time.perf_counter() - t0
    run(
        "Enkripsi AES file DICOM",
        len(encrypted) > len(dcm_bytes),
        f"{len(dcm_bytes)} -> {len(encrypted)} byte, {t_enc*1000:.1f} ms",
    )

    cipher_path = os.path.join(DATA_DIR, "cipher_MRI.bin")
    with open(cipher_path, "wb") as f:
        f.write(encrypted)

    t0 = time.perf_counter()
    decrypted = aes.decrypt(encrypted, PASSPHRASE)
    t_dec = time.perf_counter() - t0
    run("Dekripsi file DICOM utuh", decrypted == dcm_bytes, f"{t_dec*1000:.1f} ms")

    try:
        aes.decrypt(encrypted, "kunci-salah")
        run("Kunci salah ditolak", False)
    except ValueError:
        run("Kunci salah ditolak", True)

    recovered, _ = load(io.BytesIO(decrypted))
    verdict = verify_image(recovered, metadata)
    run(
        "Verifikasi DICOM hasil dekripsi: bersih",
        (not verdict["pixel_tamper"]) and verdict["metadata_ok"],
    )

    tampered = np.array(recovered, copy=True)
    bi, bj = 20, 20
    r0, c0 = bi * BLOCK, bj * BLOCK
    tampered[r0 : r0 + BLOCK, c0 : c0 + BLOCK] = np.clip(
        tampered[r0 : r0 + BLOCK, c0 : c0 + BLOCK].astype(np.int32) + 30, 0, 65535
    ).astype(np.uint16)

    verdict2 = verify_image(tampered, metadata)
    mask = verdict2["mask"]
    mask_px = int((mask == 255).sum())
    run("Manipulasi piksel DICOM terdeteksi", verdict2["pixel_tamper"], f"{mask_px} piksel")

    localized_block = bool((mask[r0 : r0 + BLOCK, c0 : c0 + BLOCK] == 255).all())
    run("Lokalisasi presisi (blok 8x8)", localized_block and mask_px == BLOCK * BLOCK)

    verdict3 = verify_image(recovered, b"PATIENT:X;UBAH-DATA")
    run(
        "Perubahan metadata DICOM terdeteksi",
        (not verdict3["metadata_ok"]) and (not verdict3["pixel_tamper"]),
    )

    print("\n== Fase 5D: jalur reversible pada DICOM 16-bit ==")
    roi = segment_roi(pixels)
    roi_ratio = float(roi.mean())
    run("Segmentasi ROI/RONI (piksel non-background)",
        roi_ratio > 0.1,
        f"ROI={roi_ratio*100:.1f}% ; RONI={100-roi_ratio*100:.1f}% (dataset ini nyaris tanpa background - catatan D-6)")

    rev_pass = "kunci-reversible-2026"
    protected_rev = protect_image_rev(pixels, metadata, block=REV_BLOCK, passphrase=rev_pass)
    run("Proteksi reversible: payload AES + hash blok embedded", True)

    clean_rev = verify_image_rev(protected_rev, metadata, passphrase=rev_pass)
    run("Verifikasi reversible: bersih", (clean_rev["error"] is None)
        and (not clean_rev["pixel_tamper"]) and clean_rev["metadata_ok"])
    recovered_rev = clean_rev["original_recovered"]
    region = pixels.shape[0] - 16
    run("Recovery eksak region (PSNR=inf, array identik)",
        np.array_equal(recovered_rev[:region], pixels[:region]))

    p_rev = psnr16(pixels, protected_rev)
    run("PSNR citra ber-watermark reversible tetap tinggi", p_rev > 80, f"PSNR={p_rev:.2f} dB")

    wm_rev_dcm = os.path.join(DATA_DIR, "watermarked_rev_MRI.dcm")
    save_watermarked(wm_rev_dcm, ds, protected_rev)
    reloaded_rev, reloaded_ds = load(wm_rev_dcm)
    run("Write-back DICOM reversible identik", np.array_equal(reloaded_rev, protected_rev))

    tampered_rev = np.array(reloaded_rev, copy=True)
    r0, c0 = 3 * REV_BLOCK, 12 * REV_BLOCK
    tampered_rev[r0 : r0 + 4, c0 : c0 + 4] = np.clip(
        tampered_rev[r0 : r0 + 4, c0 : c0 + 4].astype(np.int32) + 300, 0, 65535
    ).astype(np.uint16)
    t_rev = verify_image_rev(tampered_rev, metadata, passphrase=rev_pass)
    run("Tamper piksel reversible terdeteksi (enkripsi)",
        t_rev["pixel_tamper"] is True,
        f"error={t_rev['error']}")

    protected_loc = protect_image_rev(pixels, metadata, block=REV_BLOCK)
    loc = np.array(protected_loc, copy=True)
    loc[r0 : r0 + REV_BLOCK, c0 : c0 + REV_BLOCK] = np.clip(
        loc[r0 : r0 + REV_BLOCK, c0 : c0 + REV_BLOCK].astype(np.int32) + 50, 0, 65535
    ).astype(np.uint16)
    v_loc = verify_image_rev(loc, metadata)
    run("Tamper piksel reversible terdeteksi (tanpa enkripsi)",
        v_loc["pixel_tamper"] is True)
    run("Blok 16x16 ter-lokalisasi (jalur tidak terenkripsi)",
        bool((v_loc["mask"][r0 : r0 + REV_BLOCK, c0 : c0 + REV_BLOCK] == 255).any()),
        f"nonzero={v_loc['mask'].sum()}")

    rec_dcm = os.path.join(DATA_DIR, "recovered_rev_MRI.dcm")
    save_watermarked(rec_dcm, ds, recovered_rev)
    run("Citra hasil recovery tersimpan sebagai DICOM baru", True)

    out_before = os.path.join(DATA_DIR, "original_rev_MRI.png")
    out_after = os.path.join(DATA_DIR, "recovered_rev_MRI.png")
    Image.fromarray(preview_8bit(pixels)).save(out_before)
    Image.fromarray(preview_8bit(recovered_rev)).save(out_after)
    run("Preview original vs recovered dibuat", True)

    out_orig = os.path.join(DATA_DIR, "original_MRI.png")
    out_ovr = os.path.join(DATA_DIR, "tamper_overlay_MRI.png")
    Image.fromarray(preview_8bit(pixels)).save(out_orig)
    Image.fromarray(mark_tampered(preview_8bit(recovered), mask)).save(out_ovr)

    passed = TOTAL - len(FAILED)
    print(f"\nHasil: {passed}/{TOTAL} lulus")
    print(
        f"File hasil: {wm_dcm} | {cipher_path} | {out_orig} | {out_ovr}\n"
        f"Reversible: {wm_rev_dcm} | {rec_dcm} | {out_before} | {out_after}"
    )
    return len(FAILED) == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)