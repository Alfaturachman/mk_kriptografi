# Daftar Pustaka Jurnal - Literature Review

Topik penelitian: **Proteksi Ganda Citra Medis** (Enkripsi AES + Fragile Watermarking untuk Deteksi Manipulasi)

> Total literatur terkumpul: **7 sumber**
> - 5 jurnal internasional (layak sitasi)
> - 1 makalah mahasiswa (referensi tambahan)
> - 1 jurnal SINTA 4 (referensi tambahan)

---

## Ringkasan Literatur

| No | Judul | Penulis | Sumber / Penerbit | Tahun | Tipe | Status Sitasi |
|----|-------|---------|-------------------|-------|------|---------------|
| 1 | Penerapan Enkripsi dan Tanda Tangan Digital untuk Keamanan dan Integritas Citra Medis | Aloysius Arya Wibisono | Makalah Kuliah (ITB) | 2024 | Makalah | Referensi tambahan |
| 2 | Pelokalan Manipulasi Citra Digital Menggunakan Block-Based Fragile Watermarking LSB dan Fungsi Hash Kriptografi | Raihan Budi Waluyo, Ermadi Satria Wijaya, Sigit Sugiyanto, Harjono | Jurnal Teknologi Informasi dan Multimedia, vol. 8, no. 4, pp. 817-829 | 2026 | Jurnal SINTA 4 | Referensi tambahan |
| 3 | Advanced Watermarking Technique to Improve Medical Images' Security | Media Anugerah Ayu, Teddy Mantoro, I Made Alan Priyatna | International Journal (Sampoerna University) | 2019 | Jurnal Internasional | Layak sitasi |
| 4 | Automatic Selective Encryption of DICOM Images | Qamar Natsheh, Ana Salagean, Diwei Zhou, Eran Edirisinghe | Applied Sciences (MDPI), vol. 13, 4779 | 2023 | Jurnal Internasional (Q2) | Layak sitasi |
| 5 | Security of Medical Images for Telemedicine: A Systematic Review | Mahmoud Magdy, Khalid M. Hosny, Neveen I. Ghali, Said Ghoniiemy | Springer (Multimedia Tools and Applications) | 2022 | Jurnal Internasional (Q1) | Layak sitasi |
| 6 | Signing and Verifying Encrypted Medical Images Using Double Random Phase Encryption | Hanaa A. Abdallah, Dalia H. ElKamchouchi | Entropy (MDPI), vol. 24, 538 | 2022 | Jurnal Internasional (Q2) | Layak sitasi |
| 7 | Trigger-Based Fragile Model Watermarking for Image Transformation Networks | Preston K. Robinette, Dung T. Nguyen, Samuel Sasaki, Taylor T. Johnson | Konferensi IEEE (Vanderbilt University) | 2024 | Konferensi | Layak sitasi |

---

## Detail Setiap Literatur

### 1. Penerapan Enkripsi dan Tanda Tangan Digital untuk Keamanan dan Integritas Citra Medis

- **Penulis:** Aloysius Arya Wibisono (NIM 18329925)
- **Institusi:** Program Studi Teknik Biomedis, Sekolah Teknik Elektro dan Informatika, Institut Teknologi Bandung
- **Tipe:** Makalah kuliah
- **Tahun:** 2024
- **Topik Utama:** Implementasi enkripsi AES pada file DICOM untuk keamanan data medis
- **Metode:** AES-256 ECB, analisis histogram, PSNR, NPCR
- **Hasil Utama:** NPCR ~99.61%, PSNR terenkripsi ~27.8-27.9 dB, dekripsi sempurna (NPCR 0%, PSNR inf)
- **Relevansi:** Membahas enkripsi AES pada citra medis DICOM, analisis PSNR dan NPCR sebagai metrik evaluasi
- **Catatan:** Makalah mahasiswa, bukan jurnal terakreditasi. Cocok sebagai referensi tambahan untuk background AES dan DICOM
- **Kata Kunci:** AES, DICOM, Medical Data, PSNR, NPCR, Histogram

---

### 2. Pelokalan Manipulasi Citra Digital Menggunakan Block-Based Fragile Watermarking LSB dan Fungsi Hash Kriptografi

- **Penulis:** Raihan Budi Waluyo, Ermadi Satria Wijaya (corresponding), Sigit Sugiyanto, Harjono
- **Institusi:** Program Studi Teknik Informatika, Universitas Muhammadiyah Purwokerto
- **Jurnal:** Jurnal Teknologi Informasi dan Multimedia, vol. 8, no. 4, pp. 817-829
- **Tahun:** 2026
- **SINTA:** SINTA 4
- **Topik Utama:** Fragile watermarking berbasis blok mikro 2x2 piksel dengan hash MD5 untuk pelokalan manipulasi
- **Metode:** Watermarking LSB 1-bit, MD5 hash pada 7-bit MSB, deteksi buta (blind extraction)
- **Hasil Utama:** PSNR rata-rata 51.09 dB, SSIM 0.9977, akurasi deteksi 93.51%
- **Dataset:** CoMoFoD (30 sampel)
- **Relevansi:** Sangat relevan — fragile watermarking LSB + hash kriptografi untuk deteksi manipulasi citra, hampir identik dengan topik penelitian
- **Catatan:** Jurnal SINTA 4, tidak bisa menjadi sitasi jurnal utama, tapi sangat berguna sebagai referensi metodologi
- **Kata Kunci:** fragile watermarking, hash MD5, pelokalan manipulasi, forensik citra, autentikasi citra digital

---

### 3. Advanced Watermarking Technique to Improve Medical Images' Security

- **Penulis:** Media Anugerah Ayu (corresponding), Teddy Mantoro, I Made Alan Priyatna
- **Institusi:** Department of Computer Science, Sampoerna University, Jakarta, Indonesia
- **Tahun:** 2019
- **Topik Utama:** Dual-layer fragile watermarking untuk keamanan citra medis DICOM
- **Metode:** Dual-layer LSB (1st LSB sebagai tamper detector, 2nd LSB menyimpan EPR + hash DICOM tags), AES-256 untuk enkripsi EPR, SHA-256 untuk hash
- **Hasil Utama:** PSNR > 44 dB, SSIM ~0.99, mendeteksi cropping, copy-paste, collage, dan constant-average attack
- **Dataset:** Citra CT dan MRI (6 citra: breast MRI, cervix MRI, brain MRI, heart CT, breast CT, brain CT)
- **Relevansi:** SANGAT relevan — menggabungkan enkripsi AES + fragile watermarking LSB pada citra medis DICOM, kontribusi integrity + confidentiality + authenticity
- **Metrik:** PSNR, SSIM, MSE, Tampered Detection Rate (TDR)
- **Kata Kunci:** DICOM, fragile watermarking, LSB, medical image, tamper detection

---

### 4. Automatic Selective Encryption of DICOM Images

- **Penulis:** Qamar Natsheh, Ana Salagean, Diwei Zhou, Eran Edirisinghe
- **Institusi:** University of Birmingham, Loughborough University, Keele University (UK)
- **Jurnal:** Applied Sciences (MDPI), vol. 13, 4779
- **Tahun:** 2023
- **DOI:** https://doi.org/10.3390/app13084779
- **Topik Utama:** Selective encryption untuk mengurangi waktu proses enkripsi DICOM
- **Metode:** Pixel thresholding untuk segmentasi ROI/ROB, LZ4 compression, AES-256 (ROI), XXTEA (ROB), multi-region & multi-frame approach
- **Hasil Utama:** Multi-frame: 10,000x lebih cepat dari naive encryption; Single-frame: hemat 14-47% waktu; Metrik kriptanalis: CORR rendah, entropy tinggi, NPCR 100%
- **Dataset:** CBIS-DDSM Mammography (60 studi)
- **Relevansi:** Relevan — membahas enkripsi selektif pada citra medis DICOM, penggunaan AES, metrik kriptanalis
- **Kata Kunci:** medical image encryption, selective encryption, region of interest, segmentation, LZ4 compression, multi-frame DICOM

---

### 5. Security of Medical Images for Telemedicine: A Systematic Review

- **Penulis:** Mahmoud Magdy, Khalid M. Hosny, Neveen I. Ghali, Said Ghoniiemy
- **Jurnal:** Multimedia Tools and Applications (Springer)
- **Tahun:** 2022
- **Topik Utama:** Systematic review keamanan citra medis — kriptografi, steganografi, dan watermarking
- **Cakupan:** 200+ referensi, membahas chaotic-based encryption, DNA-based encryption, DWT, DCT, LSB, fragile vs robust watermarking, berbagai serangan (geometric, signal processing, noise)
- **Metrik yang dibahas:** PSNR, MSE, BER, NC, SSIM
- **Relevansi:** SANGAT relevan sebagai tinjauan pustaka komprehensif — mencakup seluruh domain keamanan citra medis
- **Kata Kunci:** Medical images, Watermarking, Steganography, Cryptography, Attacks, Copyright

---

### 6. Signing and Verifying Encrypted Medical Images Using Double Random Phase Encryption

- **Penulis:** Hanaa A. Abdallah, Dalia H. ElKamchouchi (corresponding)
- **Institusi:** Princess Nourah Bint Abdulrahman University, Riyadh, Saudi Arabia
- **Jurnal:** Entropy (MDPI), vol. 24, 538
- **Tahun:** 2022
- **DOI:** https://doi.org/10.3390/e24040538
- **Topik Utama:** Digital signature pada citra medis menggunakan DWT + DCT + Double Random Phase Encryption (DRPE)
- **Metode:** 2D-DWT → DCT pada sub-bands → embedding signature antar sub-bands → DRPE encryption
- **Hasil Utama:** PSNR citra bertanda ~35.99 dB, SSIM 0.97, korelasi blok tertinggi 0.75 pada AWGN 50dB, tahan serangan AWGN
- **Metrik:** PSNR, SSIM, Correlation Coefficient
- **Relevansi:** Relevan — membahas digital signature + enkripsi pada citra medis, verifikasi integritas
- **Kata Kunci:** discrete wavelet transform, discrete cosine transform, double-random-phase encryption, digital signature, authentication, encryption

---

### 7. Trigger-Based Fragile Model Watermarking for Image Transformation Networks

- **Penulis:** Preston K. Robinette, Dung T. Nguyen, Samuel Sasaki, Taylor T. Johnson
- **Institusi:** Vanderbilt University, USA
- **Tahun:** 2024
- **Tipe:** Konferensi (IEEE)
- **Topik Utama:** Fragile watermarking pada model machine learning (image transformation/generation) menggunakan trigger-based approach
- **Metode:** Trigger input → watermark output, MSE loss untuk fidelity + watermarking, NCC untuk evaluasi
- **Hasil Utama:** Keberhasilan pada 7 model (UNet, LinkNet, FPN, PSPNet, PAN, LRASPP, DeeplabV3), outperform baseline 94%, fragility terbukti setelah fine-tuning dan overwrite attack
- **Dataset:** CIFAR-10, ImageNet, CLWD, RIM-ONE DL
- **Relevansi:** Relevan sebagai referensi konsep fragile watermarking dan trigger-based approach, meskipun untuk domain ML model
- **Kata Kunci:** Security, Watermarking, Information Hiding, Machine Learning

---

### Analisis Jurnal

#### Gap Penelitian (Research Gap)

**1. Belum ada kombinasi enkripsi AES + fragile watermarking LSB + hash dalam satu framework terintegrasi**

Jurnal [3] sudah menggabungkan AES + dual-layer LSB, namun tidak menggunakan hash kriptografi untuk verifikasi integritas secara terpisah. Jurnal [2] menggunakan hash MD5 + LSB, namun tanpa enkripsi AES. Belum ada yang menggabungkan ketiganya dalam satu pipeline. (Jurnal terkait: [2], [3])

**2. Evaluasi terhadap serangan spesifik citra medis masih terbatas**

Sebagian besar jurnal menguji serangan umum (noise, cropping), namun belum ada evaluasi terhadap serangan spesifik seperti penyisipan objek asing (object insertion), penggantian region medis (region replacement), atau deepfake medis. (Jurnal terkait: [2], [3], [6])

**3. Keterbatasan ukuran dataset pada penelitian fragile watermarking citra medis**

Jurnal [2] hanya menggunakan 30 sampel (CoMoFoD), jurnal [3] hanya 6 citra. Belum ada penelitian dengan dataset citra medis yang besar (>1000 citra) untuk membuktikan robustness metode. (Jurnal terkait: [2], [3])

**4. Belum ada metrik keamanan yang komprehensif**

Sebagian besar jurnal hanya melaporkan PSNR, SSIM, dan NPCR. Belum ada yang melaporkan metrik seperti Bit Error Rate (BER), Key Sensitivity Analysis, atau Uji Chi-Square secara lengkap dalam satu penelitian. (Jurnal terkait: [1], [2], [3], [4])

**5. Performa waktu proses pada citra medis berukuran besar belum dievaluasi**

Citra DICOM asli berukuran 512×512 hingga 2048×2048 dengan kedalaman warna 12-16 bit. Belum ada jurnal yang mengevaluasi waktu eksekusi real-time pada spesifikasi hardware standar. (Jurnal terkait: [3], [4])

---

#### Perbandingan dengan Penelitian Terdahulu

**1. Kombinasi Enkripsi + Watermarking**

- **Penelitian terdahulu [3] (2019):** Dual-layer LSB + AES-256 tanpa hash
- **Posisi penelitian ini:** Pipeline AES + Fragile LSB + Hash kriptografi
- **Hubungan: Ekstensi** — menambahkan hash sebagai lapisan verifikasi ketiga

**2. Deteksi Pelokalan Manipulasi**

- **Penelitian terdahulu [2] (2026):** LSB + MD5 pada blok 2×2 piksel
- **Posisi penelitian ini:** Deteksi manipulasi pada blok berukuran lebih besar
- **Hubungan: Kontras** — ukuran blok berbeda, akurasi deteksi [2] mencapai 93.51%

**3. Selective Encryption**

- **Penelitian terdahulu [4] (2023):** ROI/ROB thresholding + AES/XXTEA
- **Posisi penelitian ini:** Enkripsi penuh pada seluruh citra
- **Hubungan: Kontras** — selective lebih efisien, full encryption lebih aman

**4. Sertifikasi Digital pada Citra Medis**

- **Penelitian terdahulu [6] (2022):** DWT + DCT + DRPE
- **Posisi penelitian ini:** Menggunakan AES (standar industri)
- **Hubungan: Kontras** — DRPE akademis, AES lebih praktis diimplementasikan

**5. Fragile Watermarking untuk ML**

- **Penelitian terdahulu [7] (2024):** Trigger-based pada model ML
- **Posisi penelitian ini:** Fragile watermarking pada citra medis langsung
- **Hubungan: Paralel** — konsep serupa, domain berbeda (ML vs. citra medis)

**6. Tinjauan Sistematis Keamanan Citra Medis**

- **Penelitian terdahulu [5] (2022):** Review 200+ literatur
- **Posisi penelitian ini:** Studi kasus spesifik
- **Hubungan: Spesialisasi** — mengisi gap yang diidentifikasi dalam review [5]

**7. Kontras dengan Pendekatan yang Ada**

- **Dual-layer LSB [3]:** Kelebihannya efisien dalam penyimpanan watermark, kelemahannya tanpa hash sehingga tidak bisa membedakan jenis serangan. Penelitian ini menambahkan hash kriptografi untuk verifikasi.
- **LSB + MD5 [2]:** Kelebihannya akurasi deteksi tinggi (93.51%), kelemahannya tanpa enkripsi sehingga tidak ada confidentiality. Penelitian ini menambahkan AES encryption.
- **Selective Encryption [4]:** Kelebihannya hemat waktu proses (14-47%), kelemahannya tidak ada watermarking untuk integritas. Penelitian ini menambahkan watermarking untuk integrity check.
- **DRPE + DWT/DCT [6]:** Kelebihannya keamanan matematika tinggi, kelemahannya kompleks implementasi dan tidak praktis. Penelitian ini menggunakan metode yang lebih sederhana dan praktis.

---

#### Kelebihan Jurnal (Kritik Positif)

**1. Metodologi dual-layer yang elegan (Jurnal [3])**

Pemanfaatan 1st LSB sebagai tamper detector dan 2nd LSB sebagai penyimpan data EPR + hash merupakan desain yang efisien dan inovatif. Pendekatan ini mengoptimalkan kapasitas watermark tanpa mengorbankan kualitas visual.

**2. Evaluasi serangan yang komprehensif (Jurnal [2], [3])**

Keduanya menguji berbagai jenis serangan: cropping, copy-paste, collage, constant-average attack, dan noise. Ini memberikan gambaran robustness yang realistis terhadap kondisi dunia nyata.

**3. Penggunaan metrik kriptanalisis yang tepat (Jurnal [4])**

Penggunaan CORR, entropy, NPCR, dan UACI sesuai standar NIST untuk evaluasi keamanan enkripsi. Memberikan jaminan keamanan yang dapat diverifikasi secara objektif.

**4. Kajian pustaka yang sangat komprehensif (Jurnal [5])**

Review 200+ referensi dengan pembahasan sistematis mencakup chaotic encryption, DNA-based encryption, DWT, DCT, LSB, fragile vs robust watermarking, dan berbagai serangan. Menjadi fondasi teori yang kuat untuk penelitian di domain ini.

**5. Dataset medis yang autentik (Jurnal [3], [4])**

Jurnal [3] menggunakan citra CT dan MRI nyata, jurnal [4] menggunakan CBIS-DDSM (mammography). Dataset medis asli meningkatkan validitas eksternal penelitian dan memastikan relevansi dengan kondisi klinis sebenarnya.

**6. Desain blind extraction (Jurnal [2])**

Deteksi buta (blind extraction) tidak memerlukan citra asli saat verifikasi. Sangat praktis untuk aplikasi klinis di mana citra asli mungkin tidak selalu tersedia atau telah terakuisisi ulang.

**7. Konsep trigger-based yang futuristik (Jurnal [7])**

Pendekatan trigger-based watermarking pada model ML membuka peluang baru untuk melindungi model AI di bidang medis, sesuai tren perkembangan AI di healthcare.

---

#### Kekurangan Jurnal (Kritik Negatif)

**1. Dataset sangat kecil (Jurnal [2], [3])**

Jurnal [2] hanya menggunakan 30 sampel (CoMoFoD), jurnal [3] hanya 6 citra. Sampel yang terlalu kecil tidak cukup untuk generalisasi hasil. Diperlukan minimal ratusan sampel untuk klaim akurasi yang valid secara statistik.

**2. Tidak ada analisis waktu proses (Jurnal [1], [2], [3])**

Tidak ada jurnal yang melaporkan waktu eksekusi enkripsi/watermarking. Untuk aplikasi medis real-time, waktu proses adalah faktor kritis yang harus dievaluasi, terutama pada citra DICOM berukuran besar.

**3. Keterbatasan jenis serangan yang diuji (Jurnal [6])**

Hanya menguji serangan AWGN, tidak menguji serangan geometris (rotasi, scaling, cropping) atau serangan kompresi (JPEG compression). Evaluasi serangan menjadi tidak komprehensif.

**4. Tidak ada uji statistik yang memadai (Jurnal [1], [2], [3])**

Tidak ada Confidence Interval, uji hipotesis, atau analisis variansi. Hasil hanya dilaporkan sebagai nilai rata-rata tanpa indikator kesalahan (error bar), sehingga signifikansi statistik tidak dapat ditentukan.

**5. Asumsi keamanan hash yang lemah (Jurnal [2])**

Menggunakan MD5 yang sudah diketahui rentan terhadap collision attack sejak tahun 2004. SHA-256 atau SHA-3 seharusnya menjadi pilihan yang lebih aman untuk aplikasi medis yang memerlukan tingkat keamanan tinggi.

**6. Tidak mempertimbangkan overhead storage (Jurnal [3])**

Dual-layer watermarking menambah ukuran data, namun tidak ada analisis berapa besar overhead storage yang ditambahkan dan dampaknya terhadap infrastruktur penyimpanan rumah sakit yang biasanya sudah terbatas.

**7. Kurangnya benchmarking dengan metode lain (Jurnal [4])**

Tidak ada perbandingan langsung (head-to-head) dengan metode enkripsi lain seperti Chaotic Map atau DNA-based encryption. Tanpa benchmarking, sulit menentukan apakah metode yang diusulkan benar-benar lebih baik.

**8. Asumsi kondisi kanal ideal (Jurnal [6])**

Tidak mempertimbangkan distorsi yang terjadi saat transmisi melalui jaringan telemedicine (packet loss, latency, bandwidth limitation). Kondisi dunia nyata jauh dari ideal.

---

#### Kesimpulan Analisis

Berdasarkan tinjauan terhadap 7 literatur, dapat disimpulkan:

1. **Kombinasi enkripsi + watermarking merupakan pendekatan yang menjanjikan** untuk keamanan citra medis, namun belum ada penelitian yang mengintegrasikan AES + fragile LSB + hash kriptografi dalam satu framework secara utuh.

2. **Gap utama** adalah keterbatasan dataset kecil, ketiadaan analisis waktu proses, dan evaluasi serangan yang belum komprehensif — terutama terhadap serangan spesifik citra medis.

3. **Pendekatan penelitian ini** (AES encryption + fragile watermarking LSB + hash verifikasi) memiliki potensi untuk mengisi gap tersebut dengan menawarkan proteksi tiga lapis: *confidentiality* (AES), *integrity* (LSB watermarking), dan *authenticity* (hash verification).

4. **Rekomendasi untuk penelitian selanjutnya:**
   - Gunakan dataset medis yang lebih besar (minimal 500-1000 citra)
   - Tambahkan analisis waktu proses dan overhead storage
   - Uji serangan yang lebih beragam termasuk serangan AI-based manipulation
   - Gunakan SHA-256/SHA-3 menggantikan MD5
   - Lakukan benchmarking dengan minimal 2 metode kompetitor
   - Sertakan analisis statistik yang memadai (CI, uji hipotesis)

---

## Peta Topik Literatur

### Berdasarkan Domain Metode

| Domain | Referensi |
|--------|-----------|
| **Enkripsi AES pada DICOM** | [1], [3], [4] |
| **Fragile Watermarking LSB** | [2], [3] |
| **Hash Kriptografi (MD5/SHA-256)** | [2], [3] |
| **Digital Signature** | [1], [6] |
| **Transform Domain (DWT/DCT)** | [6] |
| **Double Random Phase Encryption** | [6] |
| **Selective Encryption** | [4] |
| **Fragile Watermarking (ML model)** | [7] |
| **Systematic Review (Kriptografi + Watermarking)** | [5] |

### Berdasarkan Metrik Evaluasi

| Metrik | Referensi |
|--------|-----------|
| PSNR | [1], [2], [3], [4], [6] |
| SSIM | [2], [3], [6] |
| NPCR | [1], [4] |
| MSE | [1], [3] |
| NCC | [6], [7] |
| Akurasi Deteksi | [2] |
| TDR (Tampered Detection Rate) | [3] |
| Entropy | [4] |
| Correlation Coefficient | [4], [6] |

---

## Catatan untuk Penulisan Jurnal

### Referensi yang Layak Sitasi (Jurnal SINTA >= 3 / Internasional bereputasi)
1. **Advanced watermarking technique** (2019) — dual-layer LSB + AES untuk citra medis
2. **Automatic Selective Encryption** (2023) — Applied Sciences, selektif enkripsi DICOM
3. **Security of Medical Images for Telemedicine** (2022) — Systematic review komprehensif
4. **Signing and Verifying** (2022) — Entropy, DWT+DCT+DRPE untuk citra medis
5. **Trigger-Based Fragile Model** (2024) — Konferensi, fragile watermarking untuk model ML

### Referensi Tambahan (bukan sitasi jurnal, tapi bermanfaat)
6. **Penerapan Enkripsi dan Tanda Tangan Digital** (2024) — makalah mahasiswa, background AES+DICOM
7. **Pelokalan Manipulasi Citra Digital** (2026) — Jurnal SINTA 4, metodologi fragile watermarking LSB+MD5

### Masih Perlu Ditambahkan
- Minimal 15-20 sumber untuk jurnal SINTA 3
- Cari jurnal internasional (Q1/Q2) tentang:
  - Medical image encryption + watermarking combination
  - Fragile watermarking tamper detection medical image
  - DICOM security watermarking encryption
  - Medical image deepfake manipulation detection