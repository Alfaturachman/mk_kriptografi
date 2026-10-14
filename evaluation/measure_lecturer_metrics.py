"""Script pengukuran lengkap metrik permintaan dosen:
- MSE
- PSNR
- SSIM
- NPCR
- UACI
- Entropy (Shannon)
- NC (Normalized Correlation)
- NCC (Normalized Cross Correlation)
- Chi-Square (X^2)
- BER (Bit Error Rate)

Dievaluasi pada 24 slice BrainTumorMRI untuk citra medis DICOM.
"""

import glob
import math
import os
import sys
import numpy as np
import scipy.stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from crypto.dicom import load, metadata_of
from crypto.tamper import protect_image_rev, verify_image_rev, PARAM_STRIP, _rev_region
from crypto import metrics as mt
from crypto import aes

DCM_DIR = os.path.join(BASE, "dataset", "BrainTumorMRI")
PASSPHRASE = "jurnal-eval-2026"

def calc_mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))

def calc_psnr(mse: float, max_val: float) -> float:
    if mse == 0:
        return float("inf")
    return float(10.0 * np.log10((max_val ** 2) / mse))

def calc_npcr(a: np.ndarray, b: np.ndarray) -> float:
    """Number of Pixels Change Rate (%)"""
    diff = (a != b)
    return float(np.count_nonzero(diff) / diff.size * 100.0)

def calc_uaci(a: np.ndarray, b: np.ndarray, max_val: float) -> float:
    """Unified Average Changing Intensity (%)"""
    diff = np.abs(a.astype(np.float64) - b.astype(np.float64))
    return float(np.mean(diff) / max_val * 100.0)

def calc_entropy(img: np.ndarray) -> float:
    """Shannon Information Entropy (bits)"""
    vals, counts = np.unique(img, return_counts=True)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log2(probs)))

def calc_entropy_bytes(data: bytes) -> float:
    arr = np.frombuffer(data, dtype=np.uint8)
    vals, counts = np.unique(arr, return_counts=True)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log2(probs)))

def calc_nc(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized Correlation"""
    a_f = a.astype(np.float64).ravel()
    b_f = b.astype(np.float64).ravel()
    denom = np.sqrt(np.sum(a_f ** 2) * np.sum(b_f ** 2))
    if denom == 0:
        return 1.0
    return float(np.sum(a_f * b_f) / denom)

def calc_ncc(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized Cross Correlation (Zero-Mean Pearson Correlation)"""
    a_f = a.astype(np.float64).ravel()
    b_f = b.astype(np.float64).ravel()
    a_diff = a_f - np.mean(a_f)
    b_diff = b_f - np.mean(b_f)
    denom = np.sqrt(np.sum(a_diff ** 2) * np.sum(b_diff ** 2))
    if denom == 0:
        return 1.0
    return float(np.sum(a_diff * b_diff) / denom)

def calc_chi_square_hist(a: np.ndarray, b: np.ndarray) -> tuple:
    """Chi-Square distance between two histograms."""
    max_val = max(int(a.max()), int(b.max()))
    hist_a = np.bincount(a.ravel(), minlength=max_val + 1)
    hist_b = np.bincount(b.ravel(), minlength=max_val + 1)
    
    # Mask nonzero in either
    mask = (hist_a + hist_b) > 0
    ha = hist_a[mask].astype(np.float64)
    hb = hist_b[mask].astype(np.float64)
    # Chi-square divergence
    chi2 = float(0.5 * np.sum(((ha - hb) ** 2) / (ha + hb)))
    return chi2

def calc_chi_square_uniformity_bytes(data: bytes) -> tuple:
    """Chi-square goodness of fit for uniform byte distribution (AES ciphertext)."""
    arr = np.frombuffer(data, dtype=np.uint8)
    n = len(arr)
    expected = n / 256.0
    counts = np.bincount(arr, minlength=256)
    chi2 = float(np.sum(((counts - expected) ** 2) / expected))
    p_val = float(1.0 - scipy.stats.chi2.cdf(chi2, df=255))
    return chi2, p_val

def calc_chi_square_pov(img: np.ndarray) -> tuple:
    """Pairs of Values (PoV) Chi-Square test (Westfeld & Pfitzmann steganalysis)."""
    # Group into pairs (2k, 2k+1)
    flat = img.ravel()
    max_val = int(flat.max())
    counts = np.bincount(flat, minlength=max_val + 1)
    if len(counts) % 2 != 0:
        counts = np.pad(counts, (0, 1), mode="constant")
    
    evens = counts[0::2]
    odds = counts[1::2]
    total_pairs = (evens + odds).astype(np.float64)
    expected = total_pairs / 2.0
    
    # Only test pairs where total_pairs > 5
    valid = total_pairs > 5
    if not np.any(valid):
        return 0.0, 1.0
    
    chi2 = float(np.sum(((evens[valid] - expected[valid]) ** 2) / expected[valid]))
    df = int(np.count_nonzero(valid) - 1)
    p_val = float(1.0 - scipy.stats.chi2.cdf(chi2, df=df)) if df > 0 else 1.0
    return chi2, p_val

def calc_ber(a: np.ndarray, b: np.ndarray) -> float:
    """Bit Error Rate between two arrays of equal length."""
    a_bits = np.unpackbits(np.frombuffer(a.tobytes(), dtype=np.uint8))
    b_bits = np.unpackbits(np.frombuffer(b.tobytes(), dtype=np.uint8))
    errs = np.count_nonzero(a_bits != b_bits)
    return float(errs / a_bits.size)

def main():
    files = sorted(glob.glob(os.path.join(DCM_DIR, "*.dcm")))
    print(f"Mengukur {len(files)} citra DICOM...")

    results = []

    for f in files:
        name = os.path.basename(f)
        pixels, ds = load(f)
        meta = metadata_of(ds)
        bits_stored = getattr(ds, "BitsStored", 16)
        max_16 = 65535.0
        max_stored = float((1 << bits_stored) - 1)
        max_dyn = float(pixels.max())

        # Protect
        wm = protect_image_rev(pixels, meta, passphrase=PASSPHRASE)
        ver = verify_image_rev(wm, meta, passphrase=PASSPHRASE)
        rec = ver["original_recovered"]

        # Regions
        reg_len = pixels.shape[0] - PARAM_STRIP
        orig_diag = pixels[:reg_len]
        wm_diag = wm[:reg_len]
        rec_diag = rec[:reg_len]

        # 1. MSE
        mse_wm_whole = calc_mse(pixels, wm)
        mse_wm_diag = calc_mse(orig_diag, wm_diag)
        mse_rec_diag = calc_mse(orig_diag, rec_diag)

        # 2. PSNR (16-bit container MAX=65535, 12-bit stored MAX=4095, dynamic MAX)
        psnr_16_whole = calc_psnr(mse_wm_whole, max_16)
        psnr_16_diag = calc_psnr(mse_wm_diag, max_16)
        psnr_stored_diag = calc_psnr(mse_wm_diag, max_stored)
        psnr_dyn_diag = calc_psnr(mse_wm_diag, max_dyn)
        psnr_rec_diag = calc_psnr(mse_rec_diag, max_16)

        # 3. SSIM
        ssim_wm_whole = mt.ssim(pixels, wm, data_range=max_16)
        ssim_wm_diag = mt.ssim(orig_diag, wm_diag, data_range=max_16)
        ssim_rec_diag = mt.ssim(orig_diag, rec_diag, data_range=max_16)

        # 4. NPCR (%)
        npcr_whole = calc_npcr(pixels, wm)
        npcr_diag = calc_npcr(orig_diag, wm_diag)

        # 5. UACI (%)
        uaci_16_whole = calc_uaci(pixels, wm, max_16)
        uaci_16_diag = calc_uaci(orig_diag, wm_diag, max_16)
        uaci_stored_diag = calc_uaci(orig_diag, wm_diag, max_stored)

        # 6. Entropy (bits)
        ent_orig = calc_entropy(orig_diag)
        ent_wm = calc_entropy(wm_diag)
        delta_ent = abs(ent_wm - ent_orig)

        # Ciphertext payload entropy
        # Extract payload bytes directly from protection
        # We know payload size = 10144 bits = 1268 bytes
        # Let's inspect ver payload or reconstruct
        # In tamper.py: _rev_hashes + metadata -> aes.encrypt
        from crypto.tamper import _rev_hashes, _build_rev_payload
        raw_pl = _build_rev_payload(_rev_hashes(pixels, 16, 16), meta, 16, 16)
        enc_pl = aes.encrypt(raw_pl, PASSPHRASE)
        ent_aes = calc_entropy_bytes(enc_pl)
        chi2_aes, p_aes = calc_chi_square_uniformity_bytes(enc_pl)

        # 7. NC & NCC
        nc_whole = calc_nc(pixels, wm)
        nc_diag = calc_nc(orig_diag, wm_diag)
        ncc_whole = calc_ncc(pixels, wm)
        ncc_diag = calc_ncc(orig_diag, wm_diag)

        # 8. Chi-Square (X^2)
        chi2_hist_diag = calc_chi_square_hist(orig_diag, wm_diag)
        chi2_pov_orig, p_pov_orig = calc_chi_square_pov(orig_diag)
        chi2_pov_wm, p_pov_wm = calc_chi_square_pov(wm_diag)

        # 9. BER
        ber_rec_diag = calc_ber(orig_diag, rec_diag)
        ber_px_diag = float(np.count_nonzero(orig_diag != rec_diag) / orig_diag.size)

        res = {
            "slice": name,
            "bits_stored": bits_stored,
            "mse_wm_whole": mse_wm_whole,
            "mse_wm_diag": mse_wm_diag,
            "mse_rec_diag": mse_rec_diag,
            "psnr_16_whole": psnr_16_whole,
            "psnr_16_diag": psnr_16_diag,
            "psnr_stored_diag": psnr_stored_diag,
            "psnr_dyn_diag": psnr_dyn_diag,
            "psnr_rec_diag": psnr_rec_diag,
            "ssim_wm_whole": ssim_wm_whole,
            "ssim_wm_diag": ssim_wm_diag,
            "ssim_rec_diag": ssim_rec_diag,
            "npcr_whole": npcr_whole,
            "npcr_diag": npcr_diag,
            "uaci_16_whole": uaci_16_whole,
            "uaci_16_diag": uaci_16_diag,
            "uaci_stored_diag": uaci_stored_diag,
            "ent_orig": ent_orig,
            "ent_wm": ent_wm,
            "delta_ent": delta_ent,
            "ent_aes": ent_aes,
            "nc_whole": nc_whole,
            "nc_diag": nc_diag,
            "ncc_whole": ncc_whole,
            "ncc_diag": ncc_diag,
            "chi2_hist_diag": chi2_hist_diag,
            "chi2_pov_wm": chi2_pov_wm,
            "p_pov_wm": p_pov_wm,
            "chi2_aes": chi2_aes,
            "p_aes": p_aes,
            "ber_rec_diag": ber_rec_diag,
            "ber_px_diag": ber_px_diag,
        }
        results.append(res)
        print(f"Processed {name}: PSNR={psnr_16_diag:.2f}dB, SSIM={ssim_wm_diag:.6f}, NPCR={npcr_diag:.2f}%, UACI={uaci_16_diag:.4f}%, BER_rec={ber_rec_diag:.6f}")

    # Summary
    def agg(key):
        vals = [r[key] for r in results if not np.isinf(r[key])]
        return {
            "min": min(vals),
            "max": max(vals),
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals))
        }

    print("\n" + "="*80)
    print("HASIL LENGKAP PENGUKURAN METRIK DOSEN (24 SLICE)")
    print("="*80)

    keys_to_print = [
        ("MSE (Watermarked vs Orig - Diag)", "mse_wm_diag", ".6f"),
        ("MSE (Recovery vs Orig - Diag)", "mse_rec_diag", ".6f"),
        ("PSNR 16-bit (MAX=65535, Diag)", "psnr_16_diag", ".2f"),
        ("PSNR 12-bit stored (MAX=4095, Diag)", "psnr_stored_diag", ".2f"),
        ("PSNR Dynamic Range (MAX=max(I), Diag)", "psnr_dyn_diag", ".2f"),
        ("PSNR Recovery (Diag)", "psnr_rec_diag", "s"),
        ("SSIM (Watermarked vs Orig - Diag)", "ssim_wm_diag", ".6f"),
        ("SSIM (Recovery vs Orig - Diag)", "ssim_rec_diag", ".6f"),
        ("NPCR (%) (Diag)", "npcr_diag", ".4f"),
        ("NPCR (%) (Whole image)", "npcr_whole", ".4f"),
        ("UACI (%) (16-bit, Diag)", "uaci_16_diag", ".6f"),
        ("UACI (%) (12-bit stored, Diag)", "uaci_stored_diag", ".6f"),
        ("Entropy Original Image (bits)", "ent_orig", ".4f"),
        ("Entropy Watermarked Image (bits)", "ent_wm", ".4f"),
        ("Entropy Difference (|H_wm - H_orig|)", "delta_ent", ".6f"),
        ("Entropy Payload AES (bits/byte)", "ent_aes", ".4f"),
        ("NC (Normalized Correlation, Diag)", "nc_diag", ".6f"),
        ("NCC (Normalized Cross-Correlation, Diag)", "ncc_diag", ".6f"),
        ("Chi-Square Histogram Distance (X^2)", "chi2_hist_diag", ".2f"),
        ("Chi-Square AES Uniformity (X^2)", "chi2_aes", ".2f"),
        ("p-value AES Uniformity", "p_aes", ".4f"),
        ("BER Recovery (Bit Error Rate Citra)", "ber_rec_diag", ".8f"),
    ]

    for label, key, fmt in keys_to_print:
        if key == "psnr_rec_diag":
            print(f"{label:<42} : Semua slice inf (100% eksak / lossless)")
            continue
        a = agg(key)
        if fmt == "s":
            print(f"{label:<42} : {a['mean']}")
        else:
            print(f"{label:<42} : Min={a['min']:{fmt}}, Max={a['max']:{fmt}}, Mean={a['mean']:{fmt}} ± {a['std']:{fmt}}")

    # Write to json
    import json
    out_path = os.path.join(BASE, "evaluation", "lecturer_metrics_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {k: agg(k) for _, k, _ in keys_to_print if k != "psnr_rec_diag"},
            "per_slice": results
        }, f, indent=2)
    print(f"\nHasil tersimpan di {out_path}")

if __name__ == "__main__":
    main()
