# Signing and Verifying Encrypted Medical Images Using Double Random Phase Encryption

**Penulis:** Hanaa A. Abdallah, Dalia H. ElKamchouchi* (corresponding)

**Institusi:** Department of Information Technology, College of Computer and Information Sciences, Princess Nourah Bint Abdulrahman University, Riyadh, Saudi Arabia

**Jurnal:** Entropy (MDPI), vol. 24, 538, 2022

**DOI:** https://doi.org/10.3390/e24040538

**Status:** Diterima 10 April 2022, Published 12 April 2022

**Kata Kunci:** discrete wavelet transform; discrete cosine transform; double-random-phase encryption; digital signature; authentication; encryption

---

## Abstract

Digital Signature using Self-Image signing is introduced in this paper. This technique is used to verify the integrity and originality of images transmitted over insecure channels. The proposed approach uses the DWT to subdivide a picture into four bands and DCT to embed a mark from each sub-band to another sub-band. To increase security, the marked image is encrypted using Double Random Phase Encryption before transmission. By verifying the presence of the mark, the authority of the sender is verified.

---

## 1. Introduction

Information security protects integrity, confidentiality, and availability of data. Digital watermarking inserts information providing copyright protection. Electronic signatures from content data validate the identity of the signer, similar to digital signatures but with localization qualities.

## 2. Background Review

### 2.1. Discrete Wavelet Transform (DWT)
DWT decomposes images into four sub-bands: LL, HL, LH, HH using filtering approach (low pass + high pass filter + down sampling).

### 2.2. Discrete Cosine Transform (DCT)
DCT transforms spatial domain to frequency domain. Middle frequencies chosen for watermark embedding — avoids visually vital regions (low freq) and noise-exposed regions (high freq).

### 2.3. Double Random Phase Encryption (DRPE)
Proposed by Refregier and Javidi (1995). Encodes an image to stationary white noise using two independent random phase masks and Fourier transforms in a 4-f optical system.

**Enkripsi:**
```
g(x,y) = FT^-1{ FT{f(x,y) * θ(x,y)} * φ(u,v) }
```

**Dekripsi:**
```
f(x,y) = FT^-1{ FT{g(x,y) * e^(-i2πφ₀)} * e^(-i2πθ₀) }
```

## 3. Related Work

Berbagai pendekatan keamanan citra medis:
- Digital signature + DNA cryptography dengan biometric (fingerprint, iris)
- Homomorphic encryption + MAC untuk data integrity
- DWT-SVD domain watermarking dengan Chaotic-LZW compression
- Hybrid AES-RSA encryption + DWT steganography

## 4. Proposed Scheme

### 4.1. Signing Process
1. Compute 2D-DWT → 4 sub-bands (LL, HL, LH, HH)
2. Bagi sub-bands menjadi blok 8x8, lakukan DCT
3. Permutation: substitusi koefisien DCT antar sub-bands
4. IDCT + 2D-IDWT
5. Enkripsi menggunakan DRPE

### 4.2. Verification Process
1. Dekripsi DRPE → marked image
2. 2D-DWT → 4 sub-bands → DCT per blok
3. Extract embedded rows/columns → bandingkan melalui correlation analysis

## 5. Hasil

### 5.1. Performance Metrics

| Metrik | Hasil |
|--------|-------|
| PSNR (Original vs Marked) | 35.99 dB |
| SSIM (Original vs Marked) | 0.97 |
| PSNR (Marked vs Encrypted) | 12.17 dB (Chaotic) / 12.84 dB (DRPE) |
| SSIM (Marked vs Encrypted) | 0.1035 (Chaotic) / 0.0349 (DRPE) |
| Mean Correlation (Original vs Encrypted) | 0.9 |

### 5.2. AWGN Noise Resistance

| SNR (dB) | Mean Correlation |
|----------|-----------------|
| 5 | 0.0737 |
| 10 | 0.1600 |
| 20 | 0.3597 |
| 30 | 0.5407 |
| 50 | 0.7592 |

### 5.3. Comparative Analysis

| Gaussian Noise | Proposed | [24] | [25] | [26] |
|----------------|----------|------|------|------|
| 0.5 | 0.75 | 0.63 | 0.58 | 0.28 |

Proposed technique lebih robust dibandingkan DWT, SVD, DWT-SVD, dan DT-CWT-SVD.

## 6. Conclusions

- Digital signature + DRPE mampu memverifikasi keaslian citra medis
- Korelasi recovered mark dengan original mendekati 1
- Tahan terhadap AWGN noise pada berbagai level SNR
- PSNR 35.99 dB menunjukkan marking tidak mempengaruhi kualitas citra

---

## Referensi

1. Parah, S.A. et al. (2017). Information hiding in medical images. Multimed Tools Appl, 76, 10599-10633.
2. Kumar, C. et al. (2018). A recent survey on image watermarking techniques. Multimed Tools Appl, 77, 3597-3622.
3. Refregier, P. & Javidi, B. (1995). Optical image encryption based on input plane and Fourier plane random encoding. Opt Lett, 20, 767-769.
4. Wang, Z. et al. (2004). Image quality assessment: from error visibility to structural similarity. IEEE TIP, 13(4), 600-612.
5. Abdallah, H.A. & Alsodairi, S. (2020). A Novel Watermarking Technique Based on Hybrid Transforms. IJCNIS, 12, 316-325.
