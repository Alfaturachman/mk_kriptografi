# Panduan Tanya-Jawab Lisan Sidang & Ujian Dosen
## Reversible Medical DICOM Watermarking & Enkripsi Kriptografis AES-256

> **Petunjuk Penggunaan:**  
> Seluruh jawaban di bawah ini ditulis dalam bentuk **teks naratif deskriptif langsung** (gaya bahasa lisan akademik yang sopan, lugas, dan percaya diri).  
> **Menggunakan angka langsung (digit)** agar mudah dibaca sekilas dan **tanpa rumus matematika tertulis**, sehingga dapat langsung Anda hafalkan atau Anda ucapkan saat ditanya oleh dosen penguji atau pembimbing.

---

## DAFTAR PERTANYAAN CEPAT

- **Bagian 1: Logika Matematika & Algoritma Reversible (PEE-HS)**
  1. [Punya Anda menggunakan Modulo berapa?](#q1)
  2. [Buktikan secara lisan kenapa citra dijamin pulih 100% tanpa ada pembulatan desimal yang hilang!](#q2)
  3. [Kenapa menggunakan Prediktor MED dan skema Checkerboard?](#q3)
  4. [Kenapa harus Multi-Round (sampai belasan round), kenapa tidak 1 round saja?](#q4)
  5. [Bagaimana Anda menjamin tidak terjadi luapan nilai atau overflow pada piksel 16-bit?](#q5)

- **Bagian 2: Metrik Kualitas Citra & Hasil Pengujian**
  6. [UACI & NPCR Anda mengukur apa? Plainteks vs Cipherteks atau Cipherteks vs Cipherteks?](#q6)
  7. [Kenapa nilai UACI Anda cuma 0,0018% dan NPCR 14,37%? Bukankah di kriptografi UACI harus sekitar 33%?](#q7)
  8. [Kenapa di satu bagian Anda sebut PSNR 86 dB, tapi di bagian lain Anda sebut PSNR Tak-Hingga?](#q8)
  9. [Apakah hasil angka evaluasi pada GUI saat Enkripsi dan saat Dekripsi nilainya sama persis?](#q9)
  10. [Apa arti hasil uji Chi-Square keseragaman AES dengan nilai p di atas 0,05?](#q10)
  11. [Mengapa nilai Bit Error Rate (BER) pemulihan wajib 0,00000000 mutlak?](#q11)

- **Bagian 3: Keamanan Kriptografi (AES-256, Hash, Salt, & IV)**
  12. [Kenapa memakai mode AES-256-CBC, bukan ECB atau GCM?](#q12)
  13. [Apa peran Salt dan IV pada AES? Mengapa ciphertext selalu berbeda jika dienkripsi ulang?](#q13)
  14. [Mengapa password diturunkan lewat PBKDF2 200.000 iterasi, bukan di-hash biasa?](#q14)
  15. [Apa fungsi operasi geser bit piksel ke kanan 1 kali sebelum di-hash?](#q15)
  16. [Apa yang terjadi jika dokter memasukkan kata sandi yang salah saat verifikasi?](#q16)

- **Bagian 4: Standar Citra Medis DICOM & Lokalisasi Manipulasi**
  17. [Kenapa memakai format DICOM 16-bit, kenapa tidak 32-bit atau 64-bit saja?](#q17)
  18. [Kenapa citra asli DICOM 16-bit tampak gelap pekat di monitor atau penampil biasa?](#q18)
  19. [Apa dasar pembagian wilayah ROI 432 baris dan RONI 16 baris terbawah?](#q19)
  20. [Kenapa ukuran blok deteksi manipulasi dipilih 16x16 piksel?](#q20)
  21. [Bagaimana jika penyerang sengaja merusak strip RONI di 16 baris terbawah?](#q21)

---

## BAGIAN 1: LOGIKA MATEMATIKA & ALGORITMA REVERSIBLE

<a id="q1"></a>
### Q1: Punya Anda menggunakan Modulo berapa?

**Jawaban Lisan Anda:**
> *"Sistem kami menggunakan **Modulo 2**, Bapak/Ibu.  
> Alasannya karena data watermark yang disisipkan berupa bit biner murni, yaitu bernilai 0 atau 1.  
> Pada saat proses penyisipan di pengirim, nilai selisih tebakan atau galat dikalikan 2, sehingga hasilnya pasti menjadi bilangan genap. Jika bit yang kita titipkan adalah angka 0, hasilnya tetap bilangan genap. Namun jika bit yang kita titipkan adalah angka 1, hasilnya berubah menjadi bilangan ganjil.  
> Oleh karena itu, pada saat penerima mengekstrak kembali data tersebut, penerima cukup melakukan operasi sisa bagi dengan Modulo 2: jika hasilnya genap atau 0 berarti bit aslinya adalah 0, dan jika ada sisa 1 berarti bit aslinya adalah 1. Dengan cara ini, seluruh bit data rahasia dapat terekstraksi kembali dengan tepat tanpa ada kesalahan."*

---

<a id="q2"></a>
### Q2: Buktikan secara lisan kenapa citra dijamin pulih 100% tanpa ada pembulatan desimal yang hilang!

**Jawaban Lisan Anda:**
> *"Jaminan pemulihan 100% ini diperoleh karena seluruh proses komputasi kami bekerja murni pada domain bilangan bulat, tanpa melibatkan operasi bilangan berkoma atau desimal sama sekali.  
> Logikanya begini, Bapak/Ibu:  
> Saat pengirim menyisipkan bit, nilai galat dikalikan 2 lalu ditambah bit 0 atau 1.  
> Saat penerima memulihkan citra, penerima membagi nilai tersebut dengan angka 2 menggunakan pembagian bilangan bulat atau pembulatan ke bawah. Karena bit yang disisipkan tadi hanya bernilai 0 atau 1, maka saat dibagi 2 sisa pecahannya maksimal hanya 0,5. Sifat pembagian bulat ke bawah secara otomatis membuang 0,5 tersebut, sehingga nilai galatnya kembali murni ke angka bulat semula sebelum disisipi.  
> Selain itu, nilai tebakan piksel dihitung dari piksel tetangga yang tidak pernah diubah nilainya sejak awal, sehingga tebakan di sisi pengirim dan penerima pasti sama persis. Ketika tebakan yang sama dijumlahkan dengan galat asli yang sudah pulih, nilai piksel organ otak kembali 100% persis ke kondisi awal. Bukti pengujian pada seluruh 24 slice citra MRI kami menunjukkan bahwa nilai piksel sebelum dan sesudah proses selalu identik biner tanpa ada perbedaan sedikit pun."*

---

<a id="q3"></a>
### Q3: Kenapa menggunakan Prediktor MED dan skema Checkerboard?

**Jawaban Lisan Anda:**
> *"Kami menggabungkan skema papan catur atau checkerboard dengan prediktor tepi MED karena 2 alasan utama:  
> Pertama, skema papan catur membagi citra secara selang-seling menjadi piksel referensi dan piksel target. Piksel referensi dibiarkan utuh dan hanya piksel target yang disisipi data. Dengan begitu, saat pemulihan, penerima dapat menghitung ulang nilai tebakan menggunakan piksel referensi yang nilainya masih murni.  
> Kedua, prediktor MED dipilih karena kemampuannya mendeteksi arah garis tepi organ tubuh, baik garis vertikal maupun horizontal. Prediktor rata-rata biasa cenderung membuat garis batas organ menjadi kabur, sedangkan prediktor MED mampu menebak nilai piksel mengikuti arah garis jaringan otak. Hasilnya, selisih antara nilai asli dengan nilai tebakan menjadi sangat kecil dan terkumpul rapat di angka 0. Kumpulan selisih di angka 0 inilah yang menjadi ruang utama kita untuk menyisipkan bit watermark dalam jumlah besar."*

---

<a id="q4"></a>
### Q4: Kenapa harus Multi-Round (sampai belasan round), kenapa tidak 1 round saja?

**Jawaban Lisan Anda:**
> *"Karena kapasitas data rahasia yang harus kita tampung cukup besar, yaitu mencapai 10.144 bit yang memuat intisari metadata pasien, identitas DICOM, dan 594 sidik jari blok spasial yang terenkripsi AES.  
> Pada citra medis otak, 1 round rata-rata hanya mampu menampung sekitar 1.000 hingga 2.000 bit agar profil sebaran pikselnya tidak rusak. Jika kita paksakan masuk dalam 1 round saja, citra akan mengalami distorsi visual yang kasar.  
> Oleh karena itu, kami membagi penyisipan ke dalam beberapa putaran secara bertahap, rata-rata 8 hingga 12 round secara dinamis. Dengan menyebar muatan ke beberapa putaran, pergeseran nilai piksel pada setiap putaran menjadi sangat halus, sehingga kualitas citra yang dihasilkan tetap luar biasa jernih dengan nilai PSNR di atas 86 dB dan kemiripan bentuk di atas 99,999%."*

---

<a id="q5"></a>
### Q5: Bagaimana Anda menjamin tidak terjadi luapan nilai atau overflow pada piksel 16-bit?

**Jawaban Lisan Anda:**
> *"Sistem kami terlindungi secara alami oleh karakteristik fisik citra DICOM 16-bit.  
> Format 16-bit mampu menampung nilai intensitas hingga 65.535. Sementara itu, nilai intensitas tertinggi pada jaringan otak pasien di dataset MRI kami hanya berada di kisaran 1.500. Artinya, masih ada ruang kosong lebih dari 63.000 tingkat intensitas sebelum menyentuh batas atas, sehingga secara teknis mustahil terjadi luapan nilai atau overflow.  
> Selain itu, algoritma kami di program selalu memeriksa batas frekuensi kosong terdekat sebelum menggeser piksel, sehingga nilai piksel tidak akan pernah digeser melompati batas aman wadah datanya."*

---

## BAGIAN 2: METRIK KUALITAS CITRA & HASIL PENGUJIAN

<a id="q6"></a>
### Q6: UACI & NPCR Anda mengukur apa? Plainteks vs Cipherteks atau Cipherteks vs Cipherteks?

**Jawaban Lisan Anda:**
> *"Pada sistem kami, UACI dan NPCR mengukur perbedaan antara **Citra Asli dengan Citra Ber-watermark**, bukan cipherteks melawan cipherteks.  
> Alasannya karena penelitian kami berfokus pada watermarking citra medis, di mana tujuan utamanya adalah menguji imperseptibilitas visual atau seberapa tak kasat mata watermark yang disisipkan. Kami ingin membuktikan bahwa penyisipan data rahasia tidak merusak kejernihan citra medis yang akan dilihat oleh dokter spesialis radiologi."*

---

<a id="q7"></a>
### Q7: Kenapa nilai UACI Anda cuma 0,0018% dan NPCR 14,37%? Bukankah di kriptografi UACI harus sekitar 33%?

**Jawaban Lisan Anda:**
> *"Target UACI sekitar 33% dan NPCR di atas 99% itu berlaku pada sistem enkripsi citra penuh, di mana citra sengaja dirusak total menjadi derau salju abu-abu untuk menguji efek longsoran atau avalanche effect.  
> Namun pada watermarking citra medis, targetnya **justru kebalikannya, yaitu harus serendah mungkin**.  
> Nilai NPCR sebesar 14,37% membuktikan bahwa lebih dari 85% piksel otak sama sekali tidak disentuh atau tidak mengalami perubahan nilai sedikit pun. Hanya 14% piksel yang digeser untuk menampung data watermark.  
> Sedangkan nilai UACI sebesar 0,0018% membuktikan bahwa pergeseran piksel yang terjadi teramat sangat kecil, rata-rata hanya bergeser 1 tingkat intensitas abu-abu saja. Sehingga dokter radiologi tetap dapat membaca citra dengan jernih, dan saat diverifikasi seluruh wilayah organ otak pulih 100% tanpa residu."*

---

<a id="q8"></a>
### Q8: Kenapa di satu bagian Anda sebut PSNR 86 dB, tapi di bagian lain Anda sebut PSNR Tak-Hingga?

**Jawaban Lisan Anda:**
> *"Kedua angka tersebut mengukur 2 tahap yang berbeda pada siklus hidup citra, Bapak/Ibu.  
> Angka **86,19 dB** mengukur kualitas citra ber-watermark saat masih dalam perjalanan atau transmisi di jaringan rumah sakit. Angka ini membuktikan bahwa citra yang beredar sangat jernih dan jauh di atas batas aman medis yaitu 50 dB atau 60 dB.  
> Sedangkan angka **PSNR Tak-Hingga** diperoleh pada tahap verifikasi dan pemulihan di sisi penerima, khusus untuk wilayah diagnostik organ otak. Karena seluruh nilai piksel organ otak berhasil dikembalikan 100% persis sama dengan citra asli tanpa ada 1 pun nilai piksel yang beda, maka selisih kuadrat atau galatnya bernilai 0. Secara matematis, pembagian dengan angka 0 menghasilkan nilai tak hingga, yang membuktikan bahwa pemulihannya bersifat bit-exact tanpa kehilangan informasi sedikit pun."*

---

<a id="q9"></a>
### Q9: Apakah hasil angka evaluasi pada GUI saat Enkripsi dan saat Dekripsi nilainya sama persis?

**Jawaban Lisan Anda:**
> *"Ya, seluruh angka evaluasi pada tampilan GUI saat proses enkripsi dan saat proses dekripsi bernilai **sama persis 100%**, asalkan menggunakan berkas asli yang tidak dimanipulasi.  
> Sebabnya adalah karena algoritma pemulihan kami berhasil mengembalikan citra asli secara sempurna tanpa cacat. Ketika sistem di penerima membandingkan citra hasil pemulihan dengan citra ber-watermark yang ada di dalam berkas krip, seluruh nilai perhitungan seperti MSE, PSNR, SSIM, NPCR, UACI, dan korelasi spasial menghasilkan angka yang identik dengan saat proses proteksi awal.  
> Angka baru akan berbeda jika citra tersebut sengaja diedit atau diserang di tengah jalan, di mana sistem akan membunyikan alarm dan menandai kotak manipulasi dengan warna merah."*

---

<a id="q10"></a>
### Q10: Apa arti hasil uji Chi-Square keseragaman AES dengan nilai p di atas 0,05?

**Jawaban Lisan Anda:**
> *"Nilai p-value sebesar 0,4381, yang berada di atas ambang batas 0,05, membuktikan bahwa sebaran byte ciphertext AES terdistribusi secara acak seragam.  
> Dalam kaidah statistik, jika nilai p berada di atas 0,05, maka hipotesis nol diterima, yang berarti tidak ada perbedaan pola antara data kita dengan sebaran acak sempurna. Hal ini membuktikan bahwa muatan rahasia yang terenkripsi AES tidak memiliki pola frekuensi berulang, sehingga aman dari upaya pembajakan melalui analisis frekuensi sandi."*

---

<a id="q11"></a>
### Q11: Mengapa nilai Bit Error Rate (BER) pemulihan wajib 0,00000000 mutlak?

**Jawaban Lisan Anda:**
> *"Karena dalam dunia medis berlaku prinsip toleransi nol terhadap kesalahan data diagnostik.  
> 1 bit saja yang salah pada area otak dapat disalahartikan oleh dokter spesialis sebagai kalsifikasi mikro, batas kanker palsu, atau perdarahan otak. Pada sistem kami, dari 2.515.968 bit data piksel pada 1 irisan MRI, seluruh 2.515.968 bit tersebut pulih secara utuh tanpa ada 1 bit pun yang salah (BER = 0,00000000), sehingga membebaskan sistem dari risiko salah diagnosis atau malpraktik medis."*

---

## BAGIAN 3: KEAMANAN KRIPTOGRAFI (AES-256, HASH, SALT, & IV)

<a id="q12"></a>
### Q12: Kenapa memakai mode AES-256-CBC, bukan ECB atau GCM?

**Jawaban Lisan Anda:**
> *"Pertama, kami menghindari mode ECB karena ECB sangat berbahaya untuk citra medis; blok data yang bernilai sama akan menghasilkan sandi yang sama persis, sehingga pola kontur organ tubuh masih akan terlihat samar-samar.  
> Kedua, kami memilih mode CBC karena setiap blok data selalu diacak berantai dengan blok sebelumnya menggunakan vektor pengacak, sehingga seluruh pola visual teracak sempurna menjadi derau murni.  
> Ketiga, kami tidak memerlukan mode GCM karena fungsi verifikasi keaslian pada sistem kami sudah ditangani secara mandiri dan lebih teliti oleh 594 hash spasial per blok kecil serta intisari SHA-256 metadata pasien."*

---

<a id="q13"></a>
### Q13: Apa peran Salt dan IV pada AES? Mengapa ciphertext selalu berbeda jika dienkripsi ulang?

**Jawaban Lisan Anda:**
> *"Salt dan IV berfungsi untuk mencegah serangan kamus kata sandi dan serangan pengulangan atau replay attack.  
> Salt acak 16 byte dicampurkan saat menurunkan password dokter agar peretas tidak bisa menggunakan daftar tebakan kata kunci yang sudah dihitung sebelumnya.  
> Sedangkan IV acak 16 byte berfungsi sebagai pengacak awal rantai enkripsi CBC. Karena setiap kali proses enkripsi dijalankan sistem selalu membuat Salt dan IV acak baru, maka berkas krip yang dihasilkan akan selalu berbeda secara biner meskipun citra medis dan password yang dimasukkan sama persis. Hal ini membuat penyadap di jaringan tidak bisa menebak apakah 2 pengiriman berkas memuat data pasien yang sama atau berbeda."*

---

<a id="q14"></a>
### Q14: Mengapa password diturunkan lewat PBKDF2 200.000 iterasi, bukan di-hash biasa?

**Jawaban Lisan Anda:**
> *"Karena fungsi hash biasa seperti SHA-256 bekerja terlalu cepat, sehingga peretas dapat mencoba miliaran kombinasi kata sandi per detik menggunakan kartu grafis modern.  
> Dengan menggunakan PBKDF2 sebanyak 200.000 iterasi, setiap 1 tebakan kata sandi dipaksa melalui 200.000 kali perhitungan berturut-turut. Bagi dokter yang sah, proses ini hanya berlangsung sekitar 0,05 detik sehingga tidak terasa lambat. Namun bagi peretas yang ingin membongkar paksa, serangan tebakan kata sandi menjadi teramat lambat dan mustahil diselesaikan dalam waktu yang masuk akal."*

---

<a id="q15"></a>
### Q15: Apa fungsi operasi geser bit piksel ke kanan 1 kali sebelum di-hash?

**Jawaban Lisan Anda:**
> *"Fungsinya adalah untuk menerapkan prinsip kestabilan bit.  
> Bit paling bawah pada citra medis sangat rentan terhadap fluktuasi derau alami sensor mesin MRI. Dengan menggeser piksel ke kanan 1 kali, kita sengaja mengabaikan bit paling bawah tersebut dan hanya mengambil 15 bit teratas saat menghitung sidik jari hash blok.  
> Hal ini membuat sistem fokus menjaga bentuk anatomi makro organ otak pasien dari manipulasi berbahaya seperti penghapusan tumor, tanpa memicu alarm palsu akibat perubahan derau mikro yang tidak berbahaya."*

---

<a id="q16"></a>
### Q16: Apa yang terjadi jika dokter memasukkan kata sandi yang salah saat verifikasi?

**Jawaban Lisan Anda:**
> *"Sistem kami akan menolak berkas tersebut secara aman tanpa mengalami kerusakan atau aplikasi tertutup tiba-tiba.  
> Ketika password salah, kunci dekripsi yang dihasilkan tidak cocok, sehingga saat proses dekripsi selesai, susunan data di akhir berkas dipastikan tidak valid. Program kami langsung menangkap kondisi tersebut dan menampilkan pesan ramah bahwa kunci tidak cocok atau berkas telah rusak. Data pasien di dalam berkas tetap terkunci rapat dan aman dari pihak yang tidak berhak."*

---

## BAGIAN 4: STANDAR CITRA MEDIS DICOM & LOKALISASI MANIPULASI

<a id="q17"></a>
### Q17: Kenapa memakai format DICOM 16-bit, kenapa tidak 32-bit atau 64-bit saja?

**Jawaban Lisan Anda:**
> *"Karena format 16-bit adalah standar resmi internasional radiologi medis di seluruh dunia sesuai aturan baku DICOM.  
> Semua mesin scanner MRI rumah sakit seperti Siemens, GE, atau Philips menghasilkan data sensor fisik 12 hingga 16-bit. Tidak ada mesin MRI di rumah sakit yang menghasilkan data mentah 32-bit atau 64-bit.  
> Jika kita mengubahnya ke 32-bit, kita melanggar standar rumah sakit dan membuat ukuran berkas membengkak 2 kali lipat lebih besar tanpa menambah kejernihan sensor aslinya. Jadi sistem kami sengaja dirancang agar langsung cocok dengan alur kerja rumah sakit yang nyata."*

---

<a id="q18"></a>
### Q18: Kenapa citra asli DICOM 16-bit tampak gelap pekat di monitor atau penampil biasa?

**Jawaban Lisan Anda:**
> *"Tampilan gelap itu terjadi semata-mata karena perbedaan skala aplikasi penampil foto biasa, bukan karena gambar MRI-nya rusak.  
> Nilai terang piksel pada citra MRI kami berada di rentang 0 sampai sekitar 1.500. Aplikasi penampil gambar biasa mengira batas maksimalnya adalah 65.535, sehingga nilai 1.500 hanya ditampilkan dengan tingkat kecerahan sekitar 2%, yang terlihat sangat redup oleh mata kita.  
> Namun dokter radiologi di rumah sakit selalu menggunakan fitur pengaturan jendela cahaya atau windowing. Ketika fitur windowing diterapkan di penampil medis, seluruh detail jaringan otak, ventrikel, dan tumor langsung tampak sangat tajam dan berkontras tinggi."*

---

<a id="q19"></a>
### Q19: Apa dasar pembagian wilayah ROI 432 baris dan RONI 16 baris terbawah?

**Jawaban Lisan Anda:**
> *"Dasar pembagiannya adalah memisahkan area organ tubuh pasien dengan area latar belakang kosong di luar tubuh.  
> Sebanyak 432 baris teratas mencakup lebih dari 96% gambar, tempat seluruh anatomi organ otak dan tumor pasien berada. Area ini kita lindungi secara mutlak dan kita pulihkan 100% tanpa cela.  
> Sedangkan 16 baris paling bawah adalah area sintetis latar belakang hitam di luar tubuh pasien. Area ini kita manfaatkan sebagai media penyimpanan mandiri untuk menaruh parameter dekompresi data. Dengan cara ini, berkas DICOM dapat membawa kuncinya sendiri tanpa perlu dokter mengirimkan berkas catatan tambahan secara terpisah melalui email atau flashdisk."*

---

<a id="q20"></a>
### Q20: Kenapa ukuran blok deteksi manipulasi dipilih 16x16 piksel?

**Jawaban Lisan Anda:**
> *"Ukuran 16x16 piksel adalah titik temu paling seimbang antara ketelitian deteksi dengan kapasitas muatan citra.  
> Jika kita memakai ukuran blok yang lebih kecil seperti 8x8 piksel, jumlah blok menjadi 4 kali lipat lebih banyak sehingga data hash yang harus disisipkan terlalu besar dan akan menurunkan kualitas visual gambar.  
> Sebaliknya, jika memakai blok yang terlalu besar seperti 32x32 piksel, lokalisasinya menjadi terlalu kasar sehingga manipulasi tumor kecil bisa terlewat.  
> Ukuran 16x16 piksel mampu melokalisasi rekayasa tumor dengan sangat presisi sekaligus menjaga kualitas citra ber-watermark tetap di atas 86 dB."*

---

<a id="q21"></a>
### Q21: Bagaimana jika penyerang sengaja merusak strip RONI di 16 baris terbawah?

**Jawaban Lisan Anda:**
> *"Jika area 16 baris terbawah sengaja dirusak atau dimanipulasi, data parameter dekompresi di dalamnya akan mengalami korupsi.  
> Saat sistem di penerima mencoba membaca data tersebut, pembaca format data akan gagal dan sistem keamanan kami langsung menolak berkas tersebut sejak awal. Sistem akan menerbitkan peringatan bahwa berkas telah rusak atau dipalsukan, sehingga dokter terlindungi dari risiko membaca hasil pemeriksaan yang tidak valid."*

---

## CONTEKAN HAFALAN ANGKA KUANTITATIF (UNTUK DISEBUTKAN SAAT SIDANG)

- **Jumlah dataset:** 24 slice citra MRI Brain T2 aksial format DICOM 16-bit.
- **Kapasitas muatan:** 10.144 bit ciphertext AES-256 (594 hash spasial + 256 bit SHA-256 metadata + header).
- **Kualitas citra ber-watermark:** PSNR rata-rata **86,19 dB**, SSIM **0,999995 (99,9995%)**.
- **Tingkat perubahan piksel (NPCR):** **14,37%** (artinya lebih dari 85% piksel otak tidak disentuh sama sekali).
- **Intensitas pergeseran piksel (UACI):** **0,0018%** (sangat halus, rata-rata hanya bergeser 1 tingkat intensitas).
- **Keacakan ciphertext AES:** Entropi mendekati 8,0 bit/byte, dan uji Chi-Square keseragaman menghasilkan nilai p sebesar **0,4381** (jauh di atas batas 0,05).
- **Hasil pemulihan wilayah diagnostik:** PSNR bernilai **Tak-Hingga**, SSIM **1,000000**, dan Bit Error Rate (BER) bernilai **0,00000000 (0 bit salah)**.
- **Kecepatan komputasi:** Sangat cepat, rata-rata hanya **0,279 detik per slice citra**.
