# Spesifikasi mindmap multi-sheet

Satu berkas `.xmind` dengan banyak sheet. Setiap sheet harus terbaca bila dicetak di A4 landscape dengan semua cabang terbuka.

## 1. Dua opsi bentuk

Tampilkan tabel ini ke pengguna setiap kali mode mindmap dipanggil, lalu sebutkan nilai yang dipakai.

| Opsi | Nilai | Artinya | Cocok untuk |
|---|---|---|---|
| `--isi` | `penjelasan` (default) | Tiap konsep dipecah jadi elemen penjelasan yang dipilih sesuai konsepnya: Definisi, Tujuan, Urutan, Langkah, Contoh, Hubungan, dan lainnya | Bahan belajar, persiapan ujian |
| | `ringkasan` | Label pendek dari sumber, tanpa elemen penjelasan | Ikhtisar cepat, notulen |
| `--alur` | `kronologi` (default) | Mengikuti urutan penjelasan di sumber: bagian slide atau bab, lalu konsep sesuai urutan kemunculan. Cabang dan konsep diberi nomor urut | Belajar ulang berdampingan dengan slide atau rekaman |
| | `konsep` | Dikelompokkan menurut topik, tanpa nomor. Konsep yang dibahas di beberapa tempat disatukan | Revisi cepat, mencari konsep saat ujian |

Kedua opsi bebas dikombinasikan, jadi ada empat bentuk. Alur kronologi dan alur konsep dari sumber yang sama dibuat sebagai **dua berkas terpisah**, karena satu pohon hanya bisa punya satu hierarki.

Unit sheet berbeda per alur. Pada `konsep`, satu atau dua sheet per topik atau butir cakupan ujian. Pada `kronologi`, satu sheet per dek slide, dan dek tebal dipecah menjadi `05.1`, `05.2`.

**Aturan `--alur kronologi`:**

1. **Sheet** mengikuti dokumen atau dek slide sesuai urutannya. Dek tebal dipecah menjadi sheet berurutan, misalnya `05.1` dan `05.2`.
2. **Level 1** adalah bagian sumber sesuai urutan, misalnya isi slide "Outline" dosen, heading bab, atau agenda rapat. Beri tiap bagian field `sumber` berisi rentang halamannya.
3. **Level 2** adalah konsep sesuai urutan kemunculan. Konsep yang diajarkan ulang di bagian atau dek lain boleh muncul lagi; tandai kaitannya dengan elemen Hubungan.
4. **Rujukan pertama di `sumber`** adalah tempat konsep itu dibahas pada posisinya. Rujukan lain menyusul. Skrip menolak urutan yang mundur, baik nomor slide, halaman, maupun timestamp.
5. **Nomor urut** ("1.", "1.2") diberikan skrip. Jangan menulisnya manual. Nomor tidak dihitung dalam batas kata.
6. Bagian sumber yang tidak punya konsep untuk dijelaskan, misalnya slide sejarah singkat, boleh dilewati. Sebutkan di laporan.

## Struktur per sheet

- Level 0: judul sheet (maks 8 kata).
- Level 1: 4 sampai 7 kelompok konsep atau bagian slide (maks 5 kata, nomor urut tidak dihitung).
- Level 2: konsep, maksimal 5 per kelompok (maks 5 kata).
- Level 3: elemen penjelasan yang **dipilih** untuk konsep itu, satu label `Elemen: isi` (maks 10 kata).
- Level 4: hanya untuk elemen berbentuk daftar (misalnya langkah bertahap atau jenis), maksimal 15% node sheet.
- Maksimal 70 node per sheet. Dengan 3 sampai 4 elemen per konsep, satu sheet muat sekitar 8 sampai 10 konsep.
- Tanpa em dash dan tanpa LaTeX di label. Rumus ditulis ringkas tanpa spasi agar dihitung satu kata, misalnya `x'=(x-min)/(max-min)`.

## Katalog elemen penjelasan

Semua elemen **opsional**. Pilih hanya yang logis untuk konsepnya. Memaksakan semua elemen pada semua konsep menghasilkan isi yang cacat logika, misalnya "langkah matematis" untuk sebuah paradigma. Urutan tampil mengikuti tabel ini.

| Kunci outline | Label | Isi | Contoh |
|---|---|---|---|
| `definisi` | Definisi | Definisi singkat dari slide | Gini: ukuran impurity node |
| `jenis` | Jenis/komponen | Anggota taksonomi atau komponen | Tipe agen: reflex, model-based, goal, utility, learning |
| `tujuan` | Tujuan | Yang ingin dicapai | Bagging: menurunkan variance |
| `kapan` | Kapan | Kondisi pemakaian | Stratified k-fold: data imbalanced |
| `asumsi` | Asumsi | Syarat agar metode sah | Naive Bayes: independen bersyarat kelas |
| `urutan` | Urutan | Tahapan tanpa hitungan | K-fold: latih K-1 fold, uji 1 fold, rata-ratakan |
| `langkah` | Langkah | Langkah step-by-step matematis | `F=(1+β²)PR/(β²P+R)` |
| `contoh` | Contoh | Contoh dari materi, tidak harus angka | Root Ice Age: soda 0,214 |
| `interpretasi` | Interpretasi | Cara membaca hasil | R² 0,55: 55% variasi terjelaskan |
| `pembeda` | Pembeda | Beda dengan konsep yang mirip | Bagging paralel, boosting serial |
| `hubungan` | Hubungan | Kaitan dengan bagian atau sesi lain | Ensemble: menjawab high variance CART |
| `plusminus` | Kelebihan/kekurangan | Pro dan kontra dari materi | Tree: tanpa standardisasi, high variance |
| `jebakan` | Jebakan | Kesalahan umum atau konvensi yang berbeda | Accuracy untuk data imbalanced |
| `catatan` | Catatan | Hal penting lain dari materi | ccp_alpha tidak ada di slide |

## Aturan pemilihan per jenis konsep

| Jenis konsep | Elemen yang biasanya dipakai |
|---|---|
| Algoritma atau metode | Definisi, Tujuan, Langkah (bila ada hitungan) atau Urutan, Contoh, Jebakan atau Kelebihan/kekurangan |
| Rumus atau metrik | Definisi, Langkah, Contoh, Interpretasi, Pembeda |
| Konsep teoretis | Definisi, Tujuan atau Interpretasi, Pembeda, Catatan |
| Taksonomi atau kategori | Definisi, Jenis/komponen, Contoh, Pembeda |
| Prosedur praktik atau metodologi | Definisi, Kapan, Urutan, Jebakan |
| Paradigma, pendapat, atau pendekatan | Definisi, Contoh, Kelebihan/kekurangan, Pembeda |
| Studi kasus atau contoh berjalan | Tujuan, Langkah atau Urutan, Hubungan |

**Urutan atau Langkah?** Ujinya sederhana: bila tahapnya memuat rumus atau angka yang dihitung, pakai Langkah. Bila tahapnya berupa keputusan, kegiatan, atau prosedur kerja, pakai Urutan. Satu konsep boleh memakai keduanya.

**Hubungan** menjawab "kenapa konsep ini muncul di sini". Contohnya "menjawab kelemahan high variance CART" atau "dipakai ulang di sesi KNN". Elemen ini paling berguna di `--alur kronologi`, tetapi tetap opsional. Pasang hanya bila kaitannya tertulis di sumber, dan lewati bila kaitannya sudah tercakup elemen lain.

Minimal 2 elemen per konsep, biasanya 3 sampai 5. Bila satu elemen tidak punya isi dari materi, jangan diisi rekaan; tinggalkan.

## Isi

1. Label diambil dari slide terkait: contoh, aturan keputusan, dan istilah apa adanya.
2. `sumber` setiap konsep menunjuk halaman slide, format `[NN] sA-B, C; catatan sesi N`. `build_mindmap.py` menarik teks halaman itu ke catatan node konsep.
3. Halaman yang hanya gambar wajib dibaca secara visual, lalu ditulis ke `mindmap/transkripsi.json` dengan kunci `"NN:halaman"`. Skrip melaporkan halaman yang belum ditranskripsi. Banyak halaman sekaligus bisa digabung jadi satu gambar montase agar hemat.
4. Membaca gambar sering menemukan koreksi atau fakta baru. Bawa temuan itu ke `references/` skill mata kuliah juga.

## Membangun

```bash
python3 build_mindmap.py mindmap/<nama>.json --product <produk> --transkripsi mindmap/transkripsi.json \
  --isi penjelasan --alur kronologi -o <output>/mindmap_<nama>.xmind
```

Outline lama yang disusun per topik dibangun dengan `--alur konsep`. Teks slide yang dikutip ke catatan dibersihkan dari em dash secara otomatis.

Contoh hidup: KASDAD `mindmap/gen_materi-uts-kasdad-kronologi.py` menurunkan outline kronologi dari outline v2 (alur konsep) tanpa mengetik ulang isinya.

Jangan menimpa mindmap lama bila pengguna meminta perbaikan; tulis versi baru (`-v2`). Jangan membuka aplikasi Xmind milik pengguna.
