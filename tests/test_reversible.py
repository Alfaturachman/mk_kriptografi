import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto import reversible as rev
from crypto.dicom import load as dicom_load

PAYLOAD = b"REVERSIBLE-PROBE-2026:PatientID=AE-0001;Study=CHEST;Date=2026-09-20" * 2


def make_images():
    rng = np.random.default_rng(7)

    yy, xx = np.mgrid[:256, :256]
    smooth = 900 + (np.sin(yy / 12.0) * 200 + np.cos(xx / 9.0) * 150).astype(np.int64)
    smooth = smooth + rng.integers(-2, 3, size=smooth.shape)
    smooth = np.clip(smooth, 0, 1500).astype(np.uint16)

    bg = np.zeros((256, 256), dtype=np.uint16)
    sel = rng.random((256, 256)) < 0.35
    bg[sel] = (300 + rng.integers(0, 1701, size=sel.sum())).astype(np.uint16)

    flat = rng.integers(0, 65536, size=(192, 192), dtype=np.uint16)

    return {"smooth16": smooth, "bg16": bg, "flat16": flat}


def bench(name, img, bits):
    t0 = time.perf_counter()
    try:
        wm, params = rev.pee_embed(img, bits)
    except ValueError as exc:
        print(f"[SKIP] {name}: embed gagal - {exc}")
        return False
    t_emb = time.perf_counter() - t0

    n_bits = params["n_bits"]
    t0 = time.perf_counter()
    got = rev.pee_extract(wm, n_bits, params["peak"], params["direction"])
    t_ext = time.perf_counter() - t0

    t0 = time.perf_counter()
    back = rev.pee_reverse(wm, params)
    t_rev = time.perf_counter() - t0

    exact = np.array_equal(img, back)
    b = rev.ber(bits, got)
    p = rev.psnr(img, wm)

    tag = "PASS" if (exact and b == 0.0) else "FAIL"
    print(
        f"[{tag}] {name}: kap={n_bits}bit(e0={params['peak']},d={params['direction']:+.0f}) "
        f"PSNR={p:.2f}dB BER={b:.4f} exact={exact} "
        f"t={t_emb*1000:.1f}/{t_ext*1000:.1f}/{t_rev*1000:.1f}ms"
    )
    return exact and b == 0.0


def main() -> bool:
    bits = rev._to_bits(PAYLOAD)
    failures = []

    print("== PEE-HS checkerboard pada citra sintetis ==")
    for name, img in make_images().items():
        cap = rev.pee_capacity(img)
        if cap < 8:
            print(f"[INFO] {name}: kapasitas PEE {cap} bit - terlalu kecil, dilewati")
            continue
        if not bench(name, img, bits):
            failures.append(name)

    print("\n== PEE-HS checkerboard pada DICOM MRI nyata ==")
    dcm_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "dataset", "BrainTumorMRI", "IM-0001-0002.dcm",
    )
    try:
        pixels, _ = dicom_load(dcm_path)
        print(f"  shape={pixels.shape} dtype={pixels.dtype} range=[{pixels.min()}, {pixels.max()}]")
        cap = rev.pee_capacity(pixels)
        print(f"  kapasitas PEE = {cap} bit = {cap // 8} byte")
        if cap >= 8 and not bench("MRI", pixels, bits):
            failures.append("MRI")
    except Exception as exc:  # noqa: BLE001
        print(f"[SKIP] DICOM nyata gagal dimuat: {exc}")

    print("\n== PEE-HS multiround (kapasitas kumulatif + roundtrip) ==")
    caps = rev.pee_capacity_multi(pixels, 12)
    total_bits = sum(caps)
    print(f"  MRI per-round (12 round): {caps}")
    print(f"  total = {total_bits} bit = {total_bits // 8} byte")
    big = b"PAYLOAD-ROUNDTRIP:" * 512
    bb = rev._to_bits(big)[:total_bits]
    wm, rounds = rev.pee_embed_multi(pixels, bb, 12)
    got = rev.pee_extract_multi(wm, rounds)
    back = rev.pee_reverse_multi(wm, rounds)
    exact = np.array_equal(pixels, back)
    b = rev.ber(bb, got)
    p = rev.psnr(pixels, wm)
    tag = "PASS" if (exact and b == 0.0) else "FAIL"
    print(f"[{tag}] multiround: {len(rounds)} round, {sum(r['n_bits'] for r in rounds)} bit, "
          f"PSNR={p:.2f}dB BER={b:.4f} exact={exact}")

    print("\n== Perbandingan kapasitas (bit) ==")
    for name, img in {**make_images(), "MRI": None}.items():
        if name == "MRI":
            if "pixels" not in dir():
                continue
            img = pixels
        hs = rev.hs_l_capacity(img, 8)
        pee = rev.pee_capacity(img)
        print(f"  {name}: HS-L={hs} | PEE={pee}")

    print(f"\nHasil: {3 - len(failures)}/3 (di luar SKIP)")
    return len(failures) == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)