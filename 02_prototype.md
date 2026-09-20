# Fase 2 — Prototipe Inti: Pembuktian Konsep

Dokumen ini menjelaskan alur kerja Fase 2: bagaimana skema **Enkripsi AES + Fragile Watermarking**
bekerja pada citra PNG sintetis, langkah demi langkah.

**Status:** Selesai — 8/8 test lulus, PSNR 61,65 dB.

---

## Tujuan Fase 2

Membuktikan bahwa logika algoritma inti berjalan benar sebelum melangkah ke data medis (DICOM) dan web:
1. LSB watermarking bisa menyisipkan dan membaca data.
2. Manipulasi piksel bisa dideteksi **dan dilokalisasi** per blok 8x8.
3. Perubahan metadata pasien bisa dideteksi.
4. Enkripsi AES melindungi file saat disimpan/dikirim, dan kunci salah ditolak.

Gambar yang dipakai **sintetis (dibuat acak oleh komputer)**, bukan dataset asli. Ini sengaja
agar fokus pada kebenaran algoritma, bukan performa pada data nyata.

---

## Diagram Alur

```
[1] Uji LSB dasar: sisip "uji-embedding" ke LSB kanal biru -> baca balik, harus cocok

[2] PROTECT (stempel + tanda tangan)
    a. Bagi gambar jadi blok 8x8
        - tiap blok: hash SHA-256 dari 7 bit tertinggi piksel
        - 16 bit pertama hash disisipkan ke LSB kanal merah blok itu
    b. Hash SHA-256 metadata pasien disisipkan ke LSB kanal hijau
    -> data/watermarked.png

[3] ENKRIPSI AES-256-CBC  : seluruh byte PNG -> data/cipher.bin  (yang "dikirim/ditaruh server")

[4] DEKRIPSI              : cipher.bin -> PNG -> recovered

[5] VERIFIKASI (tanpa citra asli)
    a. Hitung ulang hash tiap blok, bandingkan dengan cap di LSB
       -> beda = blok dimanipulasi -> mask (lokasi presisi)
    b. Bandingkan hash metadata ekstrak vs hash ulang

[6] SIMULASI SERANGAN     : ubah piksel 1 area (+40) -> terdeteksi, 64 piksel ditandai

[7] UBAH METADATA         : ganti data pasien -> metadata_ok = False, piksel tidak disentuh
```

---

## Penjelasan Tiap Langkah

### 1. Uji LSB dasar
File: `tests/test_core.py:57-59`

Sisipkan teks `uji-embedding` ke bit terakhir kanal biru, lalu baca kembali dan bandingkan.
Memastikan mekanisme utama watermarking (`crypto/watermark.py`) bekerja.

### 2. Proteksi citra (protect_image)
File: `crypto/tamper.py:107-109`

`protect_image` menjalankan dua hal berurutan:

**a. Stempel blok** — `embed_block_watermarks` (`crypto/tamper.py:34-47`)
- Gambar dibagi menjadi blok 8x8.
- Untuk tiap blok, ambil **7 bit tertinggi** dari semua pikselnya (nilai piksel `>> 1`).
- Hitung SHA-256 dari data itu, potong **16 bit pertama**.
- 16 bit cap tersebut disisipkan ke **LSB kanal merah** 16 piksel pertama di blok itu.
- Karena cap hanya menempel di bit terakhir, nilai piksel nyaris tidak berubah
  (maksimal bergeser 1 dari 255).

Kenapa hash dihitung dari 7 bit tinggi, bukan 8 bit penuh?
Agar penyisipan cap tidak mengubah nilai yang di-hash. Cap (LSB) dan konten (7 bit tinggi)
saling terpisah, sehingga hasil hash tetap stabil.

**b. Tanda tangan metadata** — `embed_metadata` (`crypto/tamper.py:95-97`)
- Hash SHA-256 dari metadata pasien (`PATIENT:AE-0001;STUDY:CHEST-XRAY;...`)
  disisipkan ke **LSB kanal hijau**.
- Berbeda kanal dari cap blok, sehingga tidak saling menimpa.

Hasil disimpan sebagai `data/watermarked.png` (`tests/test_core.py:61-63`).

### 3. Enkripsi AES
File: `crypto/aes.py` dan `tests/test_core.py:68-82`

- Seluruh byte file PNG di-enkripsi **AES-256-CBC**.
- Kunci diturunkan dari password melalui **PBKDF2** (200.000 iterasi) + salt acak.
- Format file hasil: `AES1 | salt(16) | iv(16) | ciphertext`.
- Disimpan ke `data/cipher.bin`. Ini representasi file yang ditaruh di server / dikirim.

### 4. Dekripsi
File: `tests/test_core.py:84-95`

- `decrypt(cipher, kunci)` mengembalikan byte PNG **identik** dengan sebelum enkripsi
  (test `dekripsi sama persis` LULUS).
- Kunci salah akan memicu `ValueError` (test `kunci salah ditolak` LULUS).

### 5. Verifikasi (bebas referensi)
File: `crypto/tamper.py:112-118`

`verify_image` memeriksa dua hal tanpa perlu citra asli:

**a. Deteksi & lokalisasi piksel** — `localize_tamper` (`crypto/tamper.py:65-80`)
- Hitung ulang hash tiap blok dari 7 bit tinggi yang ada saat ini.
- Bandingkan dengan cap yang diekstrak dari LSB kanal merah.
- Blok dengan hash berbeda -> dianggap dimanipulasi -> area 8x8 ditandai `255` di mask.

**b. Verifikasi metadata** — `verify_metadata` (`crypto/tamper.py:100-104`)
- Baca ulang hash dari LSB kanal hijau.
- Cocokkan dengan SHA-256 metadata yang diberikan saat verifikasi.

### 6. Simulasi serangan piksel
File: `tests/test_core.py:102-115`

- Area baris 60-63, kolom 88-91 diubah (+40, dibatasi 0-255).
- Verifikasi ulang -> area itu ditandai. Karena berada di dalam satu blok 8x8,
  persis **64 piksel** ditandai (blok baris 56-63, kolom 88-95).

### 7. Simulasi perubahan metadata
File: `tests/test_core.py:117-121`

- Verifikasi dengan metadata pasien yang berbeda (`PATIENT:EVIL-9999;...`).
- Hasil: `metadata_ok = False` dan piksel **bersih** (tidak ada tamper).

---

## Kenapa Hasilnya Begitu?

- **Kenapa PSNR tinggi (61,65 dB)?** Hanya LSB yang disentuh, nilai piksel bergeser maksimal 1/255. Perubahan tak terlihat mata. PSNR dihitung di `tests/test_core.py:31-35`.
- **Kenapa presisi "64 piksel"?** Deteksi bekerja per blok 8x8. Satu blok = 64 piksel.
- **Kenapa tadi bisa 128 piksel?** Bukan bug — area tamper membentang dua blok, dua blok ditandai = 128 piksel.
- **Kenapa bisa tanpa citra asli?** Tiap blok membawa cap hash isinya sendiri (self-embedded fragile watermark).
- **Kenapa tanpa AI/training?** Murni matematika + manipulasi bit (rule-based), sesuai novelty jurnal.

---

## Cara Menjalankan

```
python tests\test_core.py
```

Hasil yang muncul di terminal (ringkas):

```
[PASS] LSB embed/extract membulat
[PASS] PSNR tetap tinggi (>45 dB)           PSNR=61.65 dB
[PASS] Enkripsi AES berhasil                +43 byte, ~52 ms
[PASS] Dekripsi mengembalikan file asli
[PASS] Kunci salah ditolak
[PASS] Tanpa tamper: piksel bersih + metadata valid
[PASS] Manipulasi piksel terdeteksi         64 piksel ditandai
[PASS] Lokalisasi presisi (1 blok 8x8)
[PASS] Perubahan metadata pasien terdeteksi
```

File yang dihasilkan:

- `data/watermarked.png` — citra asli + stempel blok + tanda tangan metadata.
- `data/cipher.bin` — hasil enkripsi AES dari PNG ber-watermark.
- `data/tamper_overlay.png` — hasil verifikasi: area manipulasi ditandai merah.

---

## Modul Terkait

- `crypto/aes.py` — enkripsi/dekripsi AES-256-CBC + derivasi kunci PBKDF2.
- `crypto/watermark.py` — LSB embed/extract data apa pun di satu kanal, format header `KPGW`.
- `crypto/tamper.py` — cap hash blok, lokalisasi tamper, tanda tangan metadata.
- `tests/test_core.py` — uji end-to-end alur fase 2.

> Catatan: kapasitas LSB per kanal untuk citra 128x128 adalah 2040 byte
> (di luar header 8 byte). Cukup besar untuk SHA-256 (32 byte) yang disimpan.