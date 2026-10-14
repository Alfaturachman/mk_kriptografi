## 7. Panduan Narasi Deskriptif untuk Penjelasan ke Dosen Pembimbing & Penguji

Bagian ini dirancang khusus sebagai panduan berbicara (*speech guide*) dan penjelasan konseptual ketika Anda mempresentasikan atau menjelaskan karya ilmiah ini kepada dosen.

---

### 7.1 Ringkasan Eksekutif (The 2-Minute Elevator Pitch)
> *"Bapak/Ibu Dosen, penelitian ini berfokus pada penyelesaian dilema kritis dalam keamanan citra medis DICOM.*  
>  
> *Di satu sisi, citra medis yang dikirim melalui jaringan PACS sangat rentan terhadap pemalsuan data klinis, manipulasi citra (misalnya penghapusan tumor atau rekayasa klaim asuransi), serta ketidakcocokan identitas pasien.*  
>  
> *Namun di sisi lain, citra medis **sama sekali tidak boleh dirusak** oleh metode watermark konvensional, karena perubahan 1 bit saja pada area otak dapat mengubah interpretasi dokter spesialis radiologi (risiko salah diagnosis).*  
>  
> *Untuk menjawab tantangan tersebut, kami merancang sistem **Reversible Medical DICOM Watermarking** yang menggabungkan kriptografi **AES-256-CBC** dan algoritma reversibel **Prediction Error Expansion - Histogram Shifting (PEE-HS)** secara multi-round.*  
>  
> *Sistem ini memberikan dua lapisan perlindungan sekaligus:*  
> 1. *Lapisan Integritas & Lokalisasi Tamper: Jika citra diedit secara ilegal, sistem dapat mendeteksi dan menandai lokasi manipulasi secara presisi per blok $16 \times 16$ piksel.*  
> 2. *Lapisan Pemulihan Eksak (Bit-Exact Recovery): Jika citra sah, sistem mampu memulihkan wilayah diagnostik otak **100% identik biner tanpa cacat (PSNR = Tak-Hingga, BER = 0, SSIM = 1,0)**.*  
>  
> *Seluruh parameter kontrol disimpan secara in-band di dalam citra, sehingga tidak membutuhkan saluran transmisi terpisah."*

---

### 7.2 Narasi Runtut Alur Kerja Sistem (Tahap demi Tahap dari Awal sampai Akhir)

Jelaskan kepada dosen alur proses ini secara kronologis:

```
[DICOM Asli] ──> [Pemisahan ROI & RONI] ──> [Hash Blok & Metadata] ──> [Enkripsi AES-256]
                                                                                │
[Citra Ter-watermark (PACS)] <── [Simpan JSON ke RONI] <── [Embedding PEE-HS Multi-Round]
            │
            ▼ (Transmisi Jaringan PACS Rumah Sakit)
            │
[Penerimaan Berkas] ──> [Ekstraksi JSON dari RONI] ──> [Inverse PEE-HS (Mundur 16 ke 1)]
                                                                                │
[Alarm / Mask Tamper] <── [Cocokkan Hash] <── [Dekripsi AES-256] <── [ROI Pulih 100% Eksak]
```

#### Tahap 1: Pembacaan Berkas DICOM dan Pemisahan Wilayah (Preprocessing)
1. **Input Data**: Sistem menerima berkas asli MRI Brain (`*.dcm`) 16-bit (`uint16`) dengan resolusi matriks $448 \times 364$ piksel.
2. **Pemisahan Zonasi (ROI vs RONI)**:
   - **ROI (Region of Interest / Wilayah Diagnostik)**: Terletak pada 432 baris teratas ($432 \times 364 = 157.248$ piksel). Ini adalah wilayah anatomi otak pasien yang memuat informasi patologis penting. Wilayah ini dilindungi secara ketat dan ditargetkan pulih 100% tanpa distorsi.
   - **Strip RONI (Region of Non-Interest)**: Terletak pada 16 baris terbawah ($16 \times 364 = 5.824$ piksel). Area ini adalah strip sintetis di luar anatomi diagnostik yang sengaja disiapkan sebagai media penampung parameter dekompresi (*side-channel*).

#### Tahap 2: Pembentukan Payload Kriptografis dan Tanda Tangan Integritas
1. **Ekstraksi Integritas Spasial**:
   - Wilayah diagnostik dibagi menjadi grid blok $16 \times 16$ piksel (total $27 \times 22 = 594$ blok).
   - Agar hash stabil terhadap proses modifikasi LSB saat penandaan, setiap piksel digeser ke kanan 1 bit (`pixel >> 1`).
   - Setiap blok di-hash menggunakan SHA-256, dan diambil 16-bit pertamanya ($594 \times 16\text{ bit} = 9.504\text{ bit}$). Bit-bit inilah yang menjadi "sidik jari spasial" untuk melokalisasi manipulasi.
2. **Ekstraksi Integritas Metadata Pasien**:
   - Metadata krusial pada DICOM Header (seperti `PatientID`, `StudyDate`, `SeriesInstanceUID`) dirangkum dan di-hash penuh menggunakan SHA-256 ( menghasilkan 256 bit / 32 byte digest).
3. **Penyusunan Payload Biner**:
   - Dibuat struktur data mentah: Header sistem (80 bit) + Metadata Digest (256 bit) + 594 Hash Blok (9.504 bit) = **9.840 bit** ($1.230$ byte).
4. **Enkripsi Kriptografis AES-256-CBC**:
   - Pengirim memasukkan *passphrase* rahasia. Kunci enkripsi 256-bit diturunkan menggunakan PBKDF2 dengan 200.000 iterasi HMAC-SHA256 bersama Salt acak 16 byte.
   - Payload dienkripsi dengan algoritma AES-256-CBC menggunakan Initialization Vector (IV) acak 16 byte dan *padding* PKCS#7 (+10 byte).
   - Hasil akhirnya adalah **ciphertext sebesar 10.144 bit** ($1.268$ byte) yang siap disisipkan. Data ini tidak dapat dibaca oleh penyadap tanpa passphrase.

#### Tahap 3: Penyisipan Reversibel PEE-HS Multi-Round (Pengirim)
1. **Prediksi Piksel (MED Checkerboard)**:
   - Piksel ROI dipartisi menjadi dua set selang-seling layaknya papan catur (*checkerboard*): piksel referensi (putih) dan piksel target (hitam).
   - Nilai piksel target diprediksi berdasarkan nilai tetangga referensinya menggunakan operator *Median Edge Detector* (MED).
   - Selisih antara nilai riil dan nilai prediksi menghasilkan galat prediksi: $e = x - \hat{x}$.
2. **Perluasan Galat & Pergeseran Histogram**:
   - Sistem mencari nilai galat yang paling sering muncul (titik puncak / *peak histogram* $e_0$).
   - Bit ciphertext disisipkan hanya pada titik puncak dengan menduplikasi nilai galat: $e' = 2e + b$.
   - Nilai-nilai galat di luar titik puncak digeser 1 langkah ($e' = e \pm 1$) untuk mengosongkan ruang dan mencegah tumpang tindih (*bin collision*).
3. **Iterasi Multi-Round Dinamis**:
   - Karena muatan bit yang harus disisipkan relatif besar (10.144 bit atau $0,065$ bit per piksel), satu putaran (*round*) tidak cukup menampung seluruh bit (terutama pada citra bertekstur rumit).
   - Sistem secara adaptif melakukan perulangan hingga 16 round sampai seluruh 10.144 bit ciphertext tertanam sempurna.
4. **Penyimpanan Side-Channel Parameter ke Strip RONI**:
   - Rekam jejak parameter tiap round (nilai puncak $e_0$, arah geser, dan jumlah bit yang tertanam) dikemas ke dalam berkas JSON biner.
   - String JSON ini disisipkan menggunakan teknik substitusi LSB sederhana ke dalam 16 baris strip RONI terbawah.
5. **Output Pengirim**:
   - Terbentuk citra DICOM terproteksi. Kualitas visualnya sangat tinggi (rata-rata PSNR $86,35$ dB, SSIM $0,999995$), sehingga dokter masih dapat melihat citra tersebut dengan sangat jernih pada PACS viewer standar tanpa gangguan visual.

#### Tahap 4: Transmisi Citra (PACS Storage & Network)
- Berkas DICOM dikirimkan melalui jaringan rumah sakit atau cloud storage.
- Karena sistem ini bersifat *in-band watermarking*, seluruh tanda tangan autentikasi dan parameter pemulihan menempel langsung di dalam berkas citra. Tidak dibutuhkan berkas tambahan (*sidecar file*) yang berisiko hilang di perjalanan.

#### Tahap 5: Pemulihan Citra & Ekstraksi Payload (Penerima / Dokter)
Saat berkas diterima di ruang baca radiologi:
1. **Ekstraksi Parameter PEE**:
   - Sistem membaca bit-bit LSB dari 16 baris strip RONI terbawah dan mendeserialisasi kembali struktur JSON parameter round.
2. **Pembalikan Galat (Inverse PEE-HS)**:
   - Sistem menjalankan proses secara terbalik, dimulai dari **Round 16 mundur hingga Round 1**.
   - Karena piksel referensi tidak pernah disentuh saat penyisipan, penerima dapat menghitung nilai prediksi $\hat{x}$ yang **persis sama 100%**.
   - Pada setiap round:
     - Bit ciphertext diekstrak: $b = e' \pmod 2$.
     - Nilai galat asli dipulihkan: $e = \lfloor e' / 2 \rfloor$.
     - Nilai piksel asli dipulihkan: $x = \hat{x} + e$.
     - Histogram yang sebelumnya digeser dinormalkan kembali ke posisi semula.
3. **Hasil Pemulihan ROI**:
   - Seluruh 157.248 piksel pada wilayah diagnostik kembali ke nilai aslinya secara eksak bit demi bit (`np.array_equal` bernilai `True`, BER = 0, PSNR = $\infty$, SSIM = 1.0).

#### Tahap 6: Dekripsi & Verifikasi Integritas Spasial (Penerima)
1. **Dekripsi Ciphertext**:
   - Penerima memasukkan passphrase untuk mendekripsi ciphertext AES-256-CBC.
   - Sistem memeriksa integritas format: validasi *padding* PKCS#7 dan validasi magic header `RPEE01`.
2. **Verifikasi Metadata**:
   - Sistem menghitung ulang SHA-256 dari header DICOM saat ini dan mencocokkannya dengan digest metadata hasil dekripsi. Jika cocok, data pasien terbukti otentik dan tidak tertukar.
3. **Verifikasi Integritas Spasial Piksel**:
   - Sistem menghitung ulang hash 16-bit untuk masing-masing dari 594 blok pada citra yang telah dipulihkan.
   - Nilai hash hasil hitung ulang dicocokkan dengan nilai hash asli di dalam payload.
4. **Keputusan Akhir**:
   - **Jika Seluruh Hash Cocok 100%**: Sistem menerbitkan status **"INTEGRITAS VALID & OTENTIK"**. Dokter radiologi disajikan citra asli murni tanpa artifak apapun untuk penegakan diagnosis tumor atau kelainan patologis.
   - **Jika Ditemukan Ketidakcocokan**: Sistem langsung membunyikan **"ALARM MANIPULASI (TAMPER DETECTED)"** dan menghasilkan peta biner (*tamper mask*) yang menandai blok spasial $16 \times 16$ mana saja yang telah dimanipulasi oleh pihak luar.

---

### 7.3 Naskah Tutur Presentasi untuk Mahasiswa (Slide-by-Slide Script)

Gunakan naskah ini sebagai contekan kata demi kata saat presentasi di hadapan dosen:

#### Slide 1: Judul & Latar Belakang
> *"Selamat pagi/siang Bapak/Ibu Dosen Penguji dan Pembimbing. Pada kesempatan kali ini, saya mempresentasikan tugas akhir/penelitian saya mengenai **Sistem Reversible DICOM Watermarking berbasis Multi-Round PEE-HS dan Enkripsi AES-256 untuk Proteksi Integritas Citra Medis**.*  
>  
> *Latar belakang penelitian ini berangkat dari regulasi keamanan data medis (seperti HIPAA) dan kebutuhan teleradiologi. Citra medis digital sangat rawan dimanipulasi di jaringan publik. Jika kita menggunakan watermark biasa, piksel citra akan rusak permanen. Dalam dunia kedokteran, distorsi sekecil apapun dapat menyebabkan malpraktik diagnosis. Oleh karena itu, kita membutuhkan teknik watermarking yang dapat dipulihkan kembali ke kondisi aslinya secara eksak 100% (Lossless / Reversible)."*

#### Slide 2: Metodologi & Arsitektur Sistem
> *"Pada diagram alur ini, sistem kami bagi menjadi dua sisi: Sisi Pengirim (Proteksi) dan Sisi Penerima (Pemulihan).*  
>  
> *Pertama, citra MRI Brain 16-bit kami bagi menjadi ROI Diagnostik (432 baris) dan Strip RONI (16 baris).*  
> *Kami membagi ROI menjadi 594 blok spasial ukuran 16x16 piksel, lalu menghitung hash 16-bit dari masing-masing blok dengan menggeser 1 bit piksel agar stabil. Hash spasial ini digabungkan dengan SHA-256 metadata pasien menjadi payload biner berukuran 9.840 bit.*  
>  
> *Payload tersebut kemudian kami amankan dengan enkripsi standar industri militer, yaitu AES-256-CBC dengan derivasi kunci PBKDF2 200.000 iterasi."*

#### Slide 3: Algoritma PEE-HS Reversible
> *"Inti dari kemampuan reversibilitas sistem ini terletak pada algoritma **Prediction Error Expansion - Histogram Shifting (PEE-HS)**.*  
>  
> *Kami memprediksi piksel target menggunakan skema checkerboard dengan prediktor MED. Galat prediksi yang terbentuk kami perluas dengan rumus $e' = 2e + b$ pada titik puncak histogram. Karena muatan payload enkripsi mencapai 10.144 bit, kami mengimplementasikan iterasi multi-round hingga 16 round secara dinamis.*  
>  
> *Parameter dekompresi dari setiap round disimpan ke dalam format JSON biner dan disisipkan secara LSB ke 16 baris strip RONI terbawah. Dengan cara ini, citra ter-watermark tetap memiliki kualitas visual luar biasa tinggi di atas 86 dB, sehingga dapat dibuka di PACS viewer manapun tanpa kejanggalan visual."*

#### Slide 4: Pemulihan Eksak & Deteksi Manipulasi
> *"Pada sisi penerima, dokter radiologi tidak perlu mengunduh berkas kunci terpisah.*  
>  
> *Sistem membaca parameter JSON dari strip RONI, lalu membalikkan seluruh proses round dari 16 ke 1. Dengan operasi matematika bilangan bulat: $e = \lfloor e'/2 \rfloor$ dan $b = e' \pmod 2$, **nilai piksel diagnostik berhasil dipulihkan 100% eksak biner tanpa ada 1 bit pun yang meleset**.*  
>  
> *Setelah wilayah diagnostik pulih, bit ciphertext didekripsi dengan AES-256. Sistem kemudian mencocokkan hash blok dan hash metadata. Jika citra asli, verifikasi lolos dengan PSNR Tak-Hingga. Namun jika citra telah diedit, sistem langsung mengaktifkan alarm dan menunjukkan kotak merah lokasi manipulasi secara presisi per blok 16x16 piksel."*

#### Slide 5: Kesimpulan
> *"Berdasarkan pengujian pada seluruh dataset slice MRI, sistem ini terbukti sukses mencapai target keberhasilan: Wilayah diagnostik pulih 100% (BER = 0, PSNR = Tak-Hingga, SSIM = 1,0), kerahasiaan payload terlindungi AES-256, dan manipulasi spasial dapat dilokalisasi secara akurat. Sekian presentasi dari saya, saya persilakan kepada Bapak/Ibu dosen untuk sesi tanya jawab."*

---

### 7.4 Tanya-Jawab Kritis Dosen (Antisipasi Pertanyaan "Maut" Penguji & Jawaban Ilmiahnya)

Berikut adalah pertanyaan-pertanyaan sulit yang sering diajukan oleh dosen kriptografi/pengolahan citra beserta jawaban ilmiahnya:

---

#### Pertanyaan 1:
> **Dosen**: *"Mas/Mbak, Anda mengklaim citra bisa kembali 100% tanpa rusak sama sekali. Apakah Anda yakin tidak ada pembulatan komputasi yang hilang? Buktikan secara matematis!"*

**Jawaban Anda**:
> *"Sangat yakin, Bapak/Ibu. Reversibilitas 100% ini dijamin oleh sifat **Integer-to-Integer Transform** tanpa operasi bilangan pecahan (*floating-point*).*  
>  
> *Secara matematis:*  
> *Saat penyisipan, kita menghitung galat terluas: $e' = 2e + b$, di mana $b \in \{0, 1\}$.*  
> *Saat pemulihan, penerima melakukan operasi pembagian bilangan bulat (*floor division*):*  
> $$\lfloor e'/2 \rfloor = \lfloor (2e + b)/2 \rfloor = \lfloor e + b/2 \rfloor$$  
> *Karena $b$ hanya bernilai 0 atau 1, maka $b/2$ bernilai 0 atau 0,5. Fungsi pembulatan ke bawah ($\lfloor \cdot \rfloor$) akan selalu mengabaikan 0,5 tersebut, sehingga hasilnya kembali murni menjadi $e$.*  
> *Sedangkan bit $b$ diekstrak dengan operasi modulo: $e' \pmod 2 = (2e + b) \pmod 2 = b$.*  
>  
> *Karena prediktor MED menggunakan piksel referensi yang nilainya tidak pernah diubah sejak awal, nilai prediksi $\hat{x}$ pada pengirim dan penerima identik biner. Oleh karena itu, $x = \hat{x} + e$ kembali 100% sama dengan nilai piksel asli sebelum proses embedding. Pengujian empiris pada 24 slice membuktikan `np.array_equal` selalu bernilai `True` dan BER = 0."*

---

#### Pertanyaan 2:
> **Dosen**: *"Saya melihat di tabel evaluasi Anda: di satu bagian Anda menuliskan PSNR = $\infty$ (Tak-Hingga), tapi di bagian lain Anda menuliskan PSNR = 116,42 dB. Kenapa ada dua angka yang berbeda? Apakah sistem Anda sebenarnya lossy?"*

**Jawaban Anda**:
> *"Terima kasih atas ketelitian Bapak/Ibu. Ini adalah poin transparansi penting dalam penelitian kami:*  
>  
> 1. *Nilai **$\text{PSNR} = \infty$** diperoleh ketika kita mengukur **Wilayah Diagnostik (ROI)**, yaitu 432 baris teratas ($157.248$ piksel). Pada wilayah anatomi medis ini, pemulihannya adalah **100% bit-exact murni**. Tidak ada satupun piksel yang berubah.*  
> 2. *Sedangkan nilai **$\text{PSNR} = 116,42\text{ dB}$** diperoleh jika kita mengukur **seluruh kanvas citra penuh** ($448 \times 364$ piksel), yang mencakup 16 baris strip RONI paling bawah.*  
>  
> *Pada 16 baris strip RONI terbawah, bit LSB-nya digunakan sebagai saluran samping (*side-channel*) untuk menyimpan metadata JSON parameter PEE. Karena strip RONI ini sengaja ditempatkan di luar organ otak pasien (area latar belakang hitam non-diagnostik), perubahan nilai LSB di strip ini sama sekali tidak mempengaruhi validitas klinis. Nilai 116 dB itu sendiri secara kasat mata dan komputasi sudah mendekati sempurna, sementara wilayah diagnostik otaknya tetap pulih 100% bit-exact."*

---

#### Pertanyaan 3:
> **Dosen**: *"Kenapa Anda harus repot-repot menggunakan PEE-HS Multi-Round? Kenapa tidak menggunakan metode LSB biasa atau metode transformasi frekuensi seperti DCT atau DWT?"*

**Jawaban Anda**:
> *"Alasan utamanya adalah persyaratan **reversibilitas lossless mutlak** pada citra medis:*  
> 1. *Jika kita menggunakan **LSB konvensional**, bit asli citra akan ditimpa dan hilang permanen (*lossy*). Kita tidak bisa mengembalikan citra asli kecuali jika bit aslinya ikut disimpan di tempat lain, yang akan memicu masalah kapasitas ganda.*  
> 2. *Jika kita menggunakan **domain transformasi (DCT/DWT)**, proses transformasi maju dan balik melibatkan perkalian matriks bilangan riil berkoma (*floating point*). Saat dikonversi kembali ke format integer 16-bit citra medis, akan timbul kesalahan pembulatan (*rounding errors*) yang membuat nilai piksel bergeser $\pm 1$ atau $\pm 2$. Dalam radiologi otak, pergeseran nilai integer ini bisa menimbulkan artifak fatal.*  
> 3. *Dengan **PEE-HS**, kita bekerja langsung pada domain spasial bilangan bulat, sehingga citra memiliki jaminan matematis untuk kembali 100% ke kondisi awal tanpa pembulatan desimal."*

---

#### Pertanyaan 4:
> **Dosen**: *"Mengapa saat menghitung hash spasial per blok, Anda melakukan operasi pergeseran bit `pixel >> 1` bukannya mengambil nilai piksel murni?"*

**Jawaban Anda**:
> *"Kami menerapkan operasi pergeseran bit `pixel >> 1` untuk mewujudkan prinsip **Invariansi Bit Stabil**.*  
>  
> *Piksel MRI 16-bit memiliki rentang nilai dinamis di mana informasi diagnostik utama berada pada bit-bit tingkat tinggi (MSB). Operasi `pixel >> 1` pada hakikatnya membuang bit ke-0 (LSB) dan hanya memperhitungkan 15 bit teratas.*  
>  
> *Hal ini memberikan kestabilan ekstra saat proses autentikasi lokal, sekaligus memastikan bahwa sidik jari integritas blok fokus pada struktur morfologi makro anatomi otak pasien, bukan pada fluktuasi derau kuantisasi terendah."*

---

#### Pertanyaan 5:
> **Dosen**: *"Bagaimana jika peretas melakukan manipulasi yang sangat halus, misalnya hanya mengubah bit LSB (LSB-only tampering) pada wilayah diagnostik? Apakah sistem Anda tetap dapat mendeteksinya?"*

**Jawaban Anda**:
> *"Ya, sistem kami telah diuji secara empiris terhadap serangan manipulasi LSB-only pada 8 slice citra yang berbeda.*  
>  
> *Hasil evaluasi kami menunjukkan:*  
> • *Untuk manipulasi skala 1 piksel tunggal ($1 \times 1$), sistem memiliki tingkat deteksi rata-rata 37,5% secara lokal.*  
> • *Untuk manipulasi skala $8 \times 8$ piksel, tingkat deteksi melonjak menjadi 75% hingga 100%.*  
> • *Untuk manipulasi skala $16 \times 16$ piksel (ukuran 1 blok penuh), **tingkat deteksi mencapai 100% sempurna**.*  
>  
> *Hal ini terjadi karena fungsi hash SHA-256 memiliki efek longsoran (*avalanche effect*). Perubahan pada beberapa piksel dalam satu blok akan merusak nilai hash 16-bit blok tersebut, sehingga alarm tamper langsung berbunyi dan blok yang diserang langsung ditandai dengan warna merah."*

---

#### Pertanyaan 6:
> **Dosen**: *"Bagaimana jika strip RONI di 16 baris terbawah ikut dimanipulasi atau dirusak oleh penyerang?"*

**Jawaban Anda**:
> *"Jika penyerang memanipulasi 16 baris strip RONI terbawah, bitstream parameter PEE di dalamnya akan mengalami korupsi data.*  
>  
> *Saat penerima mencoba membaca data tersebut, pustaka JSON parser akan mengalami kegagalan deserialisasi (*JSON Decode Error* atau *Key Error*). Sistem pengaman kami secara otomatis menangkap eksepsi tersebut dan **langsung menolak berkas di level file** dengan menerbitkan peringatan integritas kritis bahwa berkas DICOM telah rusak atau dipalsukan.*  
>  
> *Dengan demikian, dokter terlindungi dari risiko membaca berkas yang tidak valid."*

---

#### Pertanyaan 7 (Krusial):
> **Dosen**: *"Mas/Mbak, setahu saya hasil MRI 16-bit kurang memuaskan. Bagaimana kalau kita pakai yang 32-bit atau 64-bit saja? Secara konsep sebenarnya sudah oke, tapi plainfile-nya harus saya koreksi dulu."*

**Jawaban Anda (Penjelasan Standar Radiologi & Bukti Visual)**:
> *"Terima kasih atas masukan dan arahan Bapak/Ibu. Terkait format 16-bit vs 32/64-bit serta tampilan visual plainfile MRI mentah, izinkan kami mengklarifikasi berdasarkan standar internasional radiologi medis dan fisika pencitraan:*  
>  
> 1. **Standar Industri Scanner Klinis DICOM adalah 16-bit (`uint16`)**:  
>    *Seluruh perangkat scanner MRI diagnostik di rumah sakit (Siemens, GE Healthcare, Philips, Canon) beroperasi pada konverter ADC fisik 12-bit hingga 16-bit. Standar resmi internasional NEMA PS 3.3 (DICOM Information Object Definition) secara baku mendefinisikan kontainer citra medis sebagai integer 16-bit (`BitsAllocated: 16`, `BitsStored: 12`, `HighBit: 11`).*  
>    *Dalam praktik klinis radiologi di seluruh dunia, **tidak ada scanner MRI yang menghasilkan plainfile citra diagnostik integer 32-bit atau 64-bit**. Mengonversinya ke 32/64-bit secara artifisial justru menyimpang dari standar DICOM resmi rumah sakit, melipatgandakan beban transmisi PACS hingga 2–4 kali lipat, tanpa menambah resolusi fisik sensor scanner.*  
>  
> 2. **Mengapa Plainfile Mentah Tampak Gelap/Kurang Memuaskan di Penampil Biasa?**:  
>    *Pada dataset MRI Brain kami, rentang intensitas riil piksel otak adalah **0 hingga 1.433 / 1.513** (tersimpan dalam presisi 12-bit).*  
>    *Jika file dibuka menggunakan photo viewer komputer biasa atau penampil web tanpa fungsi windowing, aplikasi tersebut akan memetakan nilai piksel secara naif terhadap batas teoritis kontainer 16-bit ($65.535$). Akibatnya, nilai piksel tertinggi $1.433$ hanya menghasilkan intensitas kecerahan **2,2% (1.433 ÷ 65.535 = 0,022)**, sehingga mata kita melihatnya seolah-olah gelap pekat atau kurang memuaskan.*  
>  
> 3. **Solusi Radiologis: Windowing / VOI LUT Standar**:  
>    *Dokter spesialis radiologi tidak pernah melihat citra mentah tanpa windowing. Di monitor PACS rumah sakit, diterapkan fungsi pemetaan klinis (*VOI LUT / Windowing*), misalnya untuk jaringan otak digunakan **Window Center = 500 dan Window Width = 1.000**.*  
>    *Kami telah membuat visualisasi empirisnya pada Gambar [perbandingan_16bit_windowing.png](figures/perbandingan_16bit_windowing.png): ketika fungsi windowing diterapkan, seluruh anatomi parenkim otak, ventrikel, dan batas jaringan tumor tampak **sangat tajam, beresolusi tinggi, dan berbayang kontras sempurna**.*  
>    *Jadi, kualitas data plainfile MRI 16-bit ini sudah 100% tepat dan standar; tampilannya yang sempat terlihat redup semata-mata adalah efek tampilan skala tanpa windowing, bukan karena datanya rusak atau kurang memuaskan."*

---

#### Pertanyaan 8 (Permintaan Khusus Evaluasi Metrik Dosen):
> **Dosen**: *"Silahkan diukur MSE, PSNR, SSIM, UACI, NPCR (untuk imperceptibility-nya), dan diukur entropy, NC, NCC, Chi-Square ($X^2$) dan BER. Berapa hasil pengukuran sistem Anda dan bagaimana analisis ilmiahnya?"*

**Jawaban Anda (Penyajian Data Kuantitatif & Landasan Teori)**:
> *"Terima kasih banyak atas arahan Bapak/Ibu Dosen. Seluruh 10 metrik yang Bapak/Ibu minta telah kami ukur secara otomatis dan komprehensif pada seluruh 24 slice volume aksial MRI Brain (`BrainTumorMRI`) format DICOM 16-bit.*  
>  
> *Laporan formalnya telah kami susun secara lengkap di dokumen [laporan_evaluasi_metrik_dosen.md](laporan_evaluasi_metrik_dosen.md) dengan katalog visual di [katalog_visualisasi_riset.md](katalog_visualisasi_riset.md).*  
>  
> *Berikut adalah rekapitulasi data empiris dan analisis ilmiahnya:*  
>  
> | Kelompok Metrik | Parameter Evaluasi | Nilai Terukur (24 Slice MRI) | Interpretasi Ilmiah |
> |---|---|---|---|
> | **Imperseptibilitas Watermark** | **PSNR (16-bit dynamic)** | **$86,18 \pm 1,97$ dB** (rentang 83,72 – 90,37 dB) | Jauh melampaui batas klinis $\ge 60$ dB, distorsi tak kasat mata |
> | | **PSNR (12-bit stored)** | **$62,10 \pm 1,97$ dB** (rentang 59,64 – 66,29 dB) | Sangat tinggi pada skala intensitas riil modalitas |
> | | **MSE (16-bit space)** | **$11,36 \pm 4,52$** (rentang 4,32 – 19,95) | Rata-rata kuadrat selisih piksel sangat kecil |
> | | **MSE (12-bit space)** | **$0,044 \pm 0,018$** (rentang 0,017 – 0,078) | Deviasi nilai piksel mendekati nol mutlak |
> | | **SSIM Spasial** | **$0,999995 \pm 0,000002$** | Struktur anatomi dan kontur otak 99,9995% identik |
> | | **NPCR (Imperceptibility)** | **$14,37 \pm 0,39\%$** | 85,63% piksel sama sekali tidak disentuh sistem |
> | | **UACI (Imperceptibility)** | **$0,0018 \pm 0,0004\%$** | Rata-rata pergeseran amplitudo hanya 0,0018% dari skala |
> | **Karakteristik Statistik** | **Entropi Asli vs Watermark** | **$4,7071$ vs $4,7066$ bit/px** ($\Delta H = 0,0005$) | Densitas informasi citra tidak berubah secara acak |
> | | **Uji Chi-Square ($X^2$)** | **$p\text{-value} = 1,0000$** ($X^2 = 0,22 \ll 65.535$) | Distribusi histogram citra terbukti identik secara statistik |
> | **Kualitas Pemulihan (Recovery)** | **Recovery BER** | **$0,00000000$ (0 bit salah)** | **100% Bit-Exact Lossless Recovery** |
> | | **Recovery NC & NCC** | **$1,000000$ & $1,000000$** | Korelasi silang normalisasi sempurna |
> | | **Recovery PSNR & SSIM** | **$\infty$ (Tak-Hingga) & $1,000000$** | Pemulihan wilayah diagnostik anatomi tanpa cela |
>  
> *Ada satu catatan metodologis penting yang perlu kami sampaikan terkait **NPCR dan UACI**:*  
> • *Pada **kriptografi cipher citra penuh** (*full-image encryption*), target NPCR adalah $> 99,6\%$ dan UACI $\approx 33,4\%$ untuk mengacak citra menjadi derau salju.*  
> • *Namun pada **watermarking imperceptible citra medis**, targetnya justru **kebalikannya**: NPCR dan UACI harus **serendah mungkin**. Nilai NPCR $14,37\%$ membuktikan bahwa lebih dari $85\%$ piksel organ otak dibiarkan murni tanpa modifikasi, dan UACI $0,0018\%$ membuktikan bahwa pergeseran piksel yang terjadi hanyalah $\pm 1$ tingkat kuantisasi, sehingga dokter radiologi tetap dapat membaca citra dengan jernih tanpa artefak visual.*  
> • *Dan yang paling utama: berkat sifat reversibilitas PEE-HS, saat verifikasi dilakukan, nilai **Recovery BER kembali menjadi 0,00000000 dan PSNR Tak-Hingga**, menjamin kepatuhan zero-tolerance terhadap risiko malpraktik kedokteran."*

---
