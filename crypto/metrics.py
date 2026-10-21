"""Metrik evaluasi untuk jurnal - kualitas citra & kinerja deteksi/lokalisasi tamper.

Modul ini menyediakan:
  - `ssim`: Structural Similarity Index (Wang et al.), numpy + scipy.ndimage.
  - `block_confusion`: perbandingan blok-per-blok antara mask kebenaran (ground truth)
    dan mask hasil verifikasi, plus turunan precision/recall/F1/accuracy/FPR/IoU.

Digunakan oleh `evaluation/journal_eval.py` untuk menghasilkan tabel hasil yang
dapat dipertahankan di jurnal tanpa ketergantungan library eksternal besar.
"""

import numpy as np


def ssim(a: np.ndarray, b: np.ndarray, data_range: float = None, window: int = 11, sigma: float = 1.5) -> float:
    """Structural Similarity Index (SSIM) framing Wang et al., grayscale 2D.

    Nilai 1.0 = identik sempurna. `data_range` default = rentang dynamic dtype
    (255 untuk uint8, 65535 untuk uint16).
    """
    if a.shape != b.shape:
        raise ValueError("dimensi citra harus sama")
    if data_range is None:
        data_range = float(np.iinfo(a.dtype).max) if np.issubdtype(a.dtype, np.integer) else 1.0
    a = a.astype(np.float64)
    b = b.astype(np.float64)

    c1 = (0.01 * data_range) ** 2
    c2 = (0.03 * data_range) ** 2

    from scipy.ndimage import gaussian_filter

    mu_a = gaussian_filter(a, sigma, truncate=window / 2.0)
    mu_b = gaussian_filter(b, sigma, truncate=window / 2.0)
    va = np.maximum(gaussian_filter(a * a, sigma, truncate=window / 2.0) - mu_a * mu_a, 0.0)
    vb = np.maximum(gaussian_filter(b * b, sigma, truncate=window / 2.0) - mu_b * mu_b, 0.0)
    cov = gaussian_filter(a * b, sigma, truncate=window / 2.0) - mu_a * mu_b

    ssim_map = ((2 * mu_a * mu_b + c1) * (2 * cov + c2)) / (
        (mu_a * mu_a + mu_b * mu_b + c1) * (va + vb + c2)
    )
    return float(np.mean(ssim_map))


def _grid(shape, block: int):
    if shape[0] < block or shape[1] < block:
        return 0, 0
    return shape[0] // block, shape[1] // block


def block_confusion(gt_mask: np.ndarray, pred_mask: np.ndarray, block: int = 16) -> dict:
    """Kinerja lokalisasi level-blok antara mask kebenaran dan mask deteksi.

    Mask diinterpretasi boolean (nonzero = tampered). Blok dibandingkan sejajar
    dengan grid `verify_image_rev` (16x16). Mengembalikan dict berisi hitungan
    TP/TN/FP/FN dan turunannya.
    """
    gt = np.asarray(gt_mask, dtype=bool)
    pred = np.asarray(pred_mask, dtype=bool)
    if gt.shape != pred.shape:
        raise ValueError("dimensi mask harus sama")
    gh, gw = _grid(gt.shape, block)
    total = gh * gw
    if total == 0:
        return {
            "total_blocks": 0, "gt_blocks": 0, "tp": 0, "tn": 0, "fp": 0, "fn": 0,
            "precision": 1.0, "recall": 0.0, "f1": 0.0, "accuracy": 1.0, "fpr": 0.0,
            "localization_iou": 0.0,
        }

    gt_b = np.zeros((gh, gw), dtype=bool)
    pr_b = np.zeros((gh, gw), dtype=bool)
    for bi in range(gh):
        for bj in range(gw):
            gt_b[bi, bj] = gt[bi * block:(bi + 1) * block, bj * block:(bj + 1) * block].any()
            pr_b[bi, bj] = pred[bi * block:(bi + 1) * block, bj * block:(bj + 1) * block].any()

    tp = int(np.count_nonzero(gt_b & pr_b))
    fn = int(np.count_nonzero(gt_b & ~pr_b))
    fp = int(np.count_nonzero(~gt_b & pr_b))
    tn = int(np.count_nonzero(~gt_b & ~pr_b))

    def safe(n, d):
        return float(n / d) if d else 0.0

    precision = safe(tp, tp + fp) if (tp + fp) else 1.0
    recall = safe(tp, tp + fn)
    f1 = safe(2 * tp, 2 * tp + fp + fn)
    accuracy = safe(tp + tn, total)
    fpr = safe(fp, fp + tn)
    iou = safe(tp, tp + fp + fn)

    return {
        "total_blocks": total,
        "gt_blocks": int(np.count_nonzero(gt_b)),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall, "f1": f1,
        "accuracy": accuracy, "fpr": fpr, "localization_iou": iou,
    }


def summarize_confusion(results: list) -> dict:
    """Agregasi rata-rata hasil `block_confusion` di banyak kasus."""
    if not results:
        return {}
    keys = ["total_blocks", "gt_blocks", "tp", "tn", "fp", "fn",
            "precision", "recall", "f1", "accuracy", "fpr", "localization_iou"]
    return {k: float(np.mean([r[k] for r in results])) for k in keys}


# ==============================================================================
# PARAMETER EVALUASI LENGKAP: MSE, PSNR, SSIM, NPCR, UACI, ENTROPY, NC, NCC, CHI-SQUARE, BER
# ==============================================================================

def calc_mse(a: np.ndarray, b: np.ndarray) -> float:
    """Mean Squared Error (MSE)."""
    return float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))


def calc_psnr(mse: float, max_val: float = 65535.0) -> float:
    """Peak Signal-to-Noise Ratio (dB)."""
    if mse <= 0:
        return float("inf")
    return float(10.0 * np.log10((max_val ** 2) / mse))


def calc_ssim_robust(a: np.ndarray, b: np.ndarray, data_range: float = None) -> float:
    """SSIM yang mendukung citra 2D grayscale maupun 3D RGB."""
    if a.ndim == 3 and a.shape[2] == 3:
        vals = [ssim(a[:, :, c], b[:, :, c], data_range=data_range) for c in range(3)]
        return float(np.mean(vals))
    return ssim(a, b, data_range=data_range)


def calc_npcr(a: np.ndarray, b: np.ndarray) -> float:
    """Number of Pixels Change Rate (%)."""
    diff = (a != b)
    return float(np.count_nonzero(diff) / diff.size * 100.0)


def calc_uaci(a: np.ndarray, b: np.ndarray, max_val: float = 65535.0) -> float:
    """Unified Average Changing Intensity (%)."""
    diff = np.abs(a.astype(np.float64) - b.astype(np.float64))
    return float(np.mean(diff) / max_val * 100.0)


def calc_entropy(img: np.ndarray) -> float:
    """Shannon Information Entropy (bits per pixel)."""
    vals, counts = np.unique(img, return_counts=True)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log2(probs)))


def calc_entropy_bytes(data: bytes) -> float:
    """Shannon Information Entropy untuk byte data (bits per byte, maks 8.0)."""
    if not data:
        return 0.0
    arr = np.frombuffer(data, dtype=np.uint8)
    vals, counts = np.unique(arr, return_counts=True)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log2(probs)))


def calc_nc(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized Correlation (rentang 0 s.d. 1.0)."""
    a_f = a.astype(np.float64).ravel()
    b_f = b.astype(np.float64).ravel()
    denom = np.sqrt(np.sum(a_f ** 2) * np.sum(b_f ** 2))
    if denom == 0:
        return 1.0
    return float(np.sum(a_f * b_f) / denom)


def calc_ncc(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized Cross-Correlation (Pearson correlation terpusat di mean)."""
    a_f = a.astype(np.float64).ravel()
    b_f = b.astype(np.float64).ravel()
    a_diff = a_f - np.mean(a_f)
    b_diff = b_f - np.mean(b_f)
    denom = np.sqrt(np.sum(a_diff ** 2) * np.sum(b_diff ** 2))
    if denom == 0:
        return 1.0
    return float(np.sum(a_diff * b_diff) / denom)


def calc_chi_square_hist(a: np.ndarray, b: np.ndarray) -> float:
    """Jarak Chi-Square (X^2 divergence) antara histogram dua citra."""
    max_val = max(int(a.max()), int(b.max()))
    hist_a = np.bincount(a.ravel(), minlength=max_val + 1)
    hist_b = np.bincount(b.ravel(), minlength=max_val + 1)
    mask = (hist_a + hist_b) > 0
    ha = hist_a[mask].astype(np.float64)
    hb = hist_b[mask].astype(np.float64)
    return float(0.5 * np.sum(((ha - hb) ** 2) / (ha + hb)))


def calc_chi_square_uniformity_bytes(data: bytes) -> tuple:
    """Chi-Square Goodness-of-Fit untuk keseragaman distribusi byte ciphertext AES-256."""
    if not data:
        return 0.0, 1.0
    arr = np.frombuffer(data, dtype=np.uint8)
    n = len(arr)
    expected = n / 256.0
    counts = np.bincount(arr, minlength=256)
    chi2 = float(np.sum(((counts - expected) ** 2) / expected))
    try:
        import scipy.stats
        p_val = float(1.0 - scipy.stats.chi2.cdf(chi2, df=255))
    except Exception:
        p_val = 1.0
    return chi2, p_val


def calc_ber(a: np.ndarray, b: np.ndarray) -> float:
    """Bit Error Rate (BER) antara representasi biner dua array."""
    a_bits = np.unpackbits(np.frombuffer(a.tobytes(), dtype=np.uint8))
    b_bits = np.unpackbits(np.frombuffer(b.tobytes(), dtype=np.uint8))
    if a_bits.size != b_bits.size:
        min_sz = min(a_bits.size, b_bits.size)
        a_bits = a_bits[:min_sz]
        b_bits = b_bits[:min_sz]
    errs = np.count_nonzero(a_bits != b_bits)
    return float(errs / a_bits.size) if a_bits.size else 0.0


def evaluate_comprehensive_metrics(
    orig: np.ndarray,
    wm: np.ndarray,
    rec: np.ndarray = None,
    cipher_bytes: bytes = None,
    is_dicom: bool = True,
    bits_stored: int = 16,
) -> dict:
    """Evaluasi lengkap 10 parameter evaluasi standar dosen dan publikasi ilmiah.

    Mengukur: MSE, PSNR, SSIM, UACI, NPCR (imperceptibility),
    Entropy, NC, NCC, Chi-Square (X^2), dan BER.
    """
    if is_dicom and orig.ndim == 2 and orig.shape[0] > 16:
        # Pisahkan wilayah diagnostik (ROI) 432 baris teratas dan strip RONI 16 baris terbawah
        reg_len = orig.shape[0] - 16
        orig_diag = orig[:reg_len]
        wm_diag = wm[:reg_len]
        rec_diag = rec[:reg_len] if rec is not None else None
    else:
        orig_diag = orig
        wm_diag = wm
        rec_diag = rec

    max_16 = 65535.0 if (orig.dtype == np.uint16 or is_dicom) else 255.0
    max_stored = float((1 << bits_stored) - 1) if bits_stored else max_16

    # 1. MSE
    mse_wm = calc_mse(orig_diag, wm_diag)
    mse_rec = calc_mse(orig_diag, rec_diag) if rec_diag is not None else 0.0

    # 2. PSNR
    psnr_wm_16 = calc_psnr(mse_wm, max_16)
    psnr_wm_stored = calc_psnr(mse_wm, max_stored)
    psnr_rec = calc_psnr(mse_rec, max_16) if rec_diag is not None else float("inf")

    # 3. SSIM
    ssim_wm = calc_ssim_robust(orig_diag, wm_diag, data_range=max_16)
    ssim_rec = calc_ssim_robust(orig_diag, rec_diag, data_range=max_16) if rec_diag is not None else 1.0

    # 4. NPCR (%)
    npcr_wm = calc_npcr(orig_diag, wm_diag)
    npcr_rec = calc_npcr(orig_diag, rec_diag) if rec_diag is not None else 0.0

    # 5. UACI (%)
    uaci_wm = calc_uaci(orig_diag, wm_diag, max_16)
    uaci_wm_stored = calc_uaci(orig_diag, wm_diag, max_stored)
    uaci_rec = calc_uaci(orig_diag, rec_diag, max_16) if rec_diag is not None else 0.0

    # 6. Entropy (bits)
    ent_orig = calc_entropy(orig_diag)
    ent_wm = calc_entropy(wm_diag)
    ent_rec = calc_entropy(rec_diag) if rec_diag is not None else ent_orig
    delta_ent = abs(ent_wm - ent_orig)
    ent_cipher = calc_entropy_bytes(cipher_bytes) if cipher_bytes else 0.0

    # 7. NC & NCC
    nc_wm = calc_nc(orig_diag, wm_diag)
    nc_rec = calc_nc(orig_diag, rec_diag) if rec_diag is not None else 1.0
    ncc_wm = calc_ncc(orig_diag, wm_diag)
    ncc_rec = calc_ncc(orig_diag, rec_diag) if rec_diag is not None else 1.0

    # 8. Chi-Square (X^2)
    chi2_hist = calc_chi_square_hist(orig_diag, wm_diag)
    chi2_cipher, p_cipher = calc_chi_square_uniformity_bytes(cipher_bytes) if cipher_bytes else (0.0, 1.0)

    # 9. BER
    ber_wm = calc_ber(orig_diag, wm_diag)
    ber_rec = calc_ber(orig_diag, rec_diag) if rec_diag is not None else 0.0

    return {
        # Raw Float Values
        "mse_wm": mse_wm,
        "mse_rec": mse_rec,
        "psnr_wm_16": psnr_wm_16,
        "psnr_wm_stored": psnr_wm_stored,
        "psnr_rec": psnr_rec,
        "ssim_wm": ssim_wm,
        "ssim_rec": ssim_rec,
        "npcr_wm": npcr_wm,
        "npcr_rec": npcr_rec,
        "uaci_wm": uaci_wm,
        "uaci_wm_stored": uaci_wm_stored,
        "uaci_rec": uaci_rec,
        "ent_orig": ent_orig,
        "ent_wm": ent_wm,
        "ent_rec": ent_rec,
        "delta_ent": delta_ent,
        "ent_cipher": ent_cipher,
        "nc_wm": nc_wm,
        "nc_rec": nc_rec,
        "ncc_wm": ncc_wm,
        "ncc_rec": ncc_rec,
        "chi2_hist": chi2_hist,
        "chi2_cipher": chi2_cipher,
        "p_cipher": p_cipher,
        "ber_wm": ber_wm,
        "ber_rec": ber_rec,

        # Formatted Presentation Strings
        "mse_wm_str": f"{mse_wm:.4f}" if mse_wm < 100 else f"{mse_wm:.2f}",
        "mse_rec_str": "0.0000" if mse_rec == 0 else f"{mse_rec:.6f}",
        "psnr_wm_str": "inf" if psnr_wm_16 == float("inf") else f"{psnr_wm_16:.2f} dB",
        "psnr_wm_stored_str": f"{psnr_wm_stored:.2f} dB",
        "psnr_rec_str": "∞ (Bit-Exact)" if psnr_rec == float("inf") else f"{psnr_rec:.2f} dB",
        "ssim_wm_str": f"{ssim_wm:.6f}",
        "ssim_rec_str": f"{ssim_rec:.6f}",
        "npcr_wm_str": f"{npcr_wm:.2f}%",
        "npcr_rec_str": f"{npcr_rec:.2f}%",
        "uaci_wm_str": f"{uaci_wm:.4f}%",
        "uaci_wm_stored_str": f"{uaci_wm_stored:.4f}%",
        "uaci_rec_str": f"{uaci_rec:.4f}%",
        "ent_orig_str": f"{ent_orig:.4f} bit",
        "ent_wm_str": f"{ent_wm:.4f} bit",
        "ent_rec_str": f"{ent_rec:.4f} bit",
        "delta_ent_str": f"{delta_ent:.5f} bit",
        "ent_cipher_str": f"{ent_cipher:.4f} bit/B",
        "nc_wm_str": f"{nc_wm:.6f}",
        "nc_rec_str": f"{nc_rec:.6f}",
        "ncc_wm_str": f"{ncc_wm:.6f}",
        "ncc_rec_str": f"{ncc_rec:.6f}",
        "chi2_hist_str": f"{chi2_hist:.2f}",
        "chi2_cipher_str": f"X²={chi2_cipher:.1f} (p={p_cipher:.4f})",
        "ber_wm_str": f"{ber_wm:.6f}",
        "ber_rec_str": "0.00000000" if ber_rec == 0 else f"{ber_rec:.8f}",
    }