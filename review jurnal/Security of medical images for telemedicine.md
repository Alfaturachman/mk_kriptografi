# Security of Medical Images for Telemedicine: A Systematic Review

**Penulis:** Mahmoud Magdy, Khalid M. Hosny (iD), Neveen I. Ghali, Said Ghoniiemy

**Jurnal:** Multimedia Tools and Applications (Springer)

**Tahun:** 2022 | **Status:** Diterima 23 Desember 2021, Published 22 Maret 2022

**Kata Kunci:** Medical images, Watermarking, Steganography, Cryptography, Attacks, Copyright

---

## Abstract

Recently, there has been a rapid growth in the utilization of medical images in telemedicine applications. This survey paper summarizes existing medical data security approaches and the different challenges associated with them. An in-depth overview of security techniques — cryptography, steganography, and watermarking — is introduced with a full survey of recent research. The objective is to summarize and assess different algorithms based on PSNR, MSE, BER, and NC.

---

## 1. Introduction

Medical imaging (MRI, CT, X-rays, ultrasound) plays an essential role in diagnosing diseases. With telemedicine services (telesurgery, teleconsultation), medical images must be transmitted securely. If captured and tampered by attackers, it leads to false diagnosis.

**Keamanan citra medis dibutuhkan untuk:**
- Confidentiality: data tidak boleh diakses pihak tidak berwenang
- Integrity: data harus akurat
- Availability: data harus dapat diakses oleh pihak berwenang

**ROI vs RONI:**
- ROI (Region of Interest): area penting dengan informasi sensitif, tidak boleh diubah
- RONI (Region of No Interest): background, tidak mengandung informasi vital

## 2. Cryptography

### 2.1. Spatial Domain

**Chaotic-based:**
- Rajendran et al. (2019): chaotic map → key generation → confusion + diffusion
- Harshitha et al.: chaotic logistic map + linear feedback shift register

**DNA-based:**
- Banu et al.: IWT + DNA sequences + logistic map
- Guesmi et al.: SHA-2 + chaotic map + DNA masking

**Elliptic Curve:**
- Yin et al.: homomorphic encryption + elliptic curve
- ECCHC: ECC + Hill cipher

**Metaheuristics:**
- Genetic Algorithm, Bacterial Foraging Optimization, Differential Evolution untuk key optimization

**Cellular Automata:**
- Vijayakumar et al.: CA-based scheme untuk DICOM images

### 2.2. Transform Domain

- **Gyrator Transform:** Yatish et al. — phase-truncated Fourier transform
- **Fractional Fourier Transform:** FrDCT coefficients + chaotic map
- **DCT:** DCT + arithmetic encoding + chaotic sequence → PSNR 41.70 dB

## 3. Steganography

Steganography = "covered writing" — menyembunyikan data rahasia dalam media lain.

**Properties:**
1. Imperceptibility: watermark tidak terlihat
2. Security: data tidak terdeteksi oleh analisis statistik
3. Payload Capacity: kapasitas embedding maksimal
4. Robustness: ketahanan terhadap operasi citra

### Spatial Domain
- LSB, PVD (Pixel Value Differencing), histogram shifting
- Reversible data hiding untuk citra medis

### Transform Domain
- DWT, DCT, DFT, SVD
- Lebih robust terhadap serangan, tapi payload lebih rendah

### Adaptive Domain
- Menggunakan classifier untuk memilih lokasi embedding

## 4. Watermarking

Watermarking = menyematkan data tersembunyi dalam citra untuk autentikasi/kepemilikan.

**Klasifikasi:**
- **Robust:** tahan terhadap serangan (copyright protection)
- **Fragile:** sensitif terhadap modifikasi (tamper detection)

**Aplikasi pada citra medis:**
- Tamper detection dan localization
- Integrity verification
- Ownership proof

## 5. Metrik Evaluasi

| Metrik | Keterangan |
|--------|------------|
| PSNR | Peak Signal-to-Noise Ratio — kualitas citra |
| MSE | Mean Squared Error — distorsi |
| BER | Bit Error Rate — kesalahan bit |
| NC | Normalized Correlation — kemiripan watermark |
| SSIM | Structural Similarity Index |
| NPCR | Number of Pixel Change Rate |
| UACI | Unified Average Changing Intensity |

## 6. Serangan pada Citra Medis

| Kategori | Contoh Serangan |
|----------|----------------|
| Geometric | Scaling, rotation, cropping, shearing |
| Signal Processing | Histogram equalization, contrast adjustment, gamma correction |
| Noise | Salt & pepper, Gaussian noise |
| Filtering | Median, average, Sobel filter |
| Compression | JPEG compression |

## 7. Kesimpulan

- Kriptografi, steganografi, dan watermarking masing-masing memiliki kelebihan dan kekurangan
- Untuk citra medis: kombinasi teknik diperlukan untuk mencapai keamanan menyeluruh
- Fragile watermarking sangat penting untuk deteksi manipulasi
- Masih diperlukan penelitian untuk meningkatkan kapasitas embedding tanpa mengorbankan kualitas

---

## Referensi Utama

1. Bushberg, J.T. et al. (2011). The Essential Physics of Medical Imaging. Wolters Kluwer.
2. Pianykh, O.S. (2012). Digital Imaging and Communications in Medicine (DICOM). Springer.
3. Wang, Z. et al. (2004). Image quality assessment: from error visibility to structural similarity. IEEE TIP, 13(4), 1-14.
4. Al-Haj, A. (2014). Providing Integrity, Authenticity, and Confidentiality for Header and Pixel Data of DICOM Images. J Digit Imaging.
