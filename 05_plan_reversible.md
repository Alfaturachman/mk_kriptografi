# Fase 5 — Rencana Implementasi Reversible Watermarking + Payload AES

Dokumen ini adalah **validasi rencana (pre-code)** sebelum eksekusi penuh kode.
Selaras dengan arah penelitian di `01_fase_research.md` (bagian 6):

*Skema reversible watermarking berbasis ROI pada citra DICOM dengan payload terenkripsi AES,
tamper detection + tamper localization, dievaluasi pada dataset DICOM multi-modality.*
Target publikasi: **Sinta 3**, lingkup tugas akhir.

> Prinsip utama: TIDAK mengklaim reversible sebelum benar-benar terimplementasi dan teruji.
> Ceklis di bawah ini adalah syarat *done* sebelum masuk tahap penulisan jurnal.

---

## 1. Kondisi Saat Ini (fondasi yang sudah jadi)

| Modul | Fungsi | Status |
|---|---|---|
| `crypto/aes.py` | AES-256-CBC + PBKDF2 (kunci dari passphrase) | Selesai |
| `crypto/watermark.py` | LSB embed/extract + header `KPGW` | Selesai, **lossy** |
| `crypto/tamper.py` | hash blok SHA-256 + lokalisasi tamper + metadata | Selesai, **lossy** |
| `crypto/dicom.py` | load/save/preview DICOM 16-bit | Selesai |
| `app.py` + templates | Web GUI (proteksi, verifikasi, pengujian) | Selesai |

Gap penting menuju *reversible*:
1. LSB menimpa bit asli → citra tidak bisa dipulihkan sempurna. **Harus diganti/ganti mekanisme.**
2. Payload watermark (hash blok + metadata) belum dienkripsi AES; AES baru melindungi *seluruh file*.
3. Belum ada segmentasi ROI/RONI.
4. Metrik BER dan uji *recovery* (PSNR=∞) belum ada di test suite.

---

## 2. Skema Target (satu gambar besar)

```
PENGIRIM
  metadata DICOM + hash blok
        |
        v
  [A] PAYLOAD  = blok_hash (16 bit/blok) + digest SHA-256 metadata
        |
        v
  [B] AES-ENCRYPT payload (kunci PBKDF2, AES-128/256) + IV   <- kontribusi "payload terenkripsi"
        |
        v
  [C] EMBED REVERSIBLE (histogram shifting / PEE / LSB-saving)
        pada region terproteksi -> citra ber-watermark  (PSNR tinggi, tapi POSSIBLE dikecilkan)
        |
        v
  [D] (opsional) AES seluruh file .dcm (lapisan kedua, reuse aes.py)

PENERIMA
  [E] EKSTRAK payload -> dekripsi AES -> blok_hash + digest
  [F] hitung ulang hash tiap blok -> bandingkan -> tamper detection & localize (mask)
  [G] verifikasi metadata
  [H] REVERSE embed (hapus watermark) -> citra asli kembali  => PSNR = ∞, BER = 0
```

Perubahan inti: **embedding (C) menjadi reversible** dan **payload (A→B) dienkripsi AES**.

---

## 3. Keputusan Desain (wajib diputuskan — checklist)

- [x] **D-1. Teknik reversible** — **DIPUTUSKAN: (b) PEE-HS checkerboard (multiround)** pada 6-Mei-berikutnya. Hasil uji 5A:
  - Teknik (a) HS global **gagal** pada MRI medis: histogram 16-bit padat → kapasitas 0 bit (tidak ada bin kosong).
  - Teknik (c) DE **gagal** pada MRI asli: tidak DE-safe (overflow) → butuh location map.
  - Teknik (b) PEE-HS **PASS** pada MRI 448×364: PSNR 105.80 dB, `exact=True`, BER=0, kapasitas 4.302 bit/round.
  - **Multiround PEE** (lihat 06_.../5A) menambah kapasitas: 12 round = 51.624 bit (6.453 B), PSNR 84-105 dB, `exact=True`, BER=0 → cukup untuk payload tamper 8×8 (~5 kB).
  - Keterbatasan terdokumentasi: butuh ≥1 bin error kosong (citra sangat halus/random murni bisa 0 bit — tidak relevan utk medis).
- [ ] **D-2. Region embedding** — apakah watermak seluruh citra atau **ROI saja** (mis. = piksel non-background / hasil Canny dari Paper 2). RONI dipakai simpan kunci IV / parameter. *(Target riset: ROI.)*
- [ ] **D-3. MACRO payload** — berapa bit per blok (16 bit sekarang) dan di mana IV AES disimpan (header payload / RONI).
- [ ] **D-4. Mode AES** — AES-CBC (reuse) vs AES-GCM (mendapatkan otentikasi payload). Catat: payload sudah punya hash blok untuk autentikasi, jadi CBC cukup; GCM opsional.
- [ ] **D-5. Lapisan enkripsi file** — pertahankan AES seluruh file (lapisan kedua) atau hanya payload? (*Rekomendasi: pertahankan - konkret dan sudah diuji.*)
- [ ] **D-6. Dataset evaluasi** — MRI BrainTumorMRI (sudah ada) + 1 modality tambahan (CT/CR publik berformat DICOM). Target minimal 2 modality untuk klaim multi-modality.

---

## 4. Todo List Eksekusi (urutan penting — jangan loncat)

### 5A — Prototipe reversible (PNG / grayscale sintetis) ✅
- [x] Buat `crypto/reversible.py` dengan fungsi `embed_reversible(img, payload)` dan `extract_reversible(img)` + `reverse_reversible(img)` sesuai teknik D-1. **Realita 5A:** fungsi inti `pee_embed`/`pee_extract`/`pee_reverse` + multiround `pee_embed_multi`/`pee_extract_multi`/`pee_reverse_multi` + referensi `hs_l_*`, `de_*`. Side-channel (`peak`,`z`,`direction` per round) untuk integrasi 5B/5C.
- [x] Uji unit mandiri: embed → extract → reverse mengembalikan citra **harfiah identik** (`np.array_equal`) → MRI `exact=True`.
- [x] Ukur kapasitas payload & PSNR sebelum-reverse pada citra uji → MRI: PSNR 105.80 dB (1 round) / 84.18 dB (12 round), BER=0, kap 4.302 bit/round.
- [x] Bandingkan teknik (a) vs (c) → putuskan D-1 (hasil tercatat di atas).

### 5B — Integrasi dengan tamper detection (rework `crypto/tamper.py`) ✅
- [x] Ganti embedding hash blok: hash dihitung dari 7 bit tinggi (`img >> 1`) tapi **disisipkan lewat mekanisme reversible (PEE)** — bukan menimpa LSB. **Blok uji 16×16 & 16-bit hash** (kompromi: 8×8 butuh 39.2 kbit > kapasitas riil ~18.5 kbit/12 round).
- [x] Tambah `protect_image_rev` / `verify_image_rev` → verify mengembalikan `original_recovered` (region restorasi **eksak**).
- [x] Pertahankan API lama (`protect_image`/`verify_image`) — `test_core.py`/`test_dicom.py` tetap hijau.
- [x] Deteksi & lokalisasi akurat pada citra ber-watermark (blok 16×16) — uji 10/10 di `test_reversible_tamper.py`.
- **Side-channel:** round params (peak/z/direction per round) disisipkan LSB di **strip 16 baris bawah** (RONI) — di luar grid hash, dibaca self-contained.
- **Catatan batasan:** tamper yang menyentuh bit-carrier PEE merusak bitstream → tanpa enkripsi lokalisasi tetap jalan (mask lebar); dengan enkripsi → deteksi kuat tapi lokalisasi presisi hilang (dok.)

### 5C — Payload terenkripsi AES ✅
- [x] `protect_image_rev(..., passphrase=...)` → payload (`blok_hash + metadata_digest`) dienkripsi `aes.encrypt` sebelum embed (self-contained: MAGIC+salt+iv).
- [x] IV/salt ter-wrapping otomatis di ciphertext — tidak perlu simpan terpisah.
- [x] Test: kunci salah → `aes.decrypt` gagal (padding) → `error="...kunci salah..."` + `pixel_tamper=True`, tanpa pengecualian crash. 14/14 di `test_reversible_tamper.py`.

### 5D — Integrasi DICOM 16-bit ✅
- [x] Uji skema reversible pada MRI 16-bit → **PSNR(wm)=88.9 dB**, verifikasi bersih, **recovery region eksak (PSNR=∞)**.
- [x] `save_watermarked` DICOM reversible identical; simpan `recovered_rev_MRI.dcm`.
- [x] Segmentasi ROI/RONI sederhana (`segment_roi` di `dicom.py`): MRI ini **ROI=99.7% / RONI=0.3%** → dataset nyaris tanpa background (catatan D-6: butuh modality lain dengan RONI nyata).
- [x] Update `tests/test_dicom.py`: 21 uji (tambah recovery, ROI, tamper reversible, preview).

### 5E — Evaluasi multi-modality / multi-slice ✅ (parsial: MR-only)
- [x] Dataset lokal: hanya **24 slice MR** (BrainTumorMRI, ROI 99.6-99.8%) — **modalitas kedua (CT/CR) belum tersedia**; dicatat sebagai gap.
- [x] Evaluasi 24 slice (`tests/test_multi_slice.py`): **24/24 verifikasi+recovery eksak OK**.
  - PSNR(wm) min 83.64 / mean 86.34 / max 90.37 dB; kapasitas PEE 27.4-51.6 kbit (mean 36.1 kbit); waktu ~0.2-0.4 s/slice.
  - Slice 13 awalnya overflow (payload 10.1 kbit > kap riil 9.9 kbit) → **MAX_ROUNDS 12→16** menyelesaikan; 16-round cukup untuk semua slice.
  - Catatan: kapasitas riil multiround ≈ 30-50% dari estimasi "zero-payload" (embedding bit-1 mengurangi frekuensi peak round berikutnya).

### 5F — GUI & pelaporan ✅
- [x] `app.py`: alur DICOM → **jalur reversible** (`protect_image_rev`/`verify_image_rev`); hasil verifikasi menampilkan **citra hasil recovery (lossless)** + badge "reversible (PEE-HS)"; pesan error payload diperlihatkan. PNG/RGB tetap jalur legacy LSB (batasan 2D).
- [x] Smoke test Flask (`tests/test_app.py`) 12/12: protek+verif DICOM end-to-end, kunci salah → pesan ramah.
- [ ] (opsional lanjutan) tabel hasil CSV/SSIM kalau diminta reviewer.

### 5G — Sinkronisasi dokumen ✅
- [x] `05_plan_reversible.md` ini: keputusan D-1..D-5, hasil terukur, risiko tercatat.
- [x] `README.md`: roadmap ke fase reversible (lihat bagian roadmap).
- [x] `02/03/04_fase_*.md`: status fase lama tetap sebagai *baseline lossy*; hasil reversible menuntun dokumen jurnal — disinkronkan lewat changelog file ini.
- [x] `01_fase_research.md`: arah/teknik terpilih konsisten (PEE-HS ≈ Paper 2, AES-CBC, ROI/RONI untuk side-channel).

### 5H — (Opsional, default NONAWAJIB) Tamper recovery penuh
- [ ] Jika waktu memadai: simpan info recovery tiap blok agar area yang rusak bisa diperbaiki. Lingkup tugas akhir bisa dihentikan di 5G.

---

## 5. Kriteria "Selesai" (gate sebelum jurnal)

- [x] `extract + reverse` mengembalikan citra asli **byte-identical** pada semua uji (PSNR recovery = ∞, BER = 0) — dilihat `exact=True` di `test_reversible.py`, `test_reversible_tamper.py`, `test_multi_slice.py`.
- [x] Tamper detection & localization benar pada citra ber-watermark (no FP di citra utuh; blok 16×16 ter-lokalisasi di jalur tanpa enkripsi).
- [x] Payload watermark terenkripsi AES (kunci salah → gagal verifikasi tanpa crash).
- [~] Berjalan pada DICOM 16-bit **≥ 2 modality** → tercapai untuk multi-slice MR; **modalitas kedua = gap 5E** (dokumentasi diperlukan).
- [x] Test suite Fase 2 & 3 tetap hijau (8/8, 21/21); test reversible ikut hijau (15/15, 14/14, 12/12).
- [x] Klaim "reversible" kini didukung bukti eksperimen (hanya 16 baris strip RONI yang side-channel lossy — didokumentasikan).

---

## 6. Target Angka (hipotesis awal, diverifikasi saat uji)

| Metrik | Target | Hasil 5A-5E |
|---|---|---|
| PSNR recovery | **∞** (bukti reversibilitas) | **∞** — `np.array_equal` eksak semua |
| BER (recovery) | **0** | **0** |
| SSIM (recovery) | **1.0** | =1.0 (array identik; SSIM belum dilaporkan) |
| PSNR setelah embedding (16-bit) | ≥ 60 dB | **83.6-90.4 dB** (24 MRI slice) |
| Deteksi manipulasi | 100% blok tampered pada skenario uji | Ya (blok 16×16) |
| Lokalisasi | presisi per blok | 16×16 (payload tak terenkripsi); terenkripsi → deteksi kuat, lokalisasi presisi hilang (didokumentasikan) |
| Payload terbawa | muat di kapasitas | 9.5-10.1 kbit berhasil (16 round); kap 27.4-51.6 kbit |
| Runtime | dilaporkan | ~0.2-0.4 s/slice (embed+verify 16 round) |

## 7. Risiko & Mitigasi

1. **Kapasitas histogram shifting tidak cukup untuk payload hash** → TERJADI: solusi PEE checkpoint di 5A + blok 16×16 + MAX_ROUNDS 16 (slice 13). Eskalasi lanjutan: kurangi HASH_BITS/blok, atau multi-bit PEE.
2. **Regresi deteksi tamper karena embedding berubah** → jaga invariant: hash dihitung dari bit stabil; jalankan ulang test suite lama (8/8, 21/21 hijau).
3. **Klaim reversible ditolak reviewer karena payload AES** → kontribusi dipisah & diukur sendiri: (i) reversible+recovery = bukti eksak; (ii) confidentiality payload = AES-256-CBC (Kunci salah → ditolak).
4. **Dataset hanya 1 modality tersedia** → didokumentasikan (gap 5E); evaluasi multi-slice tetap valid sebagai studi eksperimen.
5. **Tamper apa pun merusak bitstream PEE** → deteksi tetap kuat (payload tak terbaca = tandai); **lokalisasi presisi hanya pada citra tak-terserang / jalur non-enkripsi** — perlu penekanan jujur di jurnal dan, bila wajib, pemetaan blok lintas-region untuk recovery (5H).

---

## 8. Titik Kerja per Modul (acuan saat coding)

| Modul | Aksi |
|---|---|
| `crypto/reversible.py` | **BARU** — teknik reversible terpilih (embed/extract/reverse) |
| `crypto/tamper.py` | Rework embed/extract hash blok ke mekanisme reversible + payload AES |
| `crypto/watermark.py` | Dipakai ulang untuk bagian yang tetap LSB (metadata di RONI) bila relevan |
| `crypto/aes.py` | Reuse `aes.encrypt/decrypt` untuk payload; mungkin tambah fungsi enkripsi payload kecil dengan header IV |
| `crypto/dicom.py` | Tambah dukungan matriks ROI/RONI (opsional) |
| `tests/test_core.py` | Tambah uji reversible & BER; jangan rusak 8 uji lama |
| `tests/test_dicom.py` | Tambah uji recovery DICOM & ROI |
| `app.py` / `templates/` | Alur verifikasi + restore di GUI (setelah 5D stabil) |