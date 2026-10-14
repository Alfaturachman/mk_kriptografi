"""Modul pembangkit histogram visual untuk antarmuka web CitraMedis.

Menghasilkan diagram visual resolusi tinggi (PNG bytes) untuk:
1. Histogram Citra Asli
2. Histogram Citra Hasil Enkripsi / Watermark (PEE-HS)
3. Histogram Citra Hasil Dekripsi / Pemulihan Reversibel
4. Histogram Keseragaman Ciphertext AES-256 (Byte 0-255)
5. Diagram Komparasi Tumpang Tindih (Overlay Comparison)
"""

import io
import math
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def shannon_entropy(arr: np.ndarray) -> float:
    """Menghitung Entropi Informasi Shannon (bit)."""
    flat = np.asarray(arr).ravel()
    vals, counts = np.unique(flat, return_counts=True)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log2(probs)))


def shannon_entropy_bytes(data: bytes) -> float:
    """Menghitung Entropi Shannon untuk rangkaian byte (bit/byte)."""
    arr = np.frombuffer(data, dtype=np.uint8)
    return shannon_entropy(arr)


def render_histogram_image(
    data: np.ndarray,
    title: str,
    color: str = "#0f766e",
    edge_color: str = "#0b5d56",
    xlabel: str = "Intensitas Piksel (0–255)",
    ylabel: str = "Jumlah Piksel",
    bins: int = 64,
    range_val: tuple = (0, 255),
    subtitle_stats: bool = True,
) -> bytes:
    """Merender histogram piksel tunggal menjadi bytes PNG."""
    flat = np.asarray(data).ravel()
    ent = shannon_entropy(flat)
    mean_val = float(np.mean(flat))
    std_val = float(np.std(flat))

    fig, ax = plt.subplots(figsize=(4.4, 3.0), dpi=115)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    counts, bin_edges, _ = ax.hist(
        flat,
        bins=bins,
        range=range_val,
        color=color,
        edgecolor=edge_color,
        linewidth=0.5,
        alpha=0.88,
    )

    ax.set_title(title, fontsize=10.5, fontweight="bold", color="#0f172a", pad=10)
    ax.set_xlabel(xlabel, fontsize=8.5, color="#475569", labelpad=4)
    ax.set_ylabel(ylabel, fontsize=8.5, color="#475569", labelpad=4)
    ax.tick_params(colors="#64748b", labelsize=8)

    for spine in ax.spines.values():
        spine.set_color("#cbd5e1")
        spine.set_linewidth(0.8)

    ax.grid(True, linestyle="--", alpha=0.45, color="#cbd5e1")

    if subtitle_stats:
        stats_str = f"μ: {mean_val:.1f}  |  σ: {std_val:.1f}  |  H: {ent:.3f} bit"
        ax.text(
            0.96,
            0.92,
            stats_str,
            transform=ax.transAxes,
            fontsize=7.8,
            color="#334155",
            fontweight="medium",
            ha="right",
            va="top",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor="#cbd5e1", alpha=0.9),
        )

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return buf.getvalue()


def render_comparison_histogram(
    orig_data: np.ndarray,
    enc_data: np.ndarray,
    dec_data: np.ndarray = None,
    bins: int = 64,
    range_val: tuple = (0, 255),
) -> bytes:
    """Merender komparasi histogram Asli vs Hasil Enkripsi vs Hasil Dekripsi."""
    fig, ax = plt.subplots(figsize=(6.2, 3.2), dpi=115)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    flat_orig = np.asarray(orig_data).ravel()
    flat_enc = np.asarray(enc_data).ravel()

    # Step histogram for clear overlapping view
    ax.hist(
        flat_orig,
        bins=bins,
        range=range_val,
        histtype="step",
        linewidth=2.0,
        color="#0284c7",
        label="Asli (Original)",
    )
    ax.hist(
        flat_enc,
        bins=bins,
        range=range_val,
        histtype="step",
        linewidth=1.8,
        linestyle="--",
        color="#d97706",
        label="Hasil Enkripsi / Watermark",
    )

    if dec_data is not None:
        flat_dec = np.asarray(dec_data).ravel()
        ax.hist(
            flat_dec,
            bins=bins,
            range=range_val,
            histtype="step",
            linewidth=1.4,
            linestyle=":",
            color="#10b981",
            label="Hasil Dekripsi (Recovery 100%)",
        )

    ax.set_title(
        "Perbandingan Distribusi Intensitas: Asli vs Enkripsi vs Dekripsi",
        fontsize=10.5,
        fontweight="bold",
        color="#0f172a",
        pad=10,
    )
    ax.set_xlabel("Intensitas Piksel (0–255)", fontsize=8.5, color="#475569")
    ax.set_ylabel("Jumlah Piksel", fontsize=8.5, color="#475569")
    ax.tick_params(colors="#64748b", labelsize=8)

    for spine in ax.spines.values():
        spine.set_color("#cbd5e1")
        spine.set_linewidth(0.8)

    ax.grid(True, linestyle="--", alpha=0.45, color="#cbd5e1")
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9, edgecolor="#cbd5e1")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return buf.getvalue()


def render_ciphertext_histogram(cipher_bytes: bytes) -> bytes:
    """Merender histogram distribusi byte AES-256 (0-255)."""
    arr = np.frombuffer(cipher_bytes, dtype=np.uint8)
    ent = shannon_entropy(arr)
    n = len(arr)
    expected = n / 256.0

    counts = np.bincount(arr, minlength=256)
    chi2 = float(np.sum(((counts - expected) ** 2) / expected))

    fig, ax = plt.subplots(figsize=(4.4, 3.0), dpi=115)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    ax.bar(
        np.arange(256),
        counts,
        width=1.0,
        color="#6366f1",
        edgecolor="none",
        alpha=0.85,
    )
    ax.axhline(
        expected,
        color="#ef4444",
        linestyle="--",
        linewidth=1.2,
        label=f"Ideal Acak ({expected:.1f})",
    )

    ax.set_title("Histogram Ciphertext AES-256", fontsize=10.5, fontweight="bold", color="#0f172a", pad=10)
    ax.set_xlabel("Nilai Byte Sandi (0–255)", fontsize=8.5, color="#475569", labelpad=4)
    ax.set_ylabel("Frekuensi", fontsize=8.5, color="#475569", labelpad=4)
    ax.set_xlim(0, 255)
    ax.tick_params(colors="#64748b", labelsize=8)

    for spine in ax.spines.values():
        spine.set_color("#cbd5e1")
        spine.set_linewidth(0.8)

    ax.grid(True, linestyle="--", alpha=0.45, color="#cbd5e1")

    stats_str = f"H: {ent:.3f} bit/B  |  χ²: {chi2:.1f}"
    ax.text(
        0.96,
        0.92,
        stats_str,
        transform=ax.transAxes,
        fontsize=7.8,
        color="#334155",
        fontweight="medium",
        ha="right",
        va="top",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor="#cbd5e1", alpha=0.9),
    )

    ax.legend(loc="lower right", fontsize=7.5, framealpha=0.9, edgecolor="#cbd5e1")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return buf.getvalue()
