# Meningkatkan Keamanan File DICOM melalui Enkripsi AES: Implementasi dan Analisis

**Penulis:** Aloysius Arya Wibisono (18329925)

**Institusi:** Program Studi Teknik Biomedis, Sekolah Teknik Elektro dan Informatika, Institut Teknologi Bandung

**Tipe:** Makalah Kuliah | **Tahun:** 2024

**Kata Kunci:** AES, DICOM, Medical Data, PSNR, NPCR, Histogram

---

## Abstract

This paper discusses the implementation of AES encryption on DICOM files in the context of medical data security and privacy. Using the AES encryption method, this study examines the effectiveness of encryption on DICOM images through histogram analysis, PSNR, and NPCR. The analysis results indicate that encryption affects changes in the encrypted images, but the decrypted images successfully maintain the integrity of information with NPCR approaching zero and high PSNR. This indicates that encrypted images can still be used accurately in patient diagnosis and treatment. In conclusion, AES encryption is an effective choice for securing medical image data without compromising information quality.

---

## 1. Pendahuluan

Salah satu sistem yang penting di rumah sakit adalah sistem PACS (Picture Archiving and Communication System) yakni sistem yang mengatur bagaimana data citra dari modalitas-modalitas tertentu dikirimkan dan disimpan untuk dianalisis. Standar DICOM (Digital Imaging and Communications in Medicine) digunakan untuk standardisasi pertukaran dan penyimpanan citra digital, yang mencakup format data penyimpanan, protokol komunikasi, dan transfer antar file.

Seiring berkembangnya penggunaan DICOM sebagai file medis, muncul masalah-masalah sekuritas. Menurut Departemen Health and Human Services, terdapat lebih dari 3000 kebocoran data yang melibatkan lebih dari 500 riwayat medis di Amerika. Algoritma AES (Advanced Encryption Standard) merupakan salah satu algoritma yang sangat cocok untuk enkripsi file citra, termasuk file DICOM, karena memiliki keunggulan dalam hal keamanan yang sangat tinggi dan efisiensi proses.

## 2. Studi Pendahuluan

### 2.1. Standar DICOM

DICOM adalah sebuah standar yang mencakup format data penyimpanan, protokol komunikasi, dan struktur file untuk file citra biomedis. File DICOM terdiri dari:
- **Preamble** (128 bytes)
- **Prefix** ('D','I','C','M')
- **Header:** Data Set (Group 0002, Group 0008, dsb.)
- **Image Pixel Intensity Data**

Header berisi data pasien dan data citra seperti NIK, nama pasien, dan dimensi citra. Protokol DICOM dapat diintegrasikan dengan TCP/IP dan dilengkapi TLS agar data tetap aman.

### 2.2. Kriptografi

Kriptografi merupakan proses menyembunyikan atau mengacak informasi sehingga hanya orang yang memiliki akses dapat membacanya. Terdiri dari dua proses:
- **Enkripsi:** menyembunyikan informasi pada data
- **Dekripsi:** mengembalikan informasi yang telah terenkripsi

Dua jenis tipe enkripsi:
- **Kunci simetris:** satu kunci untuk enkripsi dan dekripsi (AES, DES, Blowfish)
- **Kunci asimetris:** dua kunci berbeda — publik dan privat (RSA, DSA)

### 2.3. AES (Advanced Encryption Standard)

AES (Rijndael) dikembangkan oleh Joan Daemen dan Vincent Rijmen. Proses enkripsi AES terdiri dari:
1. **Key Expansion:** penghasilan subkunci
2. **Initial Round:** AddRoundKey
3. **Main Rounds (10/12/14 kali):** SubBytes → ShiftRows → MixColumns → AddRoundKey
4. **Final Round:** SubBytes → ShiftRows → AddRoundKey (tanpa MixColumns)

## 3. Metodologi

Penelitian ini menguji efektivitas enkripsi file DICOM menggunakan AES melalui:

### 3.1. Persiapan Data
Data diambil dari rumah sakit Carolus di Jakarta — CT scan otak pasien stroke. Data dibagi menjadi tiga bagian berdasarkan ukuran: 10 MB, 15 MB, dan 20 MB. Header dipisahkan dari citra karena berisi data privasi pasien.

### 3.2. Implementasi Enkripsi AES
Menggunakan AES-256 dengan mode ECB, diimplementasikan dalam Python (PyCryptodome).

### 3.3. Analisis Metrik
- **Histogram:** perbandingan distribusi pixel sebelum dan sesudah enkripsi
- **PSNR:** mengukur kualitas enkripsi (semakin rendah = semakin baik)
- **NPCR:** mengukur persentase perubahan pixel

## 4. Hasil dan Pembahasan

| Citra DICOM | Ukuran | NPCR Enkripsi | PSNR Enkripsi | NPCR Dekripsi | PSNR Dekripsi |
|-------------|--------|---------------|---------------|----------------|----------------|
| DICOM 1 | 10 MB | 99.64% | 27.83 dB | 0.0% | inf dB |
| DICOM 2 | 15 MB | 99.61% | 27.91 dB | 0.0% | inf dB |
| DICOM 3 | 20 MB | 99.61% | 27.89 dB | 0.0% | inf dB |

**Temuan Utama:**
- NPCR enkripsi tinggi (~99.61%) menunjukkan perubahan piksel signifikan setelah enkripsi
- PSNR enkripsi ~27.8-27.9 dB menunjukkan citra terenkripsi masih mempertahankan kualitas informasi
- NPCR dekripsi 0% dan PSNR inf menunjukkan dekripsi sempurna — citra terdekripsi identik dengan citra asli
- Penting untuk citra medis: dekripsi harus mengembalikan citra secara utuh agar dapat dianalisis dokter

## 5. Kesimpulan

Proses enkripsi mempengaruhi perubahan pada citra terenkripsi, namun dekripsi berhasil mengembalikan citra ke keadaan semula. AES encryption efektif mengamankan data citra medis tanpa mengorbankan kualitas informasi.

---

## Referensi

1. Annadurai, K. & Rani, S. (2012). DICOM image authentication and encryption based on RSA and AES algorithms.
2. Kobayashi, L.O. & Furuie, S.S. (2009). Proposal for DICOM multiframe medical image integrity and authenticity. J Digit Imaging, 22(1), 71-83.
3. Natsheh, Q. et al. (2023). Automatic Selective Encryption of DICOM Images. Appl. Sci. 13, 4779.
4. Kannammal, A. & Subha Rani, S. (2012). DICOM Image Authentication and Encryption Based on RSA and AES Algorithms. IRAM 2012, CCIS vol 330.
