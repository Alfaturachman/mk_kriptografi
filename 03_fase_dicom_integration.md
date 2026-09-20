# Fase 3 — Integrasi DICOM: Citra Medis Grayscale 16-Bit

Dokumen ini menjelaskan alur Fase 3: memperluas prototipe Fase 2 agar bekerja pada
**file DICOM MRI** (grayscale, 16-bit, uint16).

**Status:** Selesai — 9/9 test lulus, PSNR 105,47 dB.

---

## Keputusan Dataset

Dipakai **BrainTumorMRI** (Modality `MR`). Alasannya:

- MRI bersifat **anatomi** dengan detail struktur tinggi (448x364) — perubahan LSB 1/65535 tak mengganggu pembacaan diagnostik.
- Miriamodalitas paling banyak dibahas di literatur *medical image watermarking/encryption*, sehingga memudahkan pencarian pembanding untuk jurnal.
- Hanya 24 slice (vs PET 82 slice) dan nilai petanya tidak semi-kuantitatif (SUV) seperti PET.

Kedua dataset sebenarnya identik secara teknis (single-frame, uint16, MONOCHROME2),
jadi modul ini juga berlaku untuk BrainTumorPET bila nanti dibutuhkan.

---

## Perbedaan Kunci vs Fase 2

- **Format piksel** — Fase 2: uint8, 3 kanal (RGB); Fase 3: uint16, 1 kanal (grayscale).
- **Struktur array** — Fase 2: 3D (H, W, 3); Fase 3: 2D (H, W).
- **Metadata** — Fase 2: string buatan manual; Fase 3: tag DICOM asli (PatientID, StudyDate, dll.).
- **Output enkripsi** — Fase 2: byte PNG; Fase 3: byte file `.dcm`.
- **Preview** — Fase 2: langsung tampil; Fase 3: perlu window/level (skala 16-bit -> 8-bit).

---

## Perubahan pada Modul Inti (agar mendukung grayscale 16-bit)

### 1. Perbaikan bit mask untuk uint16
Bug di Fase 2: mask `~np.uint8(1)` bernilai 0x00FE saat dipromosikan ke uint16,
yang menghapus bit 1-7 (bukan hanya bit 0). Diperbaiki dengan mask sesuai dtype array:

```
clear_mask = np.array(1, dtype=chan.dtype)   # uint8 -> 0xFE, uint16 -> 0xFFFE
```

Lokasi: `crypto/watermark.py` (`embed_bytes`), `crypto/tamper.py` (`embed_block_watermarks`).
Gejala saat salah: PSNR turun drastis (55 dB) dan semua blok "dianggap" dimanipulasi.

### 2. Dukungan array 2D (grayscale)
`crypto/watermark.py` dan `crypto/tamper.py` kini memakai `_plane(img, channel)`:
- array 3D -> ambil `img[:, :, channel]` (perilaku Fase 2).
- array 2D -> gunakan array itu langsung (kanal tunggal).

### 3. Strip metadata pada grayscale
Di RGB, hash blok (kanal merah) dan metadata (kanal hijau) terpisah kanal.
Di grayscale hanya ada satu kanal, sehingga area metadata **dipindah ke 8 baris terbawah** (`META_STRIP`),
dan blok-blok hash tidak menjangkau baris itu:

```
_baris terproteksi_  -> grid blok 8x8 dihitung dari (H - META_STRIP) // 8
_strip metadata_     -> 8 baris terakhir, dipakai LSB untuk SHA-256 metadata
```

### 4. `mark_tampered` untuk grayscale
Area tamper ditandai putih (nilai maksimum dtype) karena hanya ada satu kanal.

---

## Modul Baru: `crypto/dicom.py`

| Fungsi | Peran |
|---|---|
| `load(path)` | Baca DICOM -> `(pixel_array, dataset)`, dukung file atau BytesIO |
| `metadata_of(ds)` | Gabungkan tag-tag penting pasien/study menjadi satu `bytes` untuk ditandatangani |
| `save_watermarked(path, ds, pixels)` | Tulis ulang piksel ber-watermark **sambil mempertahankan header DICOM** |
| `preview_8bit(pixels)` | Skala 16-bit -> 8-bit (window/level 1-99 persentil) hanya untuk tampilan, bukan untuk watermarking |

Tag metadata yang ditandatangani (SHA-256):
`PatientID, PatientName, PatientSex, PatientAge, StudyDate, StudyDescription, SeriesDescription, Modality, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID`.

---

## Alur Fase 3

```
[1] LOAD DICOM MRI      dataset/BrainTumorMRI/IM-0001-0001.dcm
    - pixel_array uint16 (448, 364) , nilai 0-1513
    - metadata = gabungan tag pasien/study

[2] PROTECT             protect_image(pixels, metadata)
    a. hash blok 8x8 -> LSB (baris 0-439)
    b. SHA-256 metadata -> LSB strip baris 440-447
    -> data/watermarked_MRI.dcm (header DICOM tetap utuh)

[3] ENKRIPSI AES        byte file .dcm -> data/cipher_MRI.bin

[4] DEKRIPSI            cipher -> file .dcm utuh kembali

[5] VERIFIKASI          blok bersih + metadata valid (tanpa manipulasi)

[6] SIMULASI            ubah 1 blok 8x8 (+30) -> 64 piksel ditandai
                        ganti metadata -> metadata_ok=False

[7] PREVIEW bantu       original_MRI.png & tamper_overlay_MRI.png (16-bit -> 8-bit)
```

---

## Cara Menjalankan

```
python tests\test_dicom.py
```

Ringkasan hasil:

```
[PASS] Proteksi: piksel bersih + metadata valid
[PASS] PSNR citra 16-bit tetap sangat tinggi     PSNR=105.47 dB
[PASS] Write-back DICOM identik
[PASS] Enkripsi AES file DICOM
[PASS] Dekripsi file DICOM utuh
[PASS] Kunci salah ditolak
[PASS] Verifikasi DICOM hasil dekripsi: bersih
[PASS] Manipulasi piksel DICOM terdeteksi        64 piksel
[PASS] Lokalisasi presisi (blok 8x8)
[PASS] Perubahan metadata DICOM terdeteksi
```

File yang dihasilkan:

- `data/watermarked_MRI.dcm` — DICOM MRI dengan watermark, header asli dipertahankan.
- `data/cipher_MRI.bin` — hasil enkripsi AES dari DICOM ber-watermark.
- `data/original_MRI.png` — preview 8-bit citra asli (hanya untuk tampilan).
- `data/tamper_overlay_MRI.png` — preview dengan area manipulasi ditandai putih.

---

## Batasan Prototipe (dicatat untuk jurnal)

- Hanya mendukung DICOM **uncompressed, little-endian** (Explicit/Implicit VR LE).
  File terkompresi (JPEG2000, JPEG Lossless) belum ditangani.
- Lebar/tinggi yang bukan kelipatan 8: blok tepi yang tidak penuh tidak diproteksi.
- Strip 8 baris terbawah tidak diproteksi blok (digunakan metadata).
- Pendekatan fragil bekerja saat penyerang mengubah nilai piksel; penyerang yang
  menghitung ulang dan menanam ulang seluruh hash dapat lolos (keterbatasan standar fragile watermarking).

---

## File yang Tersentuh di Fase 3

- `crypto/watermark.py` — dukungan 2D, mask uint16, kapasitas per kanal.
- `crypto/tamper.py` — grid grayscale, strip metadata, mark grayscale.
- `crypto/dicom.py` — baru: load / metadata / save / preview.
- `tests/test_dicom.py` — baru: uji end-to-end DICOM.
- `requirements.txt` — tambah `pydicom>=3.0`.