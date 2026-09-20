# Trigger-Based Fragile Model Watermarking for Image Transformation Networks

**Penulis:** Preston K. Robinette, Dung T. Nguyen, Samuel Sasaki, Taylor T. Johnson

**Institusi:** Computer Science, Vanderbilt University, USA

**Email:** preston.k.robinette, dung.t.nguyen, samuel.sasaki, Taylor.t.johnson@vanderbilt.edu

**Tahun:** 2024 | **Tipe:** Konferensi (IEEE)

**Kata Kunci:** Security, Watermarking, Information Hiding, Machine Learning

---

## Abstract

In fragile watermarking, a sensitive watermark is embedded in an object such that the watermark breaks upon tampering. We introduce a novel, trigger-based fragile model watermarking system for image transformation/generation networks that takes advantage of properties inherent to image outputs. Our approach effectively verifies the model's source and integrity across various datasets and attacks, outperforming baselines by 94%. This is the first work to consider fragile model watermarking for image transformation/generation networks.

---

## 1. Introduction

Verifying the source or integrity of a model is essential in maintaining trust and security in ML deployments — from critical infrastructure to healthcare and autonomous vehicles.

**Dua kategori model watermarking:**
- **Robust watermarking:** watermark tetap terdeteksi meskipun model dimodifikasi (copyright protection)
- **Fragile watermarking:** watermark rusak saat model dimodifikasi (integrity verification)

Trigger-based approach: menggunakan input trigger yang menghasilkan output spesifik untuk autentikasi.

## 2. Background and Related Works

### 2.1. Fragile Watermarking
Dua pendekatan:
1. **Parameter-based:** signature embedded pada weights/parameters (white-box access)
2. **Trigger-based:** input trigger → output spesifik (black-box compatible)

### 2.2. Fragile Watermarking Definition

Tiga kriteria watermarking yang berhasil:
1. **Fidelity:** watermark tidak degradasi performa model
2. **Retrievability:** watermark dapat diambil menggunakan trigger
3. **Fragility:** modifikasi model menyebabkan watermark rusak

## 3. Methodology

### 3.1. Immediate Tasks (Reconstruction)

Training:
```
L = MSE(x_c, x_c_hat) + α * MSE(w_f, x_wf_hat)
```

Verifikasi:
```
verified(f_tilde) = True if f_tilde(x_wf) ≈ w_f
fragile(f_tilde → f_dot) = True if f_dot(x_wf) ≉ w_f AND f_dot(x_c) ≈ x_c
```

### 3.2. Downstream Tasks (Semantic Segmentation)

```
L_S = CE(y_c, y_t) + CE(y_wf, w_f)
```

## 4. Experiments

### 4.1. Setup

**Datasets:** CIFAR-10, ImageNet, CLWD, RIM-ONE DL

**Models (7):** UNet, LinkNet, FPN, PSPNet, PAN, LRASPP, DeeplabV3

**Trigger Types:**
- Patch: kotak warna kecil di pojok kiri atas
- Block: kotak warna seukuran citra
- Noise: citra Gaussian noise random
- Steganography: citra dengan watermark tersembunyi (LSB)

**Metrics:**
- Fidelity: MSE/PSNR (reconstruction), IoU (segmentation)
- Retrievability: NCC > 0.95
- Fragility: NCC < 0.95 setelah attack

### 4.2. Results

| Model | Fidelity | Retrievability | Fragility (ftune1) | Fragility (ftune5) | Fragility (overwrite) |
|-------|----------|----------------|--------------------|--------------------|----------------------|
| UNet | Pass | 1.0000 | -0.0082 | 0.0064 | 0.0094 |
| LinkNet | Pass | 1.0000 | 0.0036 | 0.0256 | 0.0420 |
| FPN | Pass | 1.0000 | 0.0364 | 0.0137 | 0.0416 |
| PSPNet | Pass | 1.0000 | 0.0495 | 0.0554 | 0.0459 |
| PAN | Pass | 0.9998 | 0.0260 | 0.0395 | 0.0405 |
| LRASPP | Pass | 1.0000 | 0.5453 | 0.0333 | 0.0443 |
| DeeplabV3 | Pass | 1.0000 | -0.3035 | -0.1285 | 0.0444 |

**Baseline 1 & 2 (robust):** Fragility FAIL — watermark tetap ada setelah attack

### 4.3. Analysis

**Security of Trigger:**
- Semua fake trigger menghasilkan NCC rendah (0.0196 - 0.0607)
- Hanya trigger yang benar (purple patch, top-left) yang menghasilkan watermark

**Flexibility of Trigger:**
- Patch, block, noise, dan steganography semuanya berhasil
- Noise trigger menyebabkan gangguan paling kecil

**Ablation Alpha:**
- α = 0.0: watermark tidak terdeteksi (X)
- α ≥ 0.2: semua pass (fidelity + retrievability + fragility)

## 5. Conclusions

- Pertama kali fragile watermarking diterapkan pada image transformation/generation models
- Berhasil pada 7 model berbeda dengan 3 jenis attack
- Outperforms robust baselines dalam hal fragility (94%)
- Trigger-based approach cocok untuk black-box verification

---

## Referensi

1. Adi, Y. et al. (2018). Turning your weakness into a strength: Watermarking deep neural networks by backdooring. USENIX Security.
2. Zhu, R. et al. (2020). Protecting intellectual properties of deep neural networks with watermarking. arXiv.
3. Uchida, Y. et al. (2017). Embedding watermarks into deep neural networks. ACM IH&MMSec.
4. Zhang, J. et al. (2018). Protecting intellectual property of deep neural networks with watermarking. arXiv.
