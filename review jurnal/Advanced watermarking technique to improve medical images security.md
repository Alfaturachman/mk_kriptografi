# Advanced Watermarking Technique to Improve Medical Images' Security

**Penulis:** Media Anugerah Ayu* (corresponding), Teddy Mantoro, I Made Alan Priyatna

**Institusi:** Department of Computer Science, Faculty of Engineering and Technology, Sampoerna University, Jakarta, Indonesia

**Email:** media.ayu@sampoernauniversity.ac.id

**Tahun:** 2019 | **Copyright:** Universitas Ahmad Dahlan

**Kata Kunci:** DICOM, fragile watermarking, LSB, medical image, tamper detection

---

## Abstract

Advances in imaging technology have made medical images become one of the important sources for information in supporting accurate diagnoses and treatment decisions. However, the vulnerability of medical images' security is high. This study proposes to secure them by advancing the watermarking using dual-layer fragile technique. The dual-layer fragile watermarking will guarantee the integrity, authenticity, and confidentiality of patient's information and the pixel data of the medical images. The work implements two LSBs of image where the 1st LSB is as a tamper detector, and the 2nd LSB stores patient's information. Results show PSNR > 44 dB and SSIM almost 1, with tamper detector able to correctly detect and localize any tampering.

---

## 1. Introduction

Medical imaging technology (MRI, CT, X-ray, ultrasound) plays an essential role in diagnosing diseases. DICOM (Digital Imaging and Communications in Medicine) is the international standard for transferring, storing, and retrieving medical image information.

**Limitasi Keamanan DICOM:**
- Integrity dan authenticity tidak dijamin untuk seluruh DICOM Data Set
- Anonymized DICOM file tidak bisa digunakan untuk diagnosis lagi
- Tidak bisa melokalisasi piksel yang telah diubah

## 2. Digital Watermarking for Medical Images

Digital watermarking terbagi menjadi:
- **Robust watermark:** tahan terhadap signal processing, cocok untuk autentikasi
- **Fragile watermark:** tidak tahan terhadap signal processing, cocok untuk integritas

**LSB Modification:** mengubah least significant bit cover image dengan watermark bit. Embed pada 2 bit terakhir (1st dan 2nd LSB) tidak terdeteksi oleh mata manusia.

## 3. The Proposed Security Technique

### 3.1. Watermark Embedding Process

**Watermark Generation:**
1. Encrypt EPR menggunakan AES-256 (confidentiality + authenticity)
2. Hash DICOM tags menggunakan SHA-256 (integrity)
3. Concatenate HashDt + EncCt = Watermark 1 (ConDC)
4. Hitung hash SHA-256 dari blok 8x8 non-overlapped + id (row & column)

**Watermark Insertion:**
1. Embed ConDC ke 2nd LSB secara random menggunakan: f(x) = kx mod n + 1
2. Embed hash blok ke 1st LSB secara random

### 3.2. Watermark Extraction Process

1. Bagi citra menjadi blok 8x8 non-overlapped
2. Extract 1st LSB → bandingkan hash → deteksi manipulasi + lokalisasi
3. Extract 2nd LSB → dapatkan DICOM tags hash + encrypted EPR
4. Verifikasi DICOM tags → decrypt EPR

## 4. Methodology

### Dataset
| No | Nama | Modality | Size | Bit Depth | Color |
|----|------|----------|------|-----------|-------|
| 1 | BreastMRI | MRI | 256x256 | 16 | Monochrome |
| 2 | CervixMRI | MRI | 512x512 | 16 | Monochrome |
| 3 | BrainMRI | MRI | 256x256 | 16 | Monochrome |
| 4 | HeartCT | CT | 512x512 | 16 | Monochrome |
| 5 | BreastCT | CT | 512x512 | 16 | Monochrome |
| 6 | BrainCT | CT | 512x512 | 16 | Monochrome |

## 5. Hasil dan Pembahasan

### 5.1. Imperceptibility Analysis

| Medical Images | Standard PSNR | Standard SSIM | Proposed PSNR | Proposed SSIM |
|----------------|---------------|---------------|---------------|---------------|
| ct_brain | 44.92 dB | 0.9999 | 45.07 dB | 0.9999 |
| mr_brain | 44.75 dB | 0.9990 | 44.74 dB | 0.9990 |
| ct_breast | 44.73 dB | 0.9995 | 44.88 dB | 0.9996 |
| mr_breast | 44.46 dB | 0.9991 | 44.72 dB | 0.9995 |
| ct_heart | 44.15 dB | 0.9998 | 44.15 dB | 0.9998 |
| mr_cervix | 44.27 dB | 0.9994 | 44.34 dB | 0.9994 |

### 5.2. Fragility Analysis (Tamper Detection)

| Items | [27] | [26] | Proposed |
|-------|------|------|----------|
| Blind Watermarking | No | Yes | Yes |
| Image cropping | Yes | Yes | Yes |
| Copy-paste attack | Yes | Yes | Yes |
| Collage Attack | No | Yes | Yes |
| Constant-average attack | No | No | Yes |

### 5.3. Comparison with DICOM Standard

| Indicator | DICOM Standard | Standard WM | Proposed |
|-----------|---------------|-------------|----------|
| Confidentiality (header) | yes | yes | yes |
| Authenticity (header) | no | no | yes |
| Integrity (header) | no | no | yes |
| Authenticity (pixel) | yes | yes | yes |
| Integrity (pixel) | yes | yes | yes |

## 6. Conclusion

Dual-layer fragile watermarking berhasil memberikan:
- **Confidentiality** melalui AES-256 encryption pada EPR
- **Authenticity** melalui hash DICOM tags
- **Integrity** melalui tamper detection pada 1st LSB

PSNR > 44 dB dan SSIM ~0.99 menunjukkan watermark tidak terlihat oleh mata. Teknik ini lebih aman dibandingkan DICOM standard dan watermarking biasa.

---

## Referensi

1. DICOM PS3.15 (2018). Security and System Management Profiles. NEMA.
2. Al-Haj, A. (2014). Providing Integrity, Authenticity, and Confidentiality for Header and Pixel Data of DICOM Images. J Digit Imaging.
3. Pianykh, O.S. (2012). Digital Imaging and Communications in Medicine (DICOM). Springer.
4. Al-Haj, A. et al. (2016). Crypto-Watermarking of Transmitted Medical Images. J Digit Imaging, 30(1), 26-38.
5. Tan, C.K. et al. (2011). Security Protection of DICOM Medical Images Using Dual-Layer Reversible Watermarking. J Digit Imaging, 24(3), 528-540.
6. Wang, Z. et al. (2004). Image quality assessment: from error visibility to structural similarity. IEEE TIP, 13(4), 1-14.
