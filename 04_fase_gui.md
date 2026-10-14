# Fase 4 — Web GUI: Aplikasi Proteksi Citra Medis

Dokumen ini menjelaskan alur dan komponen aplikasi web Fase 4, yang menjadi produk
utama proyek di samping jurnal.

**Status:** Selesai — 9/9 smoke test lulus (halaman + protek + verifikasi + pengujian).

---

## Arah Desain

- **Terang dan bersih** — latar netral, kartu putih, aksen hijau-toska medis.
- **Tanpa AI slop** — tidak ada gradien ungu, neon futuristic, atau tema gelap.
- **Tanpa emoji** — semua ikon memakai SVG inline (stroke, konsisten).
- **Tanpa framework frontend** — HTML/CSS/JS murni agar mudah dipahami dan diaudit.

Halaman yang ada:
1. Beranda (`/`) — dua alur utama: proteksi & enkripsi, dan dekripsi & verifikasi.
2. Algoritma (`/algoritma`) — penjelasan + pseudocode 4 metode inti.
3. Pengujian (`/pengujian`) — daftar kriteria uji, tombol menjalankan ulang, ringkasan hasil.

---

## Alur 1: Proteksi & Enkripsi (sisi pengirim)

```
[1] Unggah citra: PNG/JPG/BMP atau DICOM (.dcm)
[2] Masukkan kunci + metadata (opsional; DICOM diambil otomatis dari tag)
[3] Proteksi
    a. hash blok 8x8 -> LSB  (lokalisasi tamper)
    b. SHA-256 metadata -> LSB
[4] Enkripsi seluruh berkas dengan AES-256-CBC (-PBKDF2)
[5] Hasil:
    - preview citra asli vs ber-watermark
    - PSNR sebagai ukuran tak-terlihatnya watermark
    - ukuran asli vs ukuran terenkripsi
    - tombol unduh file .krip
```

Poin penting: file `.krip` menampung format `AES1 | salt | iv | ciphertext`
dari seluruh byte berkas media, jadi tanpa kunci mustahil dibuka.

## Alur 2: Dekripsi & Verifikasi (sisi penerima)

```
[1] Unggah file .krip
[2] Masukkan kunci (metode verifikasi metadata untuk gambar)
[3] AES decrypt -> berkas tervalidasi kebenarannya (PNG atau DICOM)
[4] Verifikasi otomatis
    a. piksel: hash blok dihitung ulang vs LSB -> mask manipulasi
    b. metadata: hash SHA-256 dicek ulang
[5] Hasil:
    - citra hasil dekripsi + peta lokasi manipulasi
    - status piksel (utuh / terdeteksi + banyak piksel ditandai)
    - status metadata (valid / tidak valid)
    - tombol unduh berkas asli hasil dekripsi
```

## Penanganan Kasus

- `kunci salah` -> error ditampilkan, tidak ada data bocor.
- `bukan .krip` -> ditolak.
- `hasil bukan gambar/DICOM` -> diperiksa magic bytes (`PNG`/`DICM`/`JPEG`/`BMP`) dan ditolak.
- `DICOM`: metadata diambil langsung dari tag file setelah dekripsi (Patients ID, Study Date, UID).
- `PNG/JPG`: pengguna menyalin metadata yang dipakai saat proteksi untuk diperiksa.

## Komponen Teknis

- `app.py` — rute utama: `/` (protek + verif + kalkulasi histogram visual), `/algoritma`, `/pengujian`.
- `crypto/histogram.py` — modul rendering histogram: citra asli, ter-watermark, dekripsi, komparasi overlay, dan byte ciphertext AES.
- `templates/base.html` — kerangka: navbar, brand icon SVG, footer.
- `templates/index.html` — dua kartu formulir + panel hasil dinamis + tab komparasi histogram interaktif.
- `templates/algoritma.html` — metode PEE-HS, AES-256-CBC, SHA-256, tamper detection.
- `templates/pengujian.html` — kriteria uji, tombol jalankan ulang, output live.
- `static/css/style.css` — tema terang, aksen `#0f766e`, tata letak kartu histogram responsif.
- `static/js/main.js` — penanganan unggah berkas dan interaktivitas tab.

## Cara Menjalankan

```bash
python app.py
```

Buka `http://127.0.0.1:5000` di browser.

## Uji Web Suite (test_app.py: 12/12 Lulus)

- Halaman `/`, `/algoritma`, `/pengujian` semua dirender (HTTP 200).
- POST protek DICOM -> kalkulasi PEE-HS, generate histogram asli & ter-watermark, unduh berkas `.krip`.
- POST verif DICOM utuh -> "Piksel utuh 100% bit-exact" + histogram pulih & overlay komparasi.
- POST verif DICOM dimanipulasi -> "Manipulasi piksel terdeteksi" + peta lokasi spasial 16x16.
- Integrasi modul `crypto/histogram.py` tervalidasi penuh pada pipeline web.