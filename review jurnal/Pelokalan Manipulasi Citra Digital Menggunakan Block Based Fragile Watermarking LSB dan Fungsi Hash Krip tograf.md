# Pelokalan Manipulasi Citra Digital Menggunakan Block-Based Fragile Watermarking LSB dan Fungsi Hash Kriptografi

**Penulis:** Raihan Budi Waluyo, Ermadi Satria Wijaya (corresponding), Sigit Sugiyanto, Harjono

**Institusi:** Program Studi Teknik Informatika, Universitas Muhammadiyah Purwokerto, Indonesia

**Jurnal:** Jurnal Teknologi Informasi dan Multimedia, vol. 8, no. 4, pp. 817-829, 2026

**Status:** SINTA 4 | Diterima 29-07-2026, Direvisi 05-08-2026, Diterbitkan 02-09-2026

**Kata Kunci:** fragile watermarking; hash MD5; pelokalan manipulasi; forensik citra; autentikasi citra digital

---

## Abstrak

Penelitian ini mengusulkan skema fragile watermarking berbasis matriks blok 2x2 piksel non-overlapping, diintegrasikan dengan fungsi hash kriptografi MD5 untuk mencapai pelokalan manipulasi citra digital secara presisi. Penyisipan watermark dibatasi pada ruang 1-bit LSB, sementara 7-bit MSB diproses menggunakan MD5, dipotong menjadi 4-bit, dan disisipkan melalui operasi OR. Hasil menunjukkan PSNR rata-rata 51.09 dB, SSIM 0.9977, dan akurasi deteksi 93.51%.

---

## 1. Pendahuluan

Kemudahan akses terhadap perangkat lunak penyuntingan citra telah menjadikan pemalsuan citra digital sebagai persoalan yang semakin mengkhawatirkan, khususnya pada bidang forensik, dokumen legal, dan pencitraan medis. Penelitian ini mengusulkan skema fragile watermarking berbasis blok mikro 2x2 piksel dengan fungsi hash MD5.

**Rumusan Masalah:**
1. Sejauh mana penurunan ukuran blok menjadi 2x2 piksel meningkatkan presisi deteksi manipulasi?
2. Sejauh mana penyisipan hash MD5 pada 1-bit LSB mampu mempertahankan kualitas visual sekaligus sensitif terhadap manipulasi?

## 2. Bahan dan Metode

### 2.1. Pengumpulan Data
Dataset: CoMoFoD (Copy-Move Forgery Detection) — 30 sampel citra RGB 24-bit, berformat 512x512. Setiap sampel terdiri dari: citra asli (_O), citra termanipulasi (_F), dan citra masker biner (_B).

### 2.2. Pra-Pemrosesan
Citra RGB dikonversi ke grayscale 8-bit menggunakan rumus luminositas ITU-R BT.601:
```
Y = 0.299*R + 0.587*G + 0.114*B
```

### 2.3. Penyisipan Watermark
1. Bagi citra menjadi blok 2x2 piksel non-overlapping
2. Kosongkan 1-bit LSB pada setiap piksel (AND dengan 0xFE)
3. Gabungkan 7-bit MSB dari 4 piksel → hash MD5 → truncate ke 4-bit
4. Sisipkan 4-bit hash ke LSB menggunakan operasi OR

### 2.4. Simulasi Serangan
Manipulasi spasial dikontrol menggunakan citra masker biner sebagai acuan. Piksel target ditimpa menggunakan nilai dari citra termanipulasi.

### 2.5. Ekstraksi dan Pelokalan (Blind Extraction)
1. Buat Detection Map (matriks kosong)
2. Ekstrak "Hash Tersimpan" (4-bit dari LSB) pada setiap blok 2x2
3. Hitung "Hash Baru" (4-bit MD5 dari 7-bit MSB)
4. Jika Hash Tersimpan != Hash Baru → piksel putih (255) pada Detection Map

### 2.6. Metrik Evaluasi
- **PSNR:** kualitas visual citra ber-watermark
- **SSIM:** kemiripan struktural
- **Akurasi = (Piksel Terdeteksi Benar / Total Piksel Termanipulasi) x 100%**

## 3. Hasil

| No | Citra | PSNR (dB) | SSIM | Akurasi (%) |
|----|-------|-----------|------|-------------|
| 1 | 001 | 51.09 | 0.9978 | 90.48 |
| 2 | 002 | 51.16 | 0.9967 | 93.19 |
| 3 | 003 | 50.78 | 0.9974 | 96.85 |
| 4 | 004 | 51.14 | 0.9950 | 92.72 |
| 5 | 005 | 51.13 | 0.9950 | 93.66 |
| ... | ... | ... | ... | ... |
| **Rata-rata** | | **51.09** | **0.9977** | **93.51** |

## 4. Pembahasan

- PSNR 51.09 dB (jauh di atas ambang 40 dB) → modifikasi tingkat mikro hanya menyebabkan deviasi intensitas maksimal ±1
- SSIM 0.9977 → struktur spasial hampir identik dengan citra asli
- Akurasi 93.51 → blok mikro 2x2 memberikan presisi pelokalan yang sangat tinggi
- Dibandingkan skema berbasis blok besar [8] dan hash MD5/SHA-256 sebelumnya [11,12], pendekatan ini lebih presisi dalam pemetaan batas tepi manipulasi

## 5. Kesimpulan

Skema fragile watermarking berbasis blok mikro 2x2 dengan MD5 berhasil menyeimbangkan ketidaktampakan visual (PSNR > 50 dB) dengan sensitivitas pelokalan manipulasi (akurasi 93.51%). Direkomendasikan ekspansi ke citra RGB dan penerapan lightweight cryptography untuk real-time scanning.

---

## Daftar Pustaka

1. Toyib, R. et al. (2021). Implementasi template matching dalam mendeteksi keaslian foto. JTIS, 3(3), 32-40.
2. Umar, R. et al. (2019). Analisis forensik untuk mendeteksi pemalsuan video. J-SAKTI, 3(2), 193-200.
3. Faroek, D.A. & Umar, R. (2020). Deteksi keaslian citra menggunakan ELA dan PCA. Jurnal Ilmiah Teknik Informatika, 8(2), 132-139.
4. Isnaini, K.N. et al. (2020). Analisis forensik mendeteksi keaslian citra digital menggunakan metode NIST. J. Resist., 3, 72-81.
5. Fauzan, A. (2023). Analisis digital forensik pada kasus pemalsuan dokumen menggunakan metode NIST. Skripsi, Universitas Amikom Purwokerto.
6. Wijaya, A.Y. (2017). Pengembangan metode block matching untuk deteksi copy-move. JU-TI, 15(1), 84-94.
7. Zulfan et al. (2016). Deteksi pemalsuan citra copy-move menggunakan ordinal measure DCT. JNT, 5(2), 165-174.
8. Lumbanraja, P. (2019). Watermarking pada citra digital menggunakan kombinasi pixel value indicator dan MSB. METHODIKA, 5(1), 34-41.
9. Pambudi, A.R. et al. (2020). Deteksi keaslian uang kertas berdasarkan watermark. JIP, 6(4), 69-74.
10. Masykuroh, K. (2021). Analisis watermarking pada citra RGB dengan DCT dan DWT. TELKA, 7(1), 62-70.
11. Habiburrahman, H. (2025). MD5 di era post-kriptografi. JIIPK, 14(1), 9-18.
12. Saputra, I. & Nasution, S.D. (2019). Analisa SHA-256 untuk orisinalitas citra digital. SENARIS, 1, 164-178.
13. Rakhmawati, L. et al. (2019). A recent survey of self-embedding fragile watermarking. EURASIP JIVP, 2019(61).
14. Lin, C. et al. (2023). Fragile watermarking for tamper localization and self-recovery based on AMBTC and VQ. Electronics, 12(2), 415.
15. Su, G.D. et al. (2020). Effective self-recovery and tampering localization fragile watermarking for medical images. IEEE Access, 8.
16. Bisri, H. & Marzuki, M.I. (2023). Forensik citra digital menggunakan ELA, clone detection dan EXIF. G-Tech, 7(2), 586-595.
17. Tralic, D. et al. (2013). CoMoFoD — new database for copy-move forgery detection. ELMAR-2013, 49-54.
