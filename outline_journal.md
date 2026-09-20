# Outline Jurnal — Proteksi Citra Medis DICOM

> Penyusun: Proyek Kriptografi (Fase 6). Target publikasi: **jurnal Sinta 3**.
> Sumber data: hasil implementasi & uji Fase 5A–5G (`05_plan_reversible.md`, `handoff.md`, README Bagian G).
> Bahasa: Indonesia (dapat dialihkan ke Inggris bila jurnal target berbahasa Inggris).

---

## 1. Judul (judul kerja)

**"Reversible Watermarking Terenkripsi AES untuk Proteksi dan Verifikasi Integritas Citra Medis DICOM**

> Pilih yang paling ringkas; kata kunci utama: reversible watermarking, PEE-HS, AES, tamper localization, DICOM.

---

## 2. Abstrak (150–250 kata)

Struktur isi:
1. Masalah: citra medis digital DICOM rentan kebocoran dan manipulasi (deepfake/augmentasi lesion) saat disimpan/dikirim; enkripsi saja tidak menjamin integritas setelah dekripsi; kebanyakan skema watermarking DICOM bersifat *lossy* dan belum mengombinasikan kriptografi modern.
2. Usulan: skema *reversible watermarking* berbasis **PEE-HS checkerboard multiround** untuk menyisipkan payload hash blok + digest metadata yang **dienkripsi AES-256-CBC**, dilengkapi deteksi dan lokalisasi manipulasi.
3. Metode uji: citra DICOM MRI 16-bit (24 slice), skenario tamper (piksel/blok), metrik PSNR, SSR/SSIM, BER, akurasi deteksi-lokalisasi, runtime.
4. Hasil utama:
   - PSNR setelah embedding 83,6–90,4 dB (16-bit); recovery eksak PSNR = ∞, BER = 0.
   - 24/24 slice terverifikasi dan ter-recovery sempurna; kapasitas payload 27–51 kbit.
   - Deteksi manipulasi 100% pada blok tampered (jalur tanpa enkripsi); kunci AES salah → ditolak tanpa crash.
   - Runtime ±0,2–0,4 s/slice.
5. Kesimpulan: skema memenuhi kerahasiaan (enkripsi) + integritas (autentikasi) + reversibilitas (kualitas diagnostik terjaga) dalam satu jaluar, dengan trade-off lokalisasi saat payload dienkripsi yang didiskusikan.

Kata kunci: *DICOM; reversible watermarking; prediction error expansion; AES-256; tamper detection and localization.*

---

## 3. Pendahuluan

- **Latar belakang:**
  - Digitalisasi citra medis (MRI, CT, X-ray/CR) memudahkan penyimpanan & telemedicine.
  - Ancaman: kebocoran data pasien (kerahasiaan) dan manipulasi citra (integritas) — termasuk AI deepfake yang menambah/menghapus tanda penyakit.
  - Regulasi (UU PDP, HIPAA/GDPR) mewajibkan perlindungan data kesehatan.
  - Enkripsi melindungi saat transit/at-rest, tetapi setelah dekripsi citra dapat diubah tanpa jejak → butuh mekanisme verifikasi integritas *in-band*.
- **Gap penelitian** (dari `01_fase_research.md`):
  - Paper 1 (Mosco-Garcia 2025): reversible halftone + chaotic encryption, tamper localization FPR 1,2%; lambat (93 s), tanpa kriptografi modern.
  - Paper 2 (Qasim & Ali 2026): PEE + Canny edge, tanpa tamper localization, MD5, dataset kecil (12 citra), tanpa runtime.
  - Paper 3 (Arham dkk. — ROI-based): localization + recovery lengkap, tetapi tanpa kriptografi kuat.
  - Paper 4 (Rupa Ch 2024): IWT-DCT + ECDSA, semi-fragile, tanpa reversible, hanya MRI brain.
  - **Belum ada yang mengombinasikan: AES + reversible watermarking + tamper detection & localization + evaluasi kuantitatif lengkap pada DICOM.**
- **Rumusan masalah** (3 pertanyaan riset, lihat Bagian A.3 / README):
  1. Bagaimana merancang skema embedding–ekstraksi watermark terenkripsi AES berbasis ROI pada DICOM yang tetap *reversible* (citra asli pulih sempurna)?
  2. Seberapa akurat deteksi & lokalisasi manipulasi skema tersebut?
  3. Bagaimana dampak enkripsi & kapasitas watermark terhadap kualitas citra (PSNR, SSIM, BER) dan waktu komputasi?
- **Tujuan & kontribusi:**
  1. Skema *reversible ROI watermarking* DICOM dengan payload terenkripsi AES-256.
  2. Fungsi tamper detection + tamper localization terpadu.
  3. Evaluasi kuantitatif lengkap (PSNR, SSIM, BER, deteksi/lokalisasi, runtime) pada DICOM nyata.
  4. Implementasi Python (pydicom + cryptography + numpy) yang reproduktif.
- **Batasan & kejujuran ilmiah:**
  - Dataset lokal: MRI only (multi-slice sebagai studi eksperimen); modalitas kedua (CT/CR) = pekerjaan lanjutan.
  - Lokalisasi presisi penuh berlaku pada jalur tanpa enkripsi; dengan enkripsi, deteksi kuat tetapi lokalisasi presisi berkurang (dijelaskan di Diskusi).
  - Side-channel (parameter round) di strip 16 baris RONI bersifat lossy-LSB — satu-satunya bagian non-lossless.

---

## 4. Tinjauan Pustaka (15–20 sumber; kerangka)

Konsep dasar:
- Kriptografi simetris: AES, mode operasi CBC/CTR/GCM, derivasi kunci PBKDF2. (NIST FIPS PUB 197.)
- *Reversible data hiding*: DE, HS, PEE; medis → syarat lossless untuk kualitas diagnostik.
- *Fragile vs semi-fragile vs robust watermarking*; penerapan pada medis.
- Tamper detection & localization: hash blok, checksum, struktur mask.
- Standar DICOM: struktur file, bit-depth 16-bit, metadata pasien, ROI/RONI.
- Ancaman digital forensik medis: deepfake citra medis.

4 jurnal utama (sudah direview mendalam, `01_fase_research.md`) + literatur pendukung 2020+:
1. Garcia et al. (2025) — reversible halftone DICOM, chaotic encryption, localization.
2. Qasim & Ali (2026) — PEE + Canny edge, tanpa localization.
3. Arham et al. (2023) — ROI-based tamper localization & recovery (tanpa kriptografi).
4. Rupa Ch et al. (2024) — IWT-DCT + ECDSA, semi-fragile.

Ditutup tabel **perbandingan dan gap** (reproduksi tabel Bagian G README / `01_fase_research.md` §5–6).

---

## 5. Metodologi (diakhiri diagram alir)

### 5.1 Arsitektur sistem
Loops: Pengirim (proteksi) → media DICOM ber-watermark → Penerima (verifikasi & recovery).

### 5.2 Segmentasi ROI/RONI
- ROI = piksel `> 0` (MRI nyaris tanpa background: ROI 99,6–99,8%); strip 16 baris bawah = RONI untuk side-channel params (LSB).

### 5.3 Teknik reversible: PEE-HS checkerboard multiround
- Checkerboard: piksel (genap, genap) dengan i,j ≥ 2 di-embed; prediksi MED dari tetangga (ganjil) yang tidak pernah di-embedkan → prediksi stabil.
- Per round: peak (e0) histogram error, shift band ±1; multiround (`MAX_ROUNDS=16`) menaikkan kapasitas.
- Parameter tiap round (peak, z, direction, n_bits) → JSON → LSB strip RONI (side-channel self-contained).
- Alasan keputusan: HS global gagal (histogram MRI padat → kapasitas 0), DE overflow (butuh location map). (Lihat D-1.)

### 5.4 Payload & enkripsi AES
- Payload MACRO: `RPEE01` + block(1B) + hash_bits(1B) + n_blocks(2B) + metadata_digest(32B SHA-256) + hash blok (16 bit per blok 16×16).
- Enkripsi **AES-256-CBC** + PKCS7, kunci dari passphrase via **PBKDF2 (200k iterasi)**; IV/salt self-contained (MAGIC+salt+iv+ciphertext) → tidak perlu pembawa IV terpisah.
- Payment integrity: digest SHA-256 metadata.

### 5.5 Tamper detection & localization
- Hash blok 16×16 dihitung dari bit stabil (`img >> 1`), disisipkan via PEE.
- Verifikasi: hitung ulang hash → bandingkan → mask tamper; recovery lossless bila tidak ditamper.

### 5.6 Lapisan keamanan kedua (opsional)
- AES seluruh file `.dcm` (lapisan transport) + AES payload di dalam watermark (dua lapis, tetap dipertahankan).

### 5.7 Skenario & metrik evaluasi
- Skenario: tamper piksel tunggal / blok kecil / crop area / modifikasi metadata / *watermark removal*; kunci salah.
- Metrik: PSNR watermarking, PSNR recovery (=∞), SSIM, BER, akurasi deteksi, presisi lokalisasi (TP/FP), runtime embed + verify.

---

## 6. Hasil dan Analisis

> Angka di bawah dihasilkan ulang oleh `evaluation\journal_eval.py` (24 slice
> BrainTumorMRI, jalur AES penuh; 8 slice × 4 skenario tamper × 2 jalur).
> Data mentah: `evaluation/journal_results.json` + `journal_quality_slice.csv`.

### 6.1 Kualitas citra & reversibilitas (24 slice MRI BrainTumorMRI)

| Metrik | Nilai |
|---|---|
| PSNR setelah embedding (16-bit) | 83,72 – 90,37 dB (mean 86,35) |
| SSIM setelah embedding | 0,999992 – 0,999998 (mean 0,999995) |
| Recovery region diagnostik | **eksak 24/24** (`np.array_equal`), PSNR = ∞, BER = 0 |
| SSIM recovery (region) | 1,0 (semua slice) |
| PSNR recovery (citra utuh) | 114,6 – 117,7 dB — bukan ∞ karena strip RONI 16 baris (LSB side-channel) bersifat lossy (didokumentasikan) |
| Kapasitas payload terpakai | 10.144 bit/slice (hash blok 9.504 bit + header 336 + overhead AES 304) |
| Kapasitas riil (zero-payload estimate) | 12 round: 27,4 – 51,6 kbit (mean 36,1) — outer bound 16 round: 28,4 – 52,9 kbit |
| Runtime embed+verify | 0,197 – 0,344 s (mean 0,279) |
| Verifikasi + recovery | 24/24 slice OK |

### 6.2 Hasil pembanding teknik (5A)
| Teknik | Hasil |
|---|---|
| HS global | gagal (histogram padat → kapasitas 0) |
| DE | gagal (overflow) |
| PEE-HS multiround | PASS: PSNR 84–105 dB, BER 0, eksak |

### 6.3 Deteksi & lokalisasi tamper (8 slice × 4 ukuran tamper × 2 jalur)

**Detection rate: 100% (32/32 kombinasi) pada kedua jalur** — tamper sekecil
1 piksel maupun sebesar 48×48 selalu terdeteksi (piksel berubah atau payload gagal
dibaca), tanpa tabel FP pada citra utuh (jalur bersih 24/24, mask kosong).

| Skenario | Jalur | Deteksi | Lokalisasi tersedia | Prec | Rec | F1 | IoU | FPR |
|---|---|---|---|---|---|---|---|---|
| 1 px | tanpa AES | 8/8 | 8/8 (100%) | 0,877 | 1,0 | 0,879 | 0,877 | 0,012 |
| 1 px | AES | 8/8 | 7/8 (87,5%) | 1,0 | 1,0 | 1,0 | 1,0 | 0,0 |
| 8×8 | tanpa AES | 8/8 | 8/8 (100%) | 0,132 | 1,0 | 0,139 | 0,132 | 0,413 |
| 8×8 | AES | 8/8 | 3/8 (37,5%) | 0,342 | 1,0 | 0,351 | 0,342 | 0,123 |
| 16×16 | tanpa AES | 8/8 | 7/8 (87,5%) | 0,003 | 1,0 | 0,007 | 0,003 | 0,535 |
| 16×16 | AES | 8/8 | 0/8 (0%) | — | — | — | — | — |
| 48×48 | tanpa AES | 8/8 | 8/8 (100%) | 0,018 | 1,0 | 0,035 | 0,018 | 0,812 |
| 48×48 | AES | 8/8 | 0/8 (0%) | — | — | — | — | — |

Interpolasi: recall lokalisasi selalu 1,0 (semua blok sebenarnya yang ditamper
tertandai). Presisi & IoU menurun seiring makin besarnya tamper karena kerusakan
bitstream PEE memperlebar mask (plain) atau menghancurkan payload (AES).
Catatan keamanan: kunci AES salah → verifikasi menolak tanpa crash (uji 5C).

### 6.4 Perbandingan kompensasi & runtime
| Item | Nilai |
|---|---|
| Runtime | 0,197 – 0,344 s/slice (embed+verify, 16 round, mean 0,279) |
| Overflow handling | Slice 13: payload 10,1 kbit > kap ±9,9 kbit → MAX_ROUNDS 12→16 selesai |
| Trade-off kualitas | PSNR(wm) 83,7–90,4 dB, SSIM(wm) ≥ 0,99999 → di bawah ambang gangguan diagnostik |

### 6.5 Perbandingan dengan paper acuan
| Aspek | Paper 1 (Mosco-Garcia 2025) | Paper 2 (Qasim & Ali 2026) | Paper 3 (Arham dkk.) | Paper 4 (Rupa Ch 2024) | **Usulan** |
|---|---|---|---|---|---|
| Reversible | Ya (halftone) | Ya (PEE) | Ya | Tidak | **Ya (PEE-HS multiround)** |
| Kriptografi payload | Chaotic | MD5 | Hash | SHA-256+ECDSA | **AES-256-CBC (PBKDF2)** |
| Tamper localization | Ya (FPR 1,2%) | Tidak | Ya | Tidak | **Ya (deteksi 100%; lokalisasi presisi pd tamper kecil)** |
| PSNR watermarking | ~96 dB (16-bit) | ~97 dB | tinggi | 68,67 dB | **83,7–90,4 dB** |
| SSIM watermarking | 0,96 (kap 90%) | ~0,99999 | tinggi | 0,98 | **0,99999+** |
| Recovery eksak | PSNR 67,5 dB | PSNR ∞ / BER 0 | Ya | Tidak | **PSNR ∞ / BER 0 (region)** |
| Runtime | 93 s (embed) | tidak dilaporkan | tidak dilaporkan | 2,16 s / 1,03 s | **≤0,35 s (embed+verify)** |
| Dataset | multi (TCIA) | 12 citra | multi | MRI Brain | **24 slice MRI** (CT/CR: lanjutan) |

---

## 7. Diskusi

- **Kontribusi utama vs gap:** AES + reversible + localization dalam satu framework; kualitas sangat tinggi (recover lossless) → aman untuk diagnostik.
- **Bukti kualitas kini kuantitatif:** PSNR(wm) 83,7–90,4 dB dan SSIM(wm) 0,99999+ (sebelumnya SSIM tidak dilaporkan). Recovery region eksak (PSNR ∞, BER 0, SSIM 1,0) pada 24/24 slice; PSNR recovery citra utuh ±115 dB karena strip RONI LSB — ditulis eksplisit agar tidak terkesan mengklaim lebih.
- **Trade-off enkripsi vs lokalisasi (terukur):** deteksi 100% di semua skenario. Lokalisasi presisi terbaik pada tamper kecil tanpa AES (1 px: IoU 0,877; 1 px AES: IoU 1,0 bila tersedia). Makin besar tamper → kerusakan bitstream PEE memperlebar mask (plain, FPR naik hingga 0,81) atau menghancurkan payload (AES, mask kosong). Direkomendasikan pelaporan dua jalur terpisah: (i) integrity check selalu aktif; (ii) lokalisasi presisi = tambahan yang optimal pada tamper kecil / mode tanpa enkripsi.
- **Kapasitas riil:** payload terpakai 10,1 kbit; outer bound 16 round = 28,4–52,9 kbit; utilization riil multiround ±30–50% estimasi "zero-payload".
- **Batasan dataset:** single-modality (MR). Evaluasi multi-slice = studi eksperimen; klaim multi-modality menunggu dataset CT/CR publik (TCIA).
- **Klaim reversible:** didukung bukti array identik (region) + BER 0; bedakan klaim (i) reversible+recovery dan (ii) confidentiality AES.
- **Keterbandingan:** implementasi Python + pustaka standar (numpy/scipy/pydicom/cryptography) → mudah direproduksi; skrip evaluasi disertakan (`evaluation/journal_eval.py`).

### 7.1 Kelebihan (Strengths)

1. **Kombinasi keamanan lengkap dalam satu jaluar:** kriptografi modern (AES-256-CBC + PBKDF2) untuk kerahasiaan payload, hash blok untuk integritas, *reversible watermarking* untuk mempertahankan kualitas diagnostik — kombinasi yang belum ada pada keempat paper pembanding (semuanya menghindari AES modern dan/atau belum punya lokalisasi).
2. **Reversibilitas terbukti eksperimental:** recovery region diagnostik eksak (PSNR ∞, BER 0, SSIM 1,0) pada 24/24 slice, bukan sekadar klaim.
3. **Kualitas implementasi tanpa training:** murni berbasis aturan matematis/bit (PEE-HS + hash + AES), tanpa deep learning → ringan, instan per-file (≤0,35 s), mudah direproduksi.
4. **Deteksi kuat dan bebas false positive:** 100% skenario tamper terdeteksi (termasuk 1 piksel), dan jalur bersih tidak memunculkan mask/FP.
5. **Self-contained:** parameter round & IV/salt payload terbungkus di dalam citra (side-channel strip RONI + ciphertext AES) → tanpa kebergantungan penyimpanan kunci/parameter eksternal.
6. **Runtime sangat rendah** dibanding acuan (≤0,35 s vs 93 s Paper 1; 2,16 s Paper 4) dan **SSIM embedding ≥ 0,99999** (> Paper 4 0,98).

### 7.2 Keterbatasan (Limitations)

1. **Lokalisasi presisi menurun pada tamper besar:** kerusakan bitstream PEE memperlebar mask (jalur plain, FPR hingga 0,81) dan menghancurkan payload saat terenkripsi AES (mask kosong) — lokalisasi presisi optimal hanya pada tamper kecil/sedang.
2. **Side-channel strip 16 baris RONI bersifat lossy (LSB):** bagian ini tidak termasuk grid hash, sehingga recovery *citra utuh* PSNR ±115 dB (bukan ∞); hanya region diagnostik yang benar-benar eksak.
3. **Single-modality dataset:** evaluasi hanya pada MRI BrainTumorMRI (24 slice); klaim multi-modality belum dapat didukung sampai dataset CT/CR (TCIA) diuji (gap D-6/5E).
4. **Kapasitas riil multiround terbatas** (±30–50% estimasi "zero-payload"): membatasi besar payload (mis. recovery watermark penuh untuk 5H — status opsional).
5. **Tidak robust terhadap operasi normal** (kompresi JPEG, noise, filter) karena sifat fragile — sesuai karakteristik, dibatasi untuk penyimpanan/transmisi aman tanpa transformasi.
6. **Belum ada analisis frozen hardware & multi-centre** (statistik variansi antar perangkat/PACS belum disediakan).
7. **AES-CBC tanpa otentikasi** (GCM opsional): integritas payload ditanggung oleh hash blok yang disisipkan, bukan oleh mode ciphertext — dicatat sebagai batasan desain.

---

## 8. Kesimpulan

- Skema PEE-HS multiround + payload AES-256-CBC berhasil memenuhi kerahasiaan + integritas + reversibilitas pada DICOM 16-bit.
- Recovery region lossless (PSNR ∞, BER 0, SSIM 1,0); kualitas watermarking tinggi (PSNR ≥ 83,7 dB, SSIM ≥ 0,99999); deteksi tamper 100% pada semua skenario uji.
- Saran lanjut: dataset multi-modality (CT/CR), tamper recovery penuh (5H), evaluasi terhadap kompresi/transmisi.

---

## 9. Daftar Pustaka (kerangka; lengkapi 15–20, gaya IEEE/APA sesuai target)

- NIST FIPS PUB 197 — Advanced Encryption Standard.
- NIST SP 800-38A — mode operasi (CBC, dll.).
- DICOM Standard (NEMA PS3).
- Mosco-Garcia, M., Cedillo-Hernandez, A., & Shouno, H. (2025). Data hiding for clinical information in DICOM images via reversible halftone fragile watermarking.
- Qasim, A. F., & Ali, A. H. (2026). Fragile reversible watermarking … PEE and Canny edge detection.
- Arham, A., Adji, T. B., Alfarozi, S. A. I., & Nugroho, H. A. — Reversible watermarking for medical images using ROI-based tamper localization and recovery (venue/tahun diisi).
- Ch, R., Vivek K, N., Srivastava, G., & Gadekallu, T. R. (2024). Semi-fragile authentication watermarking … IWT-DCT and ECDSA. IJCCE, 5, 78–87.
- Tian, J. — Difference expansion (2003).
- Ni, Z., et al. — Histogram shifting (2006).
- Thodi & Rodriguez — Prediction-error expansion (2007).
- + literatur medical image encryption & deepfake detection 2020+ (isi saat penulisan).

---

## 10. Rencana Penulisan (task Fase 6)

1. [ ] Finalisasi judul (pilih 1) + abstrak (alihkan ke template jurnal target).
2. [ ] Lengkapi tinjauan pustaka → 15–20 sumber (lengkapi metadata).
3. [ ] Re-run baseline angka & buat grafik/tabel final (PSNR, SSIM, BER, runtime, akurasi).
4. [ ] (Opsional, worth it) Tambah SSIM watermarking & tabel CSV per slice; cek keberadaan dataset CT/CR untuk memperkuat klaim multi-modality.
5. [ ] Susun naskah sesuai template jurnal Sinta 3 target; revisi bersama pembimbing.