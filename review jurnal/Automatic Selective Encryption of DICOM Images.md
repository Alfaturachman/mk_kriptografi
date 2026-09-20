# Automatic Selective Encryption of DICOM Images

**Penulis:** Qamar Natsheh* (corresponding), Ana Salagean, Diwei Zhou* (corresponding), Eran Edirisinghe

**Institusi:**
- School of Computer Science, University of Birmingham, UK
- Department of Computer Science, Loughborough University, UK
- Department of Mathematical Sciences, Loughborough University, UK
- Vice-Chancellor's Office, Keele University, UK

**Jurnal:** Applied Sciences (MDPI), vol. 13, 4779, 2023

**DOI:** https://doi.org/10.3390/app13084779

**Status:** Diterima 20 Maret 2023, Direvisi 3 April 2023, Diterbitkan 11 April 2023

**Kata Kunci:** medical image encryption; selective encryption; region of interest; segmentation; LZ4 compression; multi-frame DICOM object

---

## Abstract

Securing DICOM images is essential to protect the privacy of patients, especially in the era of telemedicine. This paper introduces a selective encryption approach to reduce the processing time and sustain robustness of security. The proposed approach selects regions within medical images automatically using pixel thresholding segmentation, then compresses and encrypts them using different algorithms based on their importance. An adaptive two-region encryption approach is applied: ROB is encrypted using light encryption (XXTEA), while ROI is encrypted using sophisticated encryption (AES-256). For multi-frame DICOM: ~10,000x faster than naive encryption, 100x better compression ratio. For single-frame: 14-47% time savings.

---

## 1. Introduction

### Background
- PACS (Picture Archiving and Communication System) and DICOM standard are widely used in medical organizations
- DICOM standard lacks encryption for pixel data
- Encrypting large DICOM images using naive approach (e.g., 100,000 images) takes ~4 hours
- Selective encryption: encrypt important regions with AES, less important with lighter algorithms

### Related Work
- Selective encryption first proposed by Spanos & Maple (1995)
- Most approaches require manual segmentation (impractical)
- Frequency domain methods require additional computation
- Gap: no automatic spatial domain selective encryption using statistical properties

## 2. DICOM Image Encryption: Limitations

- No existing recommendations for securing DICOM pixel data
- Only anonymization (de-identification) of header data is recommended
- Processing time is bottleneck for real-world implementation
- Need: reduce encryption time while maintaining security

## 3. Proposed Approach

### General Framework
1. **Selection:** Segment pixel data into ROI and ROB based on intensity thresholding
2. **Compression:** LZ4 lossless compression on segmented regions
3. **Encryption:** AES-256 (ROI), XXTEA (ROB), AES-256 (header + segmentation map)

### Approach I: Multi-Region (Single-Frame Mammography)
- ROI divided into 3 regions (R1, R2, R3) based on pixel intensity distribution
- R1 (most informative) → AES-256
- R2 → AES-128
- R3 → XXTEA
- ROB → XXTEA
- Mathematical model (Linear System of Equations) guarantees shorter encryption time

### Approach II: Multi-Frame DICOM
- **Holistic-Based SE:** One segmentation map for all frames
- **Frame-Based SE:** Reference frame segmentation applied to all frames
- Adjacent frames have high redundancy → LZ4 compression very effective

## 4. Performance Analysis

### Cryptanalysis Metrics (Multi-Region)

| Metric | Value |
|--------|-------|
| CORR | -39.84 x 10^-3 |
| Entropy | 14.94 bits/pixel |
| NPCR | 100% |
| Chi-Square | 3.42 x 10^6 |
| PSNR | 3.78 dB |
| UACI | 4.00 x 10^5 |

### Time Performance
- Multi-region approach: **51-58% time savings** vs two-region approach
- Multi-region approach: **~60% time savings** vs naive AES encryption
- Multi-frame (Frame-Based SE): **~10,000x faster** than naive approach
- Compression ratio: 100x better with multi-region approach

### Segmentation Accuracy
- 100% accuracy based on LSE (Linear System of Equations)
- All manually selected area segmented as R1

## 5. Conclusions

- Selective encryption significantly reduces processing time while maintaining security
- Multi-region approach: automatically calculates optimal region sizes using mathematical model
- Frame-Based SE: exploits redundancy between adjacent frames
- Implementation in Python compiled to C using Cython for real platform deployment

---

## Referensi

1. NEMA. DICOM PS3.3 (2018). Fundamental Information Model.
2. DICOM Standards Committee. DICOM PS3.15 (2018). Security and System Management Profiles.
3. Kobayashi, L.O. et al. (2009). Proposal for DICOM multiframe medical image integrity and authenticity. J Digit Imaging, 22(1), 71-83.
4. Natsheh, Q. et al. (2018). Adaptive two-region encryption approach for DICOM medical images. IEEE.
