# Fase Research — Review Literatur Watermarking DICOM

Dokumen ini merangkum analisis literatur dari beberapa jurnal terkait *medical image watermarking* dan kriptografi DICOM. Tujuannya adalah mengidentifikasi **masalah / gap** dari penelitian sebelumnya sebagai dasar penyusunan jurnal baru.

---

## 1. Paper: Data Hiding for Clinical Information in DICOM Images via Reversible Halftone Fragile Watermarking

- **Penulis:** Mosco-Garcia, Cedillo-Hernandez, & Shouno (2025)

### Ringkasan Analisis

| Aspek | Hasil Analisis |
|---|---|
| **Medical Modality** | CT, MRI, dan X-ray/CR (Computed Radiography). Penulis mengevaluasi kapasitas embedding menggunakan ukuran tipikal MRI, CT, dan CR serta menggunakan citra medis dari TCIA. |
| **DICOM Standard** | Yes. Metode dirancang khusus untuk citra medis DICOM 16-bit (uint16 DICOM images) dan menanamkan watermark langsung ke dalam bit-plane citra DICOM. |
| **AES Encryption** | No. Penelitian tidak menggunakan AES. Keamanan watermark diperoleh melalui chaotic encryption berbasis logistic chaotic map sebelum proses embedding. |
| **Watermark Type** | Foto pasien (patient image), informasi klinis pasien (confidential clinical information), watermark autentikasi untuk integritas data. Watermark dibentuk dari citra pasien yang diubah menjadi halftone image dan informasi klinis yang disisipkan dalam area background hasil segmentasi. |
| **Watermark Nature** | Fragile Watermark. Penulis secara eksplisit menyatakan bahwa metode menggunakan fragile watermarking sehingga perubahan pada citra akan merusak watermark dan dapat digunakan untuk mendeteksi manipulasi. |
| **Tamper Detection** | Yes. Menggunakan kombinasi: fragile watermarking, checksum per blok, dan chaotic encryption. Perubahan pada citra menyebabkan kerusakan watermark yang dapat dideteksi selama proses ekstraksi. |
| **Tamper Localization** | Yes. Sistem mampu menunjukkan area yang dimanipulasi menggunakan: checksum embedding, anomaly detection mask, dan partial watermark recovery. Dilaporkan False Positive Rate = 1.2% pada proses lokalisasi. |
| **Tamper Recovery** | Partial. Metode dapat mengekstraksi bagian watermark yang tidak rusak dan mengidentifikasi area yang dimodifikasi. Namun tidak terdapat mekanisme khusus untuk merekonstruksi atau memperbaiki daerah yang telah dimanipulasi. Watermark hanya dapat dipulihkan sebagian pada area yang tidak terkena modifikasi. |
| **Watermarking Method** | Reversible Halftone Fragile Watermarking. Komponen utama metode: Jarvis Error Diffusion Halftoning, Segmentation-based background enhancement, Data Hiding in Binary Images with High Payload, Logistic Chaotic Encryption, Pseudo-random Walk Embedding, Pixel-to-Block (PTB) Transformation, Checksum-Based Authentication, DnCNN-Based Reconstruction. Metode menggabungkan watermarking reversible dengan halftoning dan deep-learning denoising untuk memulihkan kualitas citra. |
| **Attack Tests** | Superimposed Figure, JPEG Compression (QF=50), Gaussian Noise, Contrast Adjustment. Hasilnya watermark sangat sensitif terhadap serangan, sesuai karakteristik fragile watermark. |
| **Robustness Results** | Lihat tabel Robustness Results di bawah. |
| **Computational Cost** | Dilaporkan. Embedding Time = 93 detik (hardware: Apple M2 Chip). Lebih cepat dibanding metode Difference Expansion yang membutuhkan sekitar 112 detik. |
| **Image Quality** | Kualitas citra setelah embedding sangat tinggi (lihat tabel Image Quality). SSIM = 0.96 pada kapasitas watermark hingga 90%. |
| **Reconstruction Stage** | PSNR = 67.50 dB dan SSIM = 0.9995. Nilai tersebut menunjukkan distorsi visual yang sangat kecil dan rekonstruksi watermark yang sangat baik. |
| **Embedding Capacity** | Kapasitas penyisipan cukup tinggi (lihat tabel Embedding Capacity), menggunakan 15 bit per blok hasil transformasi PTB. |

#### Robustness Results

| Attack | Recovered Bits | BER | Recognition |
|---|---|---|---|
| No Modification | 100% | 0% | Excellent |
| Superimposed Figure | 96.22% | 0.03% | Good |
| JPEG Compression | 37.7% | 62.3% | Poor |
| Gaussian Noise | 21.1% | 50.35% | Poor |
| Contrast Adjustment | 46.97% | 53.03% | Poor |

#### Image Quality (PSNR)

| Ukuran Citra | PSNR |
|---|---|
| 3520×4130 | 96.59 dB |
| 512×512 | 96.72 dB |
| 320×320 | 96.68 dB |

#### Embedding Capacity

| Modality | Kapasitas |
|---|---|
| MRI 640×640 | 384,000 bits |
| CT 1024×1024 | 983,040 bits |
| CR 7040×8560 | 56,496,000 bits |

### Strengths

1. Dirancang khusus untuk citra DICOM 16-bit.
2. Menggunakan reversible watermarking, sehingga informasi tersembunyi dapat diekstraksi tanpa kehilangan data.
3. Mengimplementasikan tamper detection dan tamper localization.
4. Menggunakan chaotic encryption untuk meningkatkan keamanan watermark.
5. Mengintegrasikan DnCNN deep learning untuk meningkatkan kualitas rekonstruksi citra pasien.
6. Memiliki embedding capacity sangat besar, terutama pada citra CR beresolusi tinggi.
7. Menyematkan foto pasien sebagai mekanisme autentikasi visual tambahan.
8. Melaporkan metrik performa secara kuantitatif (PSNR, SSIM, BER, embedding time).

### Limitations

1. Robustness terhadap serangan umum masih rendah karena sifat fragile watermarking.
2. Performa menurun drastis pada JPEG Compression, Gaussian Noise, dan Contrast Adjustment.
3. Tidak menyediakan mekanisme tamper recovery untuk memperbaiki area yang telah dimodifikasi.
4. Dataset pengujian tidak dijelaskan secara rinci jumlah citranya dalam paper.
5. Waktu embedding masih relatif tinggi (93 detik) untuk aplikasi real-time.
6. Fokus utama pada autentikasi dan integritas, bukan watermark yang robust terhadap kompresi atau transmisi.

### Future Work

1. Mengembangkan watermark yang lebih tahan terhadap kompresi dan noise.
2. Menambahkan mekanisme tamper recovery secara otomatis.
3. Mengoptimalkan waktu embedding dan extraction.
4. Menguji pada dataset multi-modality yang lebih besar.
5. Mengembangkan teknik deep learning yang lebih efisien untuk rekonstruksi watermark.
6. Menggabungkan kemampuan localization dengan recovery untuk sistem autentikasi medis yang lebih lengkap.

### Relevansi untuk Penelitian Kriptografi DICOM

**Sangat relevan** jika topik penelitian terkait:

- DICOM Security
- Medical Image Watermarking
- Data Hiding pada DICOM
- Patient Authentication
- Tamper Detection & Localization
- Chaotic Encryption
- Reversible Watermarking

**Kurang relevan** apabila fokus utama penelitian adalah:

- AES-based Medical Watermarking
- Robust Watermarking terhadap kompresi JPEG
- Tamper Recovery penuh
- Blockchain-based DICOM Security

**Skor relevansi: 9/10.** Paper ini menggabungkan DICOM, reversible watermarking, chaotic encryption, autentikasi pasien, serta deteksi dan lokalisasi manipulasi dalam satu framework.

---

## 2. Paper: A Fragile Reversible Watermarking Technique for Medical Imaging Security Using Prediction Error Expansion and Canny Edge Detection

- **Penulis:** Asaad F. Qasim & Ahmed Hussain Ali (2026)

### Ringkasan Analisis

| Aspek | Hasil Analisis |
|---|---|
| **Medical Modality** | MRI Brain, MRI Breast, dan CT Lung. Dataset terdiri dari 12 citra medis DICOM (4 Brain MRI, 4 Breast MRI, 4 CT Lung). |
| **DICOM Standard** | Yes. Penelitian menggunakan citra medis format DICOM 16-bit dan memanfaatkan metadata DICOM sebagai bagian utama watermark untuk autentikasi pasien dan citra. |
| **AES Encryption** | No. Tidak menggunakan AES atau algoritma kriptografi simetris. Integritas citra dijamin menggunakan digital signature berbasis MD5 dan reversible watermarking. |
| **Watermark Type** | Metadata pasien DICOM (Patient ID, Name, Birth Date, Modality, dan lainnya) serta digital signature yang dihasilkan menggunakan hash MD5. |
| **Watermark Nature** | Fragile Watermark. Dirancang untuk mendeteksi perubahan sekecil apa pun pada citra medis. Perubahan pada citra menyebabkan perubahan watermark yang diekstraksi. |
| **Tamper Detection** | Yes. Sistem mampu mendeteksi manipulasi baik disengaja maupun tidak disengaja melalui ketidaksesuaian watermark hasil ekstraksi dengan watermark asli. |
| **Tamper Localization** | No. Sistem hanya mendeteksi adanya manipulasi tetapi tidak menunjukkan lokasi atau area spesifik yang dimanipulasi. Penulis secara eksplisit menyarankan tamper localization sebagai pengembangan penelitian berikutnya. |
| **Tamper Recovery** | Limited. Sistem memiliki kemampuan reversible watermarking sehingga citra asli dapat dipulihkan sempurna apabila citra tidak mengalami manipulasi. Namun tidak tersedia mekanisme recovery untuk bagian citra yang telah ditamper. Nilai PSNR recovery = ∞ dan BER = 0 menunjukkan pemulihan sempurna pada kondisi normal. |
| **Watermarking Method** | Reversible Watermarking berbasis Prediction Error Expansion (PEE) dikombinasikan dengan Automatic ROI-RONI Segmentation dan Canny Edge Detection. Watermark disisipkan pada area tepi (edge) ROI untuk mengurangi distorsi visual. |
| **Embedding Region** | ROI (Region of Interest), tepatnya pada blok tepi hasil deteksi Canny Edge. Panjang watermark disimpan di area RONI menggunakan Difference Expansion sederhana. |
| **Attack Tests** | Median Filter, Salt & Pepper Noise, Gaussian Noise, Gaussian Filter, Rotation, Cropping, Resize, Brightness Adjustment, Intensity Adjustment, Watermark Forgery, Copy Attack, dan Collusion Attack. |
| **Computational Cost** | Tidak dilaporkan secara kuantitatif. Implementasi dilakukan menggunakan MATLAB R2016a pada PC Windows 11 dengan Intel Core i7-1065G7 dan RAM 16 GB, tetapi tidak ada analisis waktu embedding, extraction, maupun kompleksitas komputasi. |
| **Image Quality** | Sangat tinggi. Rata-rata PSNR = 97.19 ± 1.73 dB dan rata-rata SSIM = 0.999996 ± 0.000010, menunjukkan watermark hampir tidak memengaruhi kualitas visual citra medis. |
| **Payload Capacity** | Rata-rata watermark sekitar 7835 bit per gambar dengan kapasitas maksimum bergantung pada jumlah edge-block ROI yang tersedia. |
| **Reversibility Performance** | Sangat baik. Original image dan watermark dapat dipulihkan secara sempurna dengan PSNR = ∞ dan BER = 0 pada proses ekstraksi normal. |

---

## 3. Paper: Reversible Watermarking for Medical Images Using ROI-based Tamper Localization and Recovery

- **Penulis:** Aulia Arham , Teguh Bharata Adji , Syukron Abu Ishaq Alfarozi , Hanung Adi Nugroho

### Ringkasan Analisis

| Aspek | Hasil Analisis |
|---|---|
| **Medical Modality** | Citra medis MRI Brain, MRI Breast, dan CT Lung. |
| **DICOM Standard** | Yes. Penelitian menggunakan citra medis dalam format DICOM dan mempertahankan kompatibilitas dengan standar DICOM. Informasi metadata pasien dan atribut DICOM juga dimanfaatkan sebagai bagian dari watermark. |
| **AES Encryption** | No. Penelitian tidak menggunakan algoritma AES untuk enkripsi. Keamanan data lebih difokuskan pada mekanisme watermarking reversibel, autentikasi, dan deteksi manipulasi menggunakan informasi hash serta data recovery yang disisipkan ke dalam citra. |
| **Watermark Type** | Informasi pasien (Electronic Patient Record/EPR), metadata DICOM, recovery watermark, dan authentication watermark. |
| **Watermark Nature** | Fragile Watermark. Watermark dirancang untuk mendeteksi modifikasi pada citra medis dan menjaga integritas data diagnostik. |
| **Tamper Detection** | Yes. Sistem mampu mendeteksi apakah citra telah mengalami manipulasi berdasarkan ketidaksesuaian watermark autentikasi yang diekstraksi. |
| **Tamper Localization** | Yes. Salah satu kontribusi utama penelitian ini adalah kemampuan mengidentifikasi lokasi area yang telah dimanipulasi melalui pendekatan ROI-based tamper localization. |
| **Tamper Recovery** | Yes. Sistem menyediakan mekanisme recovery untuk memperbaiki area yang mengalami manipulasi menggunakan recovery information yang disisipkan selama proses watermark embedding. |
| **Watermarking Method** | Reversible Watermarking (RW); ROI-RONI Segmentation; Tamper Localization Based on ROI Blocks; Recovery Watermark Embedding; Histogram Shifting / Data Embedding Technique. Mekanisme autentikasi dan recovery dilakukan secara terpisah untuk menjaga kualitas citra medis. |
| **Attack Tests** | Copy-paste attack, object insertion, object removal, region modification, pixel alteration, deliberate tampering pada ROI. Fokus utama pengujian adalah kemampuan sistem dalam mendeteksi, melokalisasi, dan memulihkan area yang dimanipulasi. |
| **Computational Cost** | Tidak dilaporkan secara rinci. Penelitian lebih berfokus pada performa keamanan, kualitas citra, serta efektivitas tamper localization dan recovery dibanding analisis kompleksitas komputasi atau runtime. |
| **Image Quality** | Kualitas citra setelah watermarking tetap tinggi dengan PSNR yang menunjukkan distorsi sangat rendah, SSIM mendekati 1, dan kemampuan reversibilitas memungkinkan citra asli dipulihkan secara sempurna setelah ekstraksi watermark. Hal ini penting karena perubahan kualitas citra medis dapat mempengaruhi diagnosis klinis. |

### Strengths

1. Mendukung **Tamper Localization** — mampu menentukan lokasi area yang mengalami manipulasi, bukan hanya mendeteksi keberadaan serangan.
2. Mendukung **Tamper Recovery** — area yang rusak akibat tampering dapat dipulihkan menggunakan recovery watermark.
3. **Reversible Watermarking** — citra asli dapat direkonstruksi tanpa kehilangan informasi diagnostik.
4. **ROI-Based Protection** — memberikan perlindungan lebih kuat pada area diagnostik penting (ROI).
5. **Kompatibel dengan DICOM** — mendukung kebutuhan Medical Image Management dan Telemedicine.
6. **Menjaga Kualitas Citra** — distorsi hasil embedding sangat rendah sehingga tidak mempengaruhi interpretasi klinis.
7. **Menyediakan Fungsi Keamanan yang Lengkap** — meliputi Authentication, Integrity Verification, Tamper Detection, Tamper Localization, dan Tamper Recovery, yang jarang hadir secara bersamaan dalam satu metode watermarking.

### Limitations

1. Tidak menggunakan algoritma kriptografi modern (AES atau algoritma enkripsi kuat lainnya) untuk melindungi payload watermark.
2. Robustness bukan fokus utama — karena menggunakan fragile watermark, metode kurang tahan terhadap operasi pemrosesan citra normal seperti compression, noise addition, dan filtering.
3. Evaluasi dataset terbatas — jumlah dan keragaman dataset masih relatif terbatas dibanding kebutuhan implementasi klinis skala besar.
4. Computational efficiency tidak dianalisis — tidak tersedia pengukuran detail mengenai embedding time, extraction time, recovery time, dan computational complexity.
5. Pengujian multi-center belum dilakukan — belum dievaluasi pada data dari berbagai rumah sakit atau perangkat medis yang berbeda.

### Future Work

1. Menguji sistem pada dataset yang lebih besar dan beragam.
2. Mengembangkan mekanisme recovery yang lebih efisien.
3. Meningkatkan kapasitas embedding tanpa menurunkan kualitas citra.
4. Mengintegrasikan teknik kriptografi yang lebih kuat untuk meningkatkan keamanan watermark.
5. Mengembangkan metode yang tetap mampu melakukan autentikasi dan recovery pada lingkungan telemedicine modern.
6. Mengevaluasi performa pada berbagai modalitas medis dan skenario serangan yang lebih kompleks.

---

## 4. Paper: Semi-Fragile Authentication Watermarking Citra Medis berbasis IWT-DCT dan ECDSA

- **Penulis:** Rupa Ch, Naga Vivek K, Gautam Srivastava, dan Reddy Gadekallu (2024)
- **Publikasi:** International Journal of Cognitive Computing in Engineering, Vol. 5, halaman 78-87.
- *Catatan: judul asli paper tidak tercantum dalam catatan review; judul di atas bersifat deskriptif sesuai isi analisis.*

### Ringkasan Analisis

| Aspek | Hasil Analisis |
|---|---|
| **Medical Modality** | MRI Brain. Penelitian secara khusus berfokus pada citra medis otak (brain medical images) untuk aplikasi telemedicine. Tidak menggunakan CT, X-ray, maupun multi-modality. |
| **DICOM Standard** | Tidak dilaporkan secara eksplisit. Paper hanya menyebut penggunaan brain medical images dan ROI segmentation, tetapi tidak menyatakan penggunaan format DICOM maupun metadata DICOM sebagai watermark. |
| **AES Encryption** | No. Penelitian tidak menggunakan AES. Keamanan didasarkan pada kombinasi SHA-256 hashing, ECDSA digital signature, dan watermarking berbasis transform domain. |
| **Watermark Type** | Hash dari ROI (SHA-256 hash) dan ECDSA Digital Signature yang dihasilkan dari ROI yang telah di-hash. |
| **Watermark Nature** | Semi-Fragile Authentication Watermark. Watermark digunakan untuk memverifikasi integritas dan autentikasi citra, serta mendeteksi adanya modifikasi pada ROI. Namun metode juga dirancang agar tetap bertahan terhadap berbagai serangan pemrosesan citra. |
| **Tamper Detection** | Yes. Sistem dapat mendeteksi manipulasi dengan membandingkan hash ROI dan digital signature yang diekstraksi dengan nilai asli. Jika tidak cocok maka citra dianggap telah diubah (tampered). |
| **Tamper Localization** | No. Paper hanya melakukan verifikasi autentisitas dan deteksi perubahan, tanpa menunjukkan lokasi piksel atau area yang dimanipulasi. |
| **Tamper Recovery** | No. Tidak tersedia mekanisme khusus untuk mengembalikan area yang telah dimanipulasi. Sistem hanya melakukan deteksi dan verifikasi integritas. |
| **Watermarking Method** | Menggunakan Integer Wavelet Transform - Discrete Cosine Transform (IWT-DCT) untuk embedding watermark pada high-frequency sub-bands. Dikombinasikan dengan ROI-RONI segmentation, SHA-256 hashing, dan ECDSA digital signature. |
| **Attack Tests** | Paper menyatakan pengujian terhadap berbagai serangan pemrosesan citra seperti noise addition, filtering, dan compression. Namun rincian lengkap jenis serangan (Gaussian, cropping, rotation, resize, dll.) tidak dijabarkan secara detail. |
| **Computational Cost** | Dilaporkan. Implementasi berjalan pada Windows 10 dengan kebutuhan minimal 4 GB RAM dan 4 GB SSD. Waktu embedding sekitar 2.16 detik dan waktu extraction sekitar 1.03 detik, lebih cepat dibanding beberapa metode pembanding. |
| **Image Quality** | Kualitas citra sangat baik setelah watermarking dengan PSNR = 68.67 dB, MSE = 0.96, dan SSIM = 0.98. Nilai ini menunjukkan watermark hampir tidak memengaruhi kualitas visual citra medis. |

### Strengths

1. Menggunakan SHA-256 yang lebih aman dibanding MD5.
2. Memanfaatkan ECDSA untuk autentikasi citra medis.
3. Memiliki kemampuan tamper detection.
4. Menggunakan transform domain (IWT-DCT) yang robust terhadap berbagai serangan.
5. Menjaga kualitas citra sangat tinggi (PSNR 68.67 dB, SSIM 0.98).
6. Embedding dan extraction relatif cepat.
7. Fokus pada keamanan telemedicine dan perlindungan integritas data pasien.

### Limitations

1. Hanya diuji pada brain medical images.
2. Tidak mendukung tamper localization.
3. Tidak menyediakan tamper recovery.
4. Tidak menggunakan reversible watermarking sehingga citra asli tidak dapat dipulihkan sempurna seperti RDH (Reversible Data Hiding).
5. Skalabilitas untuk dataset besar masih menjadi tantangan.
6. Validasi klinis dunia nyata belum dilakukan.

### Future Work

1. Integrasi deep learning-based watermarking untuk meningkatkan imperceptibility dan robustness.
2. Penggunaan blockchain untuk verifikasi integritas dan keamanan data.
3. Peningkatan ketahanan terhadap steganalysis.
4. Perluasan ke multi-modal medical data.
5. Pengembangan solusi yang lebih scalable untuk dataset besar.
6. Implementasi dan validasi pada lingkungan klinis nyata.

---

## 5. Perbandingan Antar Paper

| Aspek | Paper 1 (Mosco-Garcia 2025) | Paper 2 (Qasim & Ali 2026) | Paper 3 (ROI-based) | Paper 4 (Rupa Ch 2024) |
|---|---|---|---|---|
| **Medical Modality** | CT, MRI, CR | MRI Brain/Breast, CT Lung | MRI Brain/Breast, CT Lung | MRI Brain |
| **DICOM Standard** | Yes | Yes | Yes | Tidak eksplisit |
| **AES Encryption** | No (chaotic) | No (MD5) | No (hash) | No (SHA-256 + ECDSA) |
| **Watermark Nature** | Fragile | Fragile | Fragile | Semi-Fragile |
| **Reversible** | Yes | Yes | Yes | No |
| **Tamper Detection** | Yes | Yes | Yes | Yes |
| **Tamper Localization** | Yes | No | Yes | No |
| **Tamper Recovery** | Partial | Limited (No) | Yes | No |
| **Computational Cost** | 93 s (embedding) | Tidak dilaporkan | Tidak dilaporkan | 2.16 s / 1.03 s |
| **PSNR** | ~96 dB | ~97 dB | Tinggi (tidak dirinci) | 68.67 dB |
| **Robustness** | Rendah (fragile) | Rendah (fragile) | Rendah (fragile) | Semi-robust |

## 6. Temuan Masalah / Gap untuk Penelitian Baru

Berdasarkan kekurangan yang dilaporkan pada keempat paper, gap yang belum terjawab antara lain:

1. **Tidak ada yang menggabungkan kriptografi modern (AES) dengan metode watermarking DICOM.** Keempat paper menghindari AES dan hanya mengandalkan chaotic encryption (P1), MD5 (P2), hash + ECDSA (P3/P4). Hash MD5 (P2) bahkan sudah tidak direkomendasikan secara kriptografis.
2. **Fungsi keamanan belum lengkap dalam satu metode.** Paper 1 (localization, tanpa recovery penuh) vs Paper 3 (localization + recovery, tanpa kriptografi kuat); Paper 2 dan Paper 4 tanpa localization maupun recovery.
3. **Robustness rendah pada pendekatan fragile.** P1, P2, P3 sangat sensitif terhadap kompresi JPEG, noise, dan filter, sehingga kurang cocok untuk transmisi telemedicine.
4. **Evaluasi dataset terbatas / single-modality.** P4 hanya MRI Brain; P2 dan P3 berjumlah kecil (12 citra); P1 tidak merinci jumlah dataset.
5. **Kompleksitas komputasi sering tidak dilaporkan.** P2 dan P3 tidak menyediakan embedding/extraction time; P1 lambat (93 detik) untuk skala real-time.
6. **Belum ada kombinasi reversible watermarking + tamper recovery + kriptografi modern + evaluasi multi-modal dalam satu framework.** Ini adalah celah penelitian yang dapat diisi oleh jurnal baru.

**Saran arah penelitian (realistis untuk tugas akhir, target Sinta 3):**

Menggabungkan kelima fitur sekaligus (reversible + AES + localization + recovery + multi-modal) berisiko terlalu luas untuk satu tugas akhir. Fokus yang disarankan adalah dua gap paling krusial yang masih dapat diimplementasikan dalam satu semester:

1. **Integrasi enkripsi AES** ke dalam reversible watermarking berbasis ROI pada citra DICOM (menjawab gap #1).
2. **Tamper detection + tamper localization** sebagai fungsi keamanan yang relatif lengkap, dengan reversibilitas untuk menjaga kualitas diagnostik (menjawab gap #2). *Tamper recovery* dapat dijadikan pengembangan lanjutan karena membutuhkan kapasitas embedding besar.

**Rumusan masalah (mendekati format latar belakang jurnal):**

1. Bagaimana merancang skema embedding dan ekstraksi watermark terenkripsi AES berbasis ROI pada citra DICOM yang tetap reversible (citra asli dapat dipulihkan sempurna)?
2. Bagaimana akurasi deteksi dan lokalisasi manipulasi (tamper detection & localization) dari skema tersebut?
3. Bagaimana dampak enkripsi dan kapasitas watermark terhadap kualitas citra (PSNR, SSIM, BER) serta waktu komputasi embedding/ekstraksi?

**Kontribusi yang diharapkan (cukup untuk Sinta 3):**

- Skema *reversible ROI-based watermarking* DICOM dengan payload terenkripsi AES-128/256.
- Evaluasi kuantitatif lengkap (PSNR, SSIM, BER, akurasi deteksi/lokalisasi tampering, runtime) pada citra DICOM nyata dengan 2–3 modality.
- Implementasi dengan pustaka standar (mis. Python: pydicom + PyCryptodome + OpenCV) sehingga mudah direproduksi dan dibandingkan.

**Catatan:** untuk jurnal Sinta 3, kesuksesan lebih ditentukan oleh kelengkapan dan ketelitian evaluasi serta kebaruan kombinasi AES + ROI reversible watermarking, bukan banyaknya fitur. Sebaiknya hindari memaksakan tamper recovery dan dataset yang terlalu besar agar lingkup tugas akhir tetap selesai tepat waktu.