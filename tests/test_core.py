import io
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto import aes
from crypto.tamper import (
    extract_block_watermarks,
    mark_tampered,
    protect_image,
    verify_image,
)
from crypto.watermark import embed_bytes, extract_bytes, lsb_capacity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

PASSPHRASE = "kunci-prototipe-2026"
METADATA = b"PATIENT:AE-0001;STUDY:CHEST-XRAY;DATE:2026-09-17"
WRONG_METADATA = b"PATIENT:EVIL-9999;STUDY:CHEST-XRAY;DATE:2026-09-17"

TAMPER_ROWS = slice(60, 64)
TAMPER_COLS = slice(88, 92)


def psnr(original: np.ndarray, modified: np.ndarray) -> float:
    mse = np.mean((original.astype(np.float64) - modified.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")
    return float(10 * np.log10(255.0 ** 2 / mse))


failures = []


def run(name: str, ok: bool, detail: str = ""):
    if not ok:
        failures.append(name)
    if ok:
        print(f"[PASS] {name}" + (f" — {detail}" if detail else ""))
    else:
        print(f"[FAIL] {name}" + (f" — {detail}" if detail else ""))


def main() -> bool:
    os.makedirs(DATA_DIR, exist_ok=True)

    rng = np.random.default_rng(42)
    original = rng.integers(0, 256, size=(128, 128, 3), dtype=np.uint8)
    print(f"Kapasitas LSB per kanal: {lsb_capacity(original)} byte")

    probe = np.array(original, copy=True)
    probe = embed_bytes(probe, b"uji-embedding", channel=2)
    run("LSB embed/extract membulat", extract_bytes(probe, channel=2) == b"uji-embedding")

    protected = protect_image(original, METADATA)
    protected_png = os.path.join(DATA_DIR, "watermarked.png")
    Image.fromarray(protected).save(protected_png)

    p1 = psnr(original, protected)
    run("PSNR tetap tinggi (>45 dB)", p1 > 45, f"PSNR={p1:.2f} dB")

    with open(protected_png, "rb") as f:
        png_bytes = f.read()

    t0 = time.perf_counter()
    encrypted = aes.encrypt(png_bytes, PASSPHRASE)
    t_enc = time.perf_counter() - t0
    run(
        "Enkripsi AES berhasil",
        len(encrypted) > len(png_bytes),
        f"{len(png_bytes)} -> {len(encrypted)} byte, {t_enc*1000:.1f} ms",
    )

    cipher_path = os.path.join(DATA_DIR, "cipher.bin")
    with open(cipher_path, "wb") as f:
        f.write(encrypted)

    t0 = time.perf_counter()
    decrypted = aes.decrypt(encrypted, PASSPHRASE)
    t_dec = time.perf_counter() - t0
    run("Dekripsi mengembalikan file asli", decrypted == png_bytes, f"{t_dec*1000:.1f} ms")

    try:
        aes.decrypt(encrypted, "kunci-salah")
        run("Kunci salah ditolak", False)
    except ValueError:
        run("Kunci salah ditolak", True)

    recovered = np.array(Image.open(io.BytesIO(decrypted)).convert("RGB"))
    verdict = verify_image(recovered, METADATA)
    run(
        "Tanpa tamper: piksel bersih + metadata valid",
        (not verdict["pixel_tamper"]) and verdict["metadata_ok"],
    )

    tampered = np.array(recovered, copy=True)
    tampered[TAMPER_ROWS, TAMPER_COLS] = np.clip(
        tampered[TAMPER_ROWS, TAMPER_COLS].astype(np.int16) + 40, 0, 255
    ).astype(np.uint8)

    verdict2 = verify_image(tampered, METADATA)
    mask = verdict2["mask"]
    mask_px = int((mask == 255).sum())
    run("Manipulasi piksel terdeteksi", verdict2["pixel_tamper"], f"{mask_px} piksel ditandai")

    expected_rows = slice(56, 64)
    expected_cols = slice(88, 96)
    localized = bool((mask[expected_rows, expected_cols] == 255).all())
    run("Lokalisasi presisi (1 blok 8x8)", localized and mask_px == 64)

    verdict3 = verify_image(recovered, WRONG_METADATA)
    run(
        "Perubahan metadata pasien terdeteksi",
        (not verdict3["metadata_ok"]) and (not verdict3["pixel_tamper"]),
    )

    overlay = mark_tampered(tampered, mask)
    overlay_path = os.path.join(DATA_DIR, "tamper_overlay.png")
    Image.fromarray(overlay).save(overlay_path)

    total = 8
    passed = total - len(failures)
    print(f"\nHasil: {passed}/{total} lulus")
    print(f"File hasil: {protected_png} | {cipher_path} | {overlay_path}")
    return len(failures) == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)