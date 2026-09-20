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