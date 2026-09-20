import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto import tamper as tp
from crypto.dicom import load as dicom_load

META = b"MRN=456789;Name=Doe#John;Study=CHEST-MRI;Date=2026-05-06"

failures = []
total = 0


def check(name, cond, detail=""):
    global total
    total += 1
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name} {detail}")
    if not cond:
        failures.append(name)


def main():
    dcm_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "dataset", "BrainTumorMRI", "IM-0001-0002.dcm",
    )
    pixels, _ = dicom_load(dcm_path)
    print(f"citra MRI: {pixels.shape} {pixels.dtype} range=[{pixels.min()}, {pixels.max()}]")

    wm = tp.protect_image_rev(pixels, META)
    print(f"payload hash blok = {tp._rev_grid(pixels)[0] * tp._rev_grid(pixels)[1] * tp.HASH_BITS} bit")

    print("\n== Roundtrip bersih (tanpa tamper) ==")
    res = tp.verify_image_rev(wm, META)
    ok_region = False
    if not res["error"]:
        ok_region = np.array_equal(res["original_recovered"][: res["original_recovered"].shape[0] - tp.PARAM_STRIP],
                                   pixels[: pixels.shape[0] - tp.PARAM_STRIP])
    check("tidak ada error", res["error"] is None, f"error={res['error']}")
    check("pixel_tamper=False", res["pixel_tamper"] is False)
    check("tidak ada blok tertandai", not res["mask"].any())
    check("metadata_ok=True", res["metadata_ok"] is True)
    check("recovery region eksak", ok_region)

    print("\n== Deteksi & lokalisasi tamper (1 blok 16x16) ==")
    wrk = np.array(wm, copy=True)
    r0, c0 = 40, 300
    wrk[r0 : r0 + 8, c0 : c0 + 8] += 50
    res = tp.verify_image_rev(wrk, META)
    check("pixel_tamper=True", res["pixel_tamper"] is True)
    check("payload ikut rusak -> metadata_ok=False (diharapkan)", res["metadata_ok"] is False)
    br = (r0 // 16) * 16
    bc = (c0 // 16) * 16
    maskblock = res["mask"][br : br + 16, bc : bc + 16]
    check("blok tamper tertandai", maskblock.any(),
          f"nonzero={res['mask'].sum()}")
    check("recovered tidak identik (rusak terdeteksi)",
          not np.array_equal(res["original_recovered"][: pixels.shape[0] - tp.PARAM_STRIP],
                             pixels[: pixels.shape[0] - tp.PARAM_STRIP]))

    print("\n== Perubahan metadata pasien terdeteksi ==")
    res = tp.verify_image_rev(wm, META + b"TAMPERED")
    check("pixel_tamper=False (piksel utuh)", res["pixel_tamper"] is False)
    check("metadata_ok=False", res["metadata_ok"] is False)

    print("\n== 5C: payload terenkripsi AES (passphrase) ==")
    wm_a = tp.protect_image_rev(pixels, META, passphrase="rahasia-123")
    res = tp.verify_image_rev(wm_a, META, passphrase="rahasia-123")
    check("kunci benar -> bersih", (res["error"] is None) and (res["pixel_tamper"] is False)
          and res["metadata_ok"] is True)
    check("kunci benar -> recovery eksak",
          np.array_equal(res["original_recovered"][: pixels.shape[0] - tp.PARAM_STRIP],
                         pixels[: pixels.shape[0] - tp.PARAM_STRIP]))
    res = tp.verify_image_rev(wm_a, META, passphrase="salah-kunci")
    check("kunci salah -> ditolak tanpa crash", res["error"] is not None and "kunci" in res["error"].lower(),
          f"error={res['error']}")
    check("kunci salah -> status tidak dipercaya", res["pixel_tamper"] is True)

    print("\n== Verifikasi PSNR watermark ==")
    from crypto import reversible as rev
    print(f"PSNR(wm) = {rev.psnr(pixels, wm):.2f} dB")

    print(f"\nHasil: {total - len(failures)}/{total}")
    return len(failures) == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)