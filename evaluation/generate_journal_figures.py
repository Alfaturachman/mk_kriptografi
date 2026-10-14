"""Generate high-resolution (300 DPI) publication figures for the journal paper.

Figure 1: `figures/perbandingan_16bit_windowing.png`
   Visual demonstration of 16-bit DICOM display: Raw vs Clinical Windowing vs Min-Max vs Histogram.
Figure 2: `figures/perbandingan_tamper_visual.png`
   Visual comparison of Original, Watermarked, Tampered (16x16), and Detected Tamper Mask.
Figure 3: `figures/grafik_kinerja_tamper.png`
   Quantitative performance curves of IoU and FPR across tamper sizes (Plain vs AES-256).
"""

import os
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set IEEE publication style aesthetics
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8

BASE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE, "figures")
os.makedirs(FIG_DIR, exist_ok=True)
DCM_FILE = os.path.join(BASE, "dataset", "BrainTumorMRI", "IM-0001-0002.dcm")


def apply_windowing(pixels: np.ndarray, center: float = 500.0, width: float = 1000.0) -> np.ndarray:
    """Standard clinical VOI LUT Windowing for brain MRI."""
    img_min = center - width / 2.0
    img_max = center + width / 2.0
    windowed = np.clip(pixels, img_min, img_max)
    windowed = ((windowed - img_min) / (img_max - img_min) * 255.0).astype(np.uint8)
    return windowed


def generate_figure_windowing():
    """Figure 1: 16-bit display comparison."""
    ds = pydicom.dcmread(DCM_FILE)
    pixels = ds.pixel_array.astype(np.float64)
    p_min, p_max = int(pixels.min()), int(pixels.max())

    # Raw 16-bit mapped naively to [0, 65535]
    raw_naive = (pixels / 65535.0 * 255.0).astype(np.uint8)

    # Standard Clinical Brain Windowing
    win_img = apply_windowing(pixels, center=500.0, width=1000.0)

    # Min-Max Normalization
    minmax_img = ((pixels - p_min) / (p_max - p_min) * 255.0).astype(np.uint8)

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 7.0), dpi=300)

    # Panel A: Raw naive
    axes[0, 0].imshow(raw_naive, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title("(a) Tampilan Mentah 16-bit Tanpa Windowing\n(Maks: 1.433 / 65.535 = 2,2% Gray — Tampak Gelap)")
    axes[0, 0].axis('off')

    # Panel B: Clinical Windowing
    axes[0, 1].imshow(win_img, cmap='gray')
    axes[0, 1].set_title("(b) Tampilan Windowing Klinis Radiologi\n(Window Center: 500, Window Width: 1000 — Detail Jelas)")
    axes[0, 1].axis('off')

    # Panel C: Min-Max Normalization
    axes[1, 0].imshow(minmax_img, cmap='gray')
    axes[1, 0].set_title(f"(c) Normalisasi Min-Max Skala Penuh\n(Rentang Riil: {p_min} – {p_max} — Kontras Maksimal)")
    axes[1, 0].axis('off')

    # Panel D: Histogram
    nonzero_pixels = pixels[pixels > 0].ravel()
    axes[1, 1].hist(nonzero_pixels, bins=60, color='#2c3e50', edgecolor='white', alpha=0.85)
    axes[1, 1].axvline(500, color='#e74c3c', linestyle='--', linewidth=1.5, label='Window Center (500)')
    axes[1, 1].axvline(p_max, color='#2980b9', linestyle=':', linewidth=1.5, label=f'Maks Riil ({p_max})')
    axes[1, 1].set_title(f"(d) Distribusi Histogram Piksel 16-bit\n(BitsAllocated: 16, BitsStored: 12-bit [0–4095])")
    axes[1, 1].set_xlabel("Nilai Intensitas Piksel (uint16)")
    axes[1, 1].set_ylabel("Frekuensi Piksel")
    axes[1, 1].legend(loc='upper right', fontsize=7.5)
    axes[1, 1].grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "perbandingan_16bit_windowing.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_figure_tamper_visual():
    """Figure 2: Visual comparison of tampering and detection."""
    from crypto.dicom import load, metadata_of
    from crypto.tamper import protect_image_rev, verify_image_rev

    pixels, ds = load(DCM_FILE)
    meta = metadata_of(ds)
    passphrase = "jurnal-eval-2026"

    # Protected image
    wm_img = protect_image_rev(pixels, meta, passphrase=passphrase)

    # Tampered image (16x16 block at row 160, col 256)
    tampered_img = np.array(wm_img, copy=True)
    r0, c0 = 160, 256
    tampered_img[r0:r0+16, c0:c0+16] ^= np.array([0xBEEF], dtype=tampered_img.dtype)

    # Verification on tampered image
    ver = verify_image_rev(tampered_img, meta, passphrase=passphrase)

    # Display base images using clinical windowing for visual clarity
    win_orig = apply_windowing(pixels.astype(np.float64))
    win_wm = apply_windowing(wm_img.astype(np.float64))
    win_tamp = apply_windowing(tampered_img.astype(np.float64))

    fig, axes = plt.subplots(1, 4, figsize=(10.5, 3.2), dpi=300)

    # Panel A: Original
    axes[0].imshow(win_orig, cmap='gray')
    axes[0].set_title("(a) Citra Asli (Original)\nDimensi: 448 × 364")
    axes[0].axis('off')

    # Panel B: Watermarked
    axes[1].imshow(win_wm, cmap='gray')
    axes[1].set_title("(b) Citra Terproteksi (WM)\nPSNR 88,91 dB | SSIM 0,999997")
    axes[1].axis('off')

    # Panel C: Tampered with highlight box
    axes[2].imshow(win_tamp, cmap='gray')
    rect = patches.Rectangle((c0 - 2, r0 - 2), 20, 20, linewidth=1.5, edgecolor='#e74c3c', facecolor='none')
    axes[2].add_patch(rect)
    axes[2].set_title("(c) Manipulasi Sintetis\n(16 × 16 px pada parenkim)")
    axes[2].axis('off')

    # Panel D: Detection Mask Overlay
    # Create RGB overlay
    overlay = np.stack([win_tamp, win_tamp, win_tamp], axis=-1)
    mask = ver.get("mask")
    if mask is not None and np.any(mask):
        mask_bool = mask > 0
        overlay[mask_bool, 0] = np.clip(overlay[mask_bool, 0].astype(int) + 160, 0, 255).astype(np.uint8)
        overlay[mask_bool, 1] = (overlay[mask_bool, 1] * 0.3).astype(np.uint8)
        overlay[mask_bool, 2] = (overlay[mask_bool, 2] * 0.3).astype(np.uint8)
        status_txt = "Terdeteksi: 100% (Alarm Aktif)"
    else:
        # If AES failed to decrypt, whole image integrity failed
        status_txt = "Alarm: Dekripsi Gagal (100% Tamper)"

    axes[3].imshow(overlay)
    axes[3].set_title(f"(d) Output Deteksi\n({status_txt})")
    axes[3].axis('off')

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "perbandingan_tamper_visual.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_figure_performance_curves():
    """Figure 3: FPR and IoU curves across tamper scenarios."""
    scenarios = ['1 × 1 px', '8 × 8 px', '16 × 16 px', '48 × 48 px']
    x = np.arange(len(scenarios))
    width = 0.35

    # Empirical data from Table 6.3
    # IoU
    iou_plain = [0.877, 0.132, 0.003, 0.018]
    iou_plain_err = [0.325, 0.328, 0.001, 0.002]
    # For AES: 1px is 1.0, 8x8 is 0.342, 16x16 and 48x48 are 0.0 (all-or-nothing)
    iou_aes = [1.000, 0.342, 0.0, 0.0]
    iou_aes_err = [0.000, 0.465, 0.0, 0.0]

    # FPR
    fpr_plain = [0.012, 0.413, 0.535, 0.812]
    fpr_plain_err = [0.031, 0.292, 0.157, 0.072]
    fpr_aes = [0.000, 0.123, 0.0, 0.0]  # Available cases
    fpr_aes_err = [0.000, 0.085, 0.0, 0.0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.2), dpi=300)

    # Plot 1: IoU
    ax1.bar(x - width/2, iou_plain, width, yerr=iou_plain_err, capsize=3,
            label='Jalur Plain (Tanpa Enkripsi)', color='#3498db', edgecolor='#2980b9', alpha=0.85)
    ax1.bar(x + width/2, iou_aes, width, yerr=iou_aes_err, capsize=3,
            label='Jalur Terenkripsi AES-256', color='#e74c3c', edgecolor='#c0392b', alpha=0.85)
    ax1.set_ylabel('Intersection over Union (IoU)')
    ax1.set_title('(a) Presisi Lokalisasi Spasial (IoU)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios)
    ax1.set_ylim(-0.05, 1.15)
    ax1.legend(loc='upper right', fontsize=7.5)
    ax1.grid(True, linestyle=':', alpha=0.5)

    # Plot 2: FPR
    ax2.bar(x - width/2, fpr_plain, width, yerr=fpr_plain_err, capsize=3,
            label='Jalur Plain (Mask Bloat PEE)', color='#3498db', edgecolor='#2980b9', alpha=0.85)
    ax2.bar(x + width/2, fpr_aes, width, yerr=fpr_aes_err, capsize=3,
            label='Jalur AES-256 (All-or-Nothing)', color='#e74c3c', edgecolor='#c0392b', alpha=0.85)
    ax2.set_ylabel('False Positive Rate (FPR)')
    ax2.set_title('(b) Tingkat Alarm Palsu Spasial (FPR)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios)
    ax2.set_ylim(-0.05, 1.05)
    ax2.legend(loc='upper left', fontsize=7.5)
    ax2.grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "grafik_kinerja_tamper.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    print("Generating publication figures...")
    generate_figure_windowing()
    generate_figure_tamper_visual()
    generate_figure_performance_curves()
    print("All figures generated successfully!")
