# 07 — Handoff Riwayat Sesi (untuk lanjutan di chat baru)

> Ditulis: Sun Sep 20 2026 (sesi 5). Tujuan: dokumentasi ringkas seluruh progres agar
> sesi berikutnya (dengan token segar) bisa langsung lanjut tanpa mengulang eksplorasi.

## 1. Ringkasan proyek

- **Topik tugas akhir Kriptografi:** *Reversible ROI watermarking + payload terenkripsi AES* pada citra medis DICOM, dengan deteksi & lokalisasi tamper. Target publikasi: **jurnal Sinta 3** (BUKAN Scopus).
- **Scope yang disepakati:** AES + reversible ROI watermarking + tamper detection & localization. **Tamper recovery = NONAWAJIB** (5H hanya bila waktu cukup).
- **Path proyek:** `D:\A11.2025.16609\SEMESTER 3\KRIPTOGRAFI\project_medical_dicom_watermark\`
- **OS/shell:** Windows, PowerShell 5.1. Python 3.10.6 (laragon), numpy 1.26.4, scipy 1.15.3, pydicom 3.0.2, cryptography 46.0.7 (Flask/Pillow untuk GUI). Run test: `python tests\<nama>.py`.

## 2. Keputusan desain (D-1..D-6)

| Keputusan | Hasil |
|---|---|
| **D-1 Teknik reversible** | **PEE-HS checkerboard multiround** (Prediction Error Expansion + Histogram Shifting). Ditolak: HS global (MRI histogram padat → kap 0), DE (overflow pada MRI → butuh location map). Checkerboard = piksel (genap,genap) i,j≥2, prediksi MED dari tetangga yang tak pernah di-embed → stabil. |
| **D-2 Region embedding** | Payload di seluruh region citra (kecuali strip side-channel); side-channel params di **strip 16 baris bawah (RONI)** via LSB. ROI/RONI segmentation sederhana: `pixel > 0`. MRI nyaris tanpa background (ROI 99,6–99,8%). |
| **D-3 MACRO payload** | Payload = `RPEE01` + block(1B)+hash_bits(1B)+n_blocks(2B) + metadata_digest(32B) + hash blok. **Blok 16×16, hash 16-bit**. Payload terpakai 9.504 bit hash + header → **10.144 bit** setelah AES (overhead 304 bit). |
| **D-4 Mode AES** | **AES-256-CBC** (reuse `crypto/aes.py`, PKCS7, PBKDF2 200k iter). IV/salt self-contained (MAGIC+salt+iv+ct). GCM opsional (catatan: CBC tanpa otentikasi — integritas ditanggung hash blok). |
| **D-5 Lapisan file** | Pertahankan **AES seluruh file** (.krip) + AES payload di dalam watermark. Dua lapis, diuji. |
| **D-6 Dataset** | MRI BrainTumorMRI (24 slice). **GAP: modalitas kedua (CT/CR) belum ada** — klaim multi-modality butuh dataset tambahan (TCIA). |

## 3. Riwayat kerja

### Fase 1–5 (dari sesi 1, selesai & tetap hijau)
- **01_fase_research.md**: review 4 jurnal + gap analysis + rumusan masalah Sinta 3. Paper 3 kini punya penulis resmi: **Arham, Adji, Alfarozi, & Nugroho**.
- **Fase 2–4 (baseline LSB):** `crypto/aes.py`, `crypto/watermark.py`, `crypto/tamper.py` (jalur lama), `crypto/dicom.py`, `app.py` + Flask GUI.
- **Fase 5 (reversible):** `crypto/reversible.py` (PEE-HS multiround), `crypto/tamper.py` (jalur `protect_image_rev`/`verify_image_rev`, REV_MAGIC=`RPEE01`, PARAM_STRIP=16, MAX_ROUNDS=16), integrasi DICOM 16-bit, payload AES opsi `passphrase`, evaluasi 24 slice MRI, GUI reversible. Detail lengkap ada di `05_plan_reversible.md`.

### Sesi 2 (BARU) — memperkuat bukti jurnal
1. **Unifikasi penulis Paper 3** di `outline_journal.md` → Arham dkk. (gap, tinjauan, daftar pustaka).
2. **`crypto/metrics.py` (BARU):** `ssim` (Gaussian, scipy.ndimage; data_range auto utk uint8/uint16) + `block_confusion` (TP/TN/FP/FN, precision, recall, F1, accuracy, FPR, localization_iou pada grid blok) + `summarize_confusion`. Precision = 1.0 bila tak ada prediksi positif (kasus bersih).
3. **`tests/test_metrics.py` (BARU):** pass **14/14** (SSIM identik/noise; confusion math incl. edge case bersih).
4. **`evaluation/journal_eval.py` (BARU):** evaluasi otomatis 2 fase:
   - Fase A: 24 slice jalur AES → PSNR/SSIM wm, PSNR/SSIM recovery, BER, exact, capacity, runtime.
   - Fase B: 8 slice × [1px, 8×8, 16×16, 48×48] × [plain, AES] → deteksi + metrik lokalisasi blok.
   - Output: `evaluation/journal_results.json` + `evaluation/journal_quality_slice.csv`.
   - Run: `python evaluation\journal_eval.py [n_slice_fase_b]` (default 8).
5. **`outline_journal.md` (UPDATE):** isi hasil kuantitatif final, tabel deteksi/lokalisasi, **tabel perbandingan baseline 4 paper**, subseksi **7.1 Kelebihan** & **7.2 Keterbatasan**, catatan analisis risiko di bagian Diskusi.

## 4. Hasil uji (semua hijau)

| Test | Hasil |
|---|---|
| `tests\test_core.py` | 8/8 (jalur LSB lama tidak rusak) |
| `tests\test_dicom.py` | 21/21 (LSB 9 + reversible DICOM) |
| `tests\test_reversible.py` | 3/3 (+2 SKIP informatif flat16/smooth16 kap 0) |
| `tests\test_reversible_tamper.py` | 15/15 |
| `tests\test_metrics.py` | 14/14 |
| `tests\test_multi_slice.py` | 24/24 slice, PSNR(wm) 83,63–90,43 dB |
| `tests\test_app.py` | 12/12 (Flask smoke, dari sesi 1) |

## 5. Hasil evaluasi jurnal (terukur ulang, `journal_results.json`)

**Fase A — kualitas & reversibilitas (24 slice, jalur AES):**
- PSNR(wm) 83,72–90,37 dB (mean 86,35); **SSIM(wm) 0,999992–0,999998** (mean 0,999995) — SSIM kini dilaporkan.
- Recovery **region diagnostik eksak 24/24** (`np.array_equal`), PSNR region = ∞, BER = 0, SSIM(region) = 1,0.
- PSNR recovery **citra utuh** = 114,6–117,7 dB (BUKAN ∞ — strip RONI 16 baris LSB lossy ≈ 3,6% piksel). Ditulis eksplisit.
- Kapasitas: terpakai 10.144 bit/slice; zero-payload estimate 12 round 27,4–51,6 kbit, 16 round 28,4–52,9 kbit.
- Runtime embed+verify 0,197–0,344 s (mean 0,279).

**Fase B — deteksi & lokalisasi (8 slice × 4 skenario × 2 jalur):**
- **Detection rate 100% (32/32)** semua kombinasi; jalur bersih tanpa mask/FP.
- Tabel lokalisasi (Prec/Rec/F1/IoU/FPR saat tersedia):

| Skenario | Jalur | Detection | Localized | Prec | Rec | F1 | IoU | FPR |
|---|---|---|---|---|---|---|---|---|
| 1 px | plain | 8/8 | 8/8 | 0,877 | 1,0 | 0,879 | 0,877 | 0,012 |
| 1 px | AES | 8/8 | 7/8 | 1,0 | 1,0 | 1,0 | 1,0 | 0,0 |
| 8×8 | plain | 8/8 | 8/8 | 0,132 | 1,0 | 0,139 | 0,132 | 0,413 |
| 8×8 | AES | 8/8 | 3/8 | 0,342 | 1,0 | 0,351 | 0,342 | 0,123 |
| 16×16 | plain | 8/8 | 7/8 | 0,003 | 1,0 | 0,007 | 0,003 | 0,535 |
| 16×16 | AES | 8/8 | 0/8 | — | — | — | — | — |
| 48×48 | plain | 8/8 | 8/8 | 0,018 | 1,0 | 0,035 | 0,018 | 0,812 |
| 48×48 | AES | 8/8 | 0/8 | — | — | — | — | — |

- **Interpolasi penting:** lokalisasi presisi hanya optimal untuk tamper kecil; tamper besar melebarkan mask (plain, IoU → 0,02) atau menghilangkan lokalisasi (AES, mask kosong 0%). Rec selalu 1,0.

## 6. Batasan & catatan jurnal (penting, jujur)

1. **Lokalisasi presisi = titik lemah utama.** Rata-rata IoU ±0,26 (plain) / ±0,34 (AES saat tersedia); vs 1px=0,88. Untuk Sinta 3 → EMPAT pilihan: (a) reframe klaim jadi "deteksi + indikasi area kasar" + dokumentasi trade-off AES; atau (b) interleaving/mapping hash antar-blok (Paper 3 Arham) untuk lokalisasi robust — butuh cek ulang kapasitas & re-run test. **Rekomendasi: (a) cukup.**
2. **Recovery utuh ≠ ∞:** strip RONI 16 baris (LSB, di luar grid hash) lossy ≈ 3,6% piksel. Region diagnostik baru yang benar-benar eksak.
3. **Single-modality:** hanya MRI (ROI 99,6–99,8%). Evaluasi multi-slice = studi eksperimen; CT/CR (TCIA) = gap D-6/5E.
4. **Kapasitas riil multiround ±30–50%** estimasi zero-payload (bit-1 menurunkan frekuensi peak round berikutnya).
5. **Klaim reversible & confidentiality dipisah:** (i) reversible+recovery = bukti eksak region; (ii) confidentiality = AES-256-CBC (kunci salah → ditolak).
6. **Fragile → tidak robust** thd kompresi/noise/filter (sesuai sifat).
7. **AES-CBC tanpa otentikasi** (GCM opsional): integritas ditanggung hash blok yang disisipkan.

## 7. Status file (sesi 2)

- `crypto/metrics.py` **BARU** — SSIM, block_confusion, summarize_confusion.
- `tests/test_metrics.py` **BARU** — 14/14.
- `evaluation/journal_eval.py` **BARU** — evaluasi Fase A+B, output JSON+CSV.
- `evaluation/journal_results.json`, `evaluation/journal_quality_slice.csv` **BARU** — data mentah hasil.
- `outline_journal.md` **DIPERBARUI** — angka final, tabel perbandingan baseline, 7.1 Kelebihan, 7.2 Keterbatasan, Paper 3 = Arham dkk.
- Tidak ada perubahan pada `crypto/*` inti (AES/reversible/tamper/dicom) — hanya penambahan modul metrik & evaluasi.

## 8. Langkah tersisa (roadmap)

1. **Reframe klaim lokalisasi di outline** (opsi a) ATAU implementasi interleaving hash (opsi b) bila pembimbing meminta lokalisasi kuat.
2. **D-6:** dapatkan dataset DICOM kedua (CT/CR/X-ray TCIA) → uji multi-modality (bandingkan kapasitas/PSNR/BER/SSIM).
3. **5H opsional:** tamper recovery penuh — hanya bila waktu cukup (butuh kapasitas besar).
4. **Fase 6 — Penulisan jurnal:** susun naskah penuh dari `outline_journal.md`; lengkapi tinjauan pustaka (15–20 sumber), grafik/tabel final berbasis `journal_quality_slice.csv`, revisi pembimbing, submit.

## 9. Berkas pustaka paling berguna untuk lanjut

- `outline_journal.md` — OUTLINE + hasil final + kelebihan/keterbatasan (baca dulu).
- `05_plan_reversible.md` — rencana + keputusan + hasil Fase 5 (gate/risiko).
- `evaluation/journal_eval.py` + `journal_results.json` — bukti kuantitatif & cara re-run.
- `crypto/metrics.py` — SSIM + metrik lokalisasi (hasil evaluasi).
- `crypto/reversible.py` — inti teknik; `crypto/tamper.py` — jalur reversible + AES.
- `tests/test_multi_slice.py` — template evaluasi (ganti dataset utk D-6).
- `01_fase_research.md` bagian 6 — gap/rumusan masalah; Paper 3 penulis Arham dkk.