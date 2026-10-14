# Reversible Medical DICOM Watermarking & Enkripsi Kriptografis AES-256

Sistem Proteksi Ganda Citra Medis DICOM 16-Bit menggabungkan **Reversible Watermarking berbasis Multi-Round Prediction Error Expansion - Histogram Shifting (PEE-HS)** dan **Enkripsi Kriptografis AES-256-CBC**.

Sistem ini menjamin:
1. **Kerahasiaan Medis (*Confidentiality*):** Perlindungan berkas dan muatan tanda tangan menggunakan enkripsi standar militer AES-256-CBC dengan derivasi kunci PBKDF2 (200.000 iterasi).
2. **Integritas Spasial (*Integrity & Tamper Localization*):** Deteksi dan lokalisasi manipulasi spasial presisi berbasis grid blok $16 \times 16$ piksel serta verifikasi keaslian metadata pasien via digest SHA-256.
3. **Pemulihan Eksak Tanpa Cacat (*100% Bit-Exact Lossless Recovery*):** Wilayah diagnostik anatomi otak pulih sempurna tanpa distorsi biner ($\text{PSNR} = \infty, \text{BER} = 0, \text{SSIM} = 1,0$), memenuhi standar ketat teleradiologi klinis.

Target Publikasi: **Jurnal Ilmiah Nasional Terakreditasi Sinta 3 / Prosiding Internasional IEEE**.

---

## 1. Ringkasan Eksekutif & Kontribusi Ilmiah

- **Judul Jurnal Resmi:**  
  *"Reversible Medical DICOM Watermarking berbasis Multi-Round Prediction Error Expansion dan Enkripsi AES-256 untuk Proteksi Integritas serta Kerahasiaan Citra MRI"*
- **Modalitas Eksperimen:**  
  24 slice aksial volume MRI Brain (`BrainTumorMRI`) format DICOM 16-bit (`uint16`, dynamic range 0–1513, dimensi $448 \times 364$ piksel).
- **Zonasi Spasial Citra:**
  - **ROI Diagnostik:** 432 baris teratas ($432 \times 364 = 157.248$ piksel) — diproteksi secara eksak biner 100%.
  - **Strip RONI:** 16 baris terbawah ($16 \times 364 = 5.824$ piksel) — menyimpan parameter kontrol dekompresi PEE via LSB.
- **Kapasitas Payload:**
  Header (80 bit) + Metadata Digest SHA-256 (256 bit) + 594 Hash Blok Spasial (9.504 bit) = 9.840 bit plaintext $\rightarrow$ **10.144 bit ciphertext AES-256**.

## 2. Hasil Evaluasi Kuantitatif Komprehensif

Pengujian kuantitatif dilakukan pada seluruh 24 slice volume aksial MRI Brain (`BrainTumorMRI`) format DICOM 16-bit. Seluruh metrik imperseptibilitas, integritas, kualitas rekonstruksi, dan sifat statistik dievaluasi secara otomatis (tersimpan di [lecturer_metrics_results.json](evaluation/lecturer_metrics_results.json) dan dilaporkan lengkap di [laporan_evaluasi_metrik_dosen.md](laporan_evaluasi_metrik_dosen.md)):

| Kategori Evaluasi | Metrik | Target Teori | Hasil Terukur (24 Slice MRI) | Status |
|---|---|---|---|:---:|
| **Rekonstruksi ROI Medis** | **Recovery PSNR** | $\infty$ (Tak-Hingga) | **$\infty$ (Bit-Exact Eksak 24/24)** | **Tercapai** |
| | **Recovery SSIM** | 1,000000 | **1,000000** | **Tercapai** |
| | **Recovery BER** | 0,00000000 | **0,00000000 (0 bit salah)** | **Tercapai** |
| | **Normalized Correlation (NC)** | 1,000000 | **1,000000** | **Tercapai** |
| | **Normalized Cross-Correlation (NCC)** | 1,000000 | **1,000000** | **Tercapai** |
| **Imperseptibilitas Watermark** | **Watermarked PSNR (16-bit dynamic)** | $\ge 60$ dB | **86,18 ± 1,97 dB** (83,72 – 90,37 dB) | **Tercapai** |
| | **Watermarked PSNR (12-bit stored)** | $\ge 50$ dB | **62,10 ± 1,97 dB** (59,64 – 66,29 dB) | **Tercapai** |
| | **Mean Squared Error (MSE 16-bit)** | Mendekati 0 | **11,36 ± 4,52** (4,32 – 19,95) | **Tercapai** |
| | **Mean Squared Error (MSE 12-bit)** | Mendekati 0 | **0,044 ± 0,018** (0,017 – 0,078) | **Tercapai** |
| | **SSIM Citra Ter-watermark** | $\ge 0,999$ | **0,999995 ± 0,000002** | **Tercapai** |
| | **NPCR (Watermarked vs Asli)** | Sangat rendah | **14,37 ± 0,39%** (imperceptible) | **Tercapai** |
| | **UACI (Watermarked vs Asli)** | Sangat rendah | **0,0018 ± 0,0004%** (tak kasat mata) | **Tercapai** |
| **Karakteristik Statistik** | **Entropi Informasi Citra Asli** | Identik | **4,7071 ± 0,3816** bit/piksel | **Tercapai** |
| | **Entropi Citra Ter-watermark** | $\Delta H \le 0,001$ | **4,7066 ± 0,3815** bit/piksel ($\Delta H = 0,0005$) | **Tercapai** |
| | **Chi-Square Uniformity Test ($X^2$)** | $p > 0,05$ | **$p = 1,0000$** (Distribusi identik) | **Tercapai** |
| **Keamanan & Komputasi** | **Deteksi Manipulasi (Tamper)** | 100% | **100% (32/32 skenario serangan)** | **Tercapai** |
| | **Waktu Total (Embed + Verify)** | $\le 1,0$ detik | **0,279 detik per slice** | **Tercapai** |

---

## 3. Arsitektur Alur Kerja Sistem

Alur kerja dirancang dalam dua kolom paralel standar IEEE/Sinta (dapat dilihat pada diagram resmi di [journal_flow_diagram.md](journal_flow_diagram.md)):

```
[SISI PENGIRIM: PROTEKSI]
DICOM Asli (448x364)
   │
   ├─► ROI (432x364) ──► Stabilisasi (>> 1) ──► 594 Hash Blok (9.504b) ──┐
   ├─► Metadata Tag  ──► SHA-256 Digest (256b) ───────────────────────────┼─► Payload (9.840b)
   │                                                                      │        │
   │                                                    Passphrase K ─────┴─► Enkripsi AES-256
   │                                                                               │
   │   ┌─────────────────────── Iterasi Multi-Round (r=1..16) ─────────────────────┤
   │   │ MED Predictor (Checkerboard) ──► Galat e = x - x_hat                      ▼
   │   │ PEE Expansion: e' = 2e + b (peak e0) & Shifting: e' = e +/- 1    Ciphertext (10.144b)
   │   └───────────────────────────────────────────────────────────────────────────┘
   │
   ├─► Parameter JSON PEE ──► Sisip ke LSB 16 Baris Strip RONI
   ▼
Citra DICOM Ter-watermark (PSNR ~86 dB, SSIM 0,999995) ──► Transmisi Jaringan PACS

========================================================================================

[SISI PENERIMA: VERIFIKASI & PEMULIHAN]
Penerimaan Berkas DICOM Terproteksi
   │
   ├─► Baca Parameter JSON dari LSB Strip RONI
   │
   ├─► Inverse PEE-HS Multi-Round (Mundur r=16..1)
   │     ├─► Ekstraksi Bit Ciphertext: b = e' mod 2
   │     ├─► Pulihkan Galat Asli: e = floor(e' / 2)
   │     └─► Pulihkan Piksel Asli: x = x_hat + e  ===> ROI Pulih 100% Bit-Exact!
   │
   ├─► Dekripsi AES-256-CBC (Passphrase Dokter) ──► Parsing Hash Asli & Digest
   │
   ├─► Hitung Ulang 594 Hash Blok (rec >> 1) & Hash Metadata Header
   ▼
Pencocokan Integritas:
   ├─► Cocok 100%: Status "VALID & OTENTIK" (PSNR = inf, BER = 0, SSIM = 1.0)
   └─► Ada Selisih: Status "TAMPER DETECTED" ──► Tampilkan Mask Spasial Merah 16x16
```

---

## 4. Struktur Direktori Repositori

```
medical_dicom_watermark/
├── README.md                          # Dokumentasi utama proyek
├── outline_journal.md                 # Naskah lengkap jurnal ilmiah (Sinta 3/IEEE)
├── journal_flow_diagram.md            # Diagram alur lengkap Mermaid & spesifikasi matematis
├── journal_guide.md                   # Panduan naratif presentasi & tanya-jawab dosen
├── laporan_evaluasi_metrik_dosen.md   # Laporan evaluasi komprehensif 10 metrik dosen
├── katalog_visualisasi_riset.md       # Katalog lengkap visualisasi & grafik publikasi
├── app.py                             # Aplikasi web interaktif Flask dengan multi-histogram
├── requirements.txt                   # Dependensi pustaka Python
│
├── crypto/                            # Modul algoritma kriptografi & watermarking
│   ├── reversible.py                  # PEE-HS checkerboard multi-round + integer transform
│   ├── metrics.py                     # SSIM Gaussian, confusion matrix, & IoU lokalisasi
│   ├── aes.py                         # AES-256-CBC + derivasi kunci PBKDF2 (200k iterasi)
│   ├── tamper.py                      # Integrasi proteksi reversible, deteksi, & masking
│   ├── watermark.py                   # Utilitas manipulasi LSB & bitstream
│   ├── dicom.py                       # Parsing DICOM pydicom, windowing, & ekspor
│   └── histogram.py                   # Pembangkit histogram visual & analisis distribusi
│
├── figures/                           # Berkas visualisasi & grafik publikasi 300 DPI
│   ├── diagram_alur_jurnal.png        # Flowchart jurnal resolusi tinggi 300 DPI
│   ├── diagram_alur_jurnal.pdf        # Flowchart vektor PDF untuk naskah LaTeX/Word
│   ├── peta_selisih_residual.png      # Visualisasi selisih residual absolut citra (x100)
│   ├── korelasi_piksel_spasial.png    # Scatter plot korelasi pasangan piksel bertetangga
│   ├── histogram_galat_prediksi_pee.png # Distribusi galat prediksi MED checkerboard
│   ├── distribusi_metrik_24slice.png  # Boxplot sebaran metrik PSNR, SSIM, MSE, NPCR
│   ├── histogram_panel_lengkap.png    # Komparasi 4-panel histogram (Asli, Enkripsi, Dekripsi, Cipher)
│   ├── histogram_komparasi_overlay.png# Overlay kurva densitas kontur sebelum vs sesudah
│   ├── perbandingan_16bit_windowing.png # Bukti visual windowing radiologi standar
│   └── perbandingan_tamper_visual.png # Visualisasi lokalisasi tamper grid 16x16
│
├── evaluation/                        # Modul pengujian, skrip analisis, & data mentah
│   ├── measure_lecturer_metrics.py    # Skrip pengukuran otomatis 10 metrik dosen
│   ├── generate_advanced_visualizations.py # Skrip pembangkit seluruh visualisasi 300 DPI
│   ├── generate_markdown_report.py    # Skrip generator laporan evaluasi metrik
│   ├── generate_journal_figures.py    # Skrip generator grafik performa tamper
│   ├── generate_journal_flowchart.py  # Skrip pembangkit flowchart dua kolom IEEE
│   ├── journal_eval.py                # Skrip evaluasi eksperimen Fase A & Fase B
│   ├── lecturer_metrics_results.json  # Data mentah JSON pengukuran 10 metrik (24 slice)
│   ├── journal_results.json           # Rekapitulasi metrik reversibilitas & tamper
│   └── journal_quality_slice.csv      # Tabel metrik per slice (PSNR, SSIM, kapasitas)
│
├── dataset/                           # Dataset citra medis DICOM
│   └── BrainTumorMRI/                 # 24 slice aksial MRI T2 (IM-0001-0001 s.d. 0024)
│
├── templates/                         # Antarmuka web Flask (Jinja2)
│   ├── base.html                      # Layout dasar & navigasi
│   ├── index.html                     # Beranda: proteksi, verifikasi, & panel histogram
│   ├── algoritma.html                 # Dokumentasi teknis 4 pilar algoritma
│   └── pengujian.html                 # Dashboard pengujian otomatis server
│
├── static/                            # Aset frontend (CSS murni, SVG ikon, JavaScript)
│   ├── css/style.css
│   └── js/main.js
│
└── tests/                             # Suite pengujian unit dan integrasi
    ├── test_reversible_tamper.py      # Uji Reversible PEE-HS & deteksi tamper (15 uji)
    ├── test_metrics.py                # Uji metrik SSIM & confusion matrix (14 uji)
    ├── test_multi_slice.py            # Uji reversibilitas pada seluruh 24 slice MRI
    ├── test_dicom.py                  # Uji integrasi DICOM baseline (21 uji)
    ├── test_core.py                   # Uji prototipe inti baseline (8 uji)
    └── test_app.py                    # Uji endpoint & integrasi Web GUI Flask (12 uji)
```

---

## 5. Cara Menjalankan Sistem

### A. Menjalankan Aplikasi Web Interaktif
Pastikan dependensi terpasang (`pip install -r requirements.txt`), lalu jalankan:
```bash
python app.py
```
Buka browser pada alamat: **`http://127.0.0.1:5000`**

Fitur aplikasi web:
1. **Beranda:** Mengunggah citra DICOM (`.dcm`), memasukkan passphrase, dan mengunduh berkas terproteksi `.krip`. Pada sisi verifikasi, mengunggah `.krip`, memasukkan passphrase, dan melihat visualisasi pemulihan bit-exact serta deteksi manipulasi.
2. **Visualisasi Histogram Interaktif:** Menampilkan komparasi grafis langsung antara **Histogram Citra Asli**, **Histogram Citra Ter-watermark**, **Histogram Citra Pulih**, **Overlay Komparasi**, dan **Distribusi Byte Ciphertext AES-256**.
3. **Algoritma:** Penjelasan interaktif mengenai PEE-HS, MED predictor, AES-256-CBC, dan grid lokalisasi 16x16.
4. **Pengujian:** Menjalankan test suite Python secara live langsung dari browser.

### B. Menjalankan Pengukuran Metrik & Pembangkit Visualisasi

```bash
# 1. Jalankan Pengukuran Otomatis 10 Metrik Dosen (24 Slice MRI):
python evaluation/measure_lecturer_metrics.py

# 2. Pembangkitan Grafik & Visualisasi Publikasi 300 DPI:
python evaluation/generate_advanced_visualizations.py

# 3. Pembangkitan Diagram Alur Publikasi Standar IEEE:
python evaluation/generate_journal_flowchart.py

# 4. Uji Reversible PEE-HS & Tamper Detection (15/15 PASS):
python tests/test_reversible_tamper.py

# 5. Uji Web GUI & Multi-Histogram Rendering (12/12 PASS):
python tests/test_app.py

# 6. Uji Komprehensif Seluruh 24 Slice MRI:
python tests/test_multi_slice.py
```

---

## 6. Riwayat Pengembangan & Dokumentasi Terkait

- [outline_journal.md](outline_journal.md): Naskah lengkap jurnal ilmiah (Sinta 3/IEEE) yang telah memuat 10 metrik evaluasi dosen.
- [laporan_evaluasi_metrik_dosen.md](laporan_evaluasi_metrik_dosen.md): Laporan formal evaluasi 10 metrik untuk dosen pembimbing/penguji.
- [katalog_visualisasi_riset.md](katalog_visualisasi_riset.md): Katalog komprehensif seluruh grafik, diagram alur, dan analisis visual riset.
- [journal_flow_diagram.md](journal_flow_diagram.md): Diagram alur end-to-end, matriks transformasi, dan pembuktian matematis reversibilitas.
- [journal_guide.md](journal_guide.md): Panduan presentasi naratif dan tanya-jawab bimbingan/sidang dosen.
- [01_review_literature.md](01_review_literature.md): Telaah literatur 4 paper pembanding dan analisis research gap.
- [02_prototype.md](02_prototype.md): Dokumentasi pengujian prototipe awal 8-bit sintetis.
- [03_fase_dicom_integration.md](03_fase_dicom_integration.md): Dokumentasi integrasi DICOM 16-bit grayscale awal.
- [04_fase_gui.md](04_fase_gui.md): Dokumentasi pengembangan antarmuka web Flask dan visualisasi histogram.
- [05_plan_reversible.md](05_plan_reversible.md): Rencana implementasi teknis Fase 5 (Reversible Watermarking).