# Spesifikasi mindmap multi-sheet

Satu berkas `.xmind`, satu atau dua sheet per topik atau per butir cakupan ujian. Setiap sheet harus terbaca bila dicetak di A4 landscape dengan semua cabang terbuka.

## Struktur per sheet

- Level 0: judul sheet (maks 8 kata).
- Level 1: 4 sampai 7 kelompok konsep (maks 5 kata).
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
| `langkah` | Langkah | Langkah step-by-step matematis | `F=(1+β²)PR/(β²P+R)` |
| `contoh` | Contoh | Contoh dari materi, tidak harus angka | Root Ice Age: soda 0,214 |
| `interpretasi` | Interpretasi | Cara membaca hasil | R² 0,55: 55% variasi terjelaskan |
| `pembeda` | Pembeda | Beda dengan konsep yang mirip | Bagging paralel, boosting serial |
| `plusminus` | Kelebihan/kekurangan | Pro dan kontra dari materi | Tree: tanpa standardisasi, high variance |
| `jebakan` | Jebakan | Kesalahan umum atau konvensi yang berbeda | Accuracy untuk data imbalanced |
| `catatan` | Catatan | Hal penting lain dari materi | ccp_alpha tidak ada di slide |

## Aturan pemilihan per jenis konsep

| Jenis konsep | Elemen yang biasanya dipakai |
|---|---|
| Algoritma atau metode | Definisi, Tujuan, Langkah, Contoh, Jebakan atau Kelebihan/kekurangan |
| Rumus atau metrik | Definisi, Langkah (rumus), Contoh, Interpretasi, Pembeda |
| Konsep teoretis | Definisi, Tujuan atau Interpretasi, Pembeda, Catatan |
| Taksonomi atau kategori | Definisi, Jenis/komponen, Contoh, Pembeda |
| Prosedur praktik | Definisi, Kapan, Langkah, Jebakan |
| Paradigma atau pendekatan | Definisi, Contoh, Kelebihan/kekurangan, Pembeda |

Minimal 2 elemen per konsep, biasanya 3 sampai 5. Bila satu elemen tidak punya isi dari materi, jangan diisi rekaan; tinggalkan.

## Isi

1. Label diambil dari slide terkait: contoh, aturan keputusan, dan istilah apa adanya.
2. `sumber` setiap konsep menunjuk halaman slide, format `[NN] sA-B, C; catatan sesi N`. `build_mindmap.py` menarik teks halaman itu ke catatan node konsep.
3. Halaman yang hanya gambar wajib dibaca secara visual, lalu ditulis ke `mindmap/transkripsi.json` dengan kunci `"NN:halaman"`. Skrip melaporkan halaman yang belum ditranskripsi. Banyak halaman sekaligus bisa digabung jadi satu gambar montase agar hemat.
4. Membaca gambar sering menemukan koreksi atau fakta baru. Bawa temuan itu ke `references/` skill mata kuliah juga.

## Membangun

```bash
python3 build_mindmap.py mindmap/<nama>.json --product <produk> --transkripsi mindmap/transkripsi.json -o <output>/mindmap_<nama>.xmind
```

Jangan menimpa mindmap lama bila pengguna meminta perbaikan; tulis versi baru (`-v2`). Jangan membuka aplikasi Xmind milik pengguna.
