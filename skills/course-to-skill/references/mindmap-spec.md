# Spesifikasi mindmap multi-sheet

Satu berkas `.xmind`, satu sheet per topik atau per butir cakupan ujian. Setiap sheet harus terbaca bila dicetak di A4 landscape dengan semua cabang terbuka.

## Struktur per sheet

- Level 0: judul sheet (maks 8 kata).
- Level 1: 4 sampai 7 kelompok konsep (maks 5 kata).
- Level 2: konsep, maksimal 5 per kelompok (maks 5 kata).
- Level 3: tiga cabang wajib per konsep: `Definisi: ...`, `Kapan: ...`, `Langkah: ...` (maks 10 kata).
- Level 4: hanya untuk langkah matematis bertahap, maksimal 15% node sheet.
- Maksimal 70 node per sheet. Kira-kira 14 sampai 16 konsep per sheet.
- Tanpa em dash dan tanpa LaTeX di label. Rumus ditulis ringkas tanpa spasi agar dihitung satu kata, misalnya `x'=(x-min)/(max-min)`.

## Isi

1. Label diambil dari slide terkait: contoh angka, aturan keputusan, dan istilah apa adanya.
2. `sumber` setiap konsep menunjuk halaman slide, format `[NN] sA-B, C; catatan sesi N`. `build_mindmap.py` menarik teks halaman itu ke catatan node.
3. Halaman yang hanya gambar wajib dibaca secara visual, lalu ditulis ke `mindmap/transkripsi.json` dengan kunci `"NN:halaman"`. Skrip melaporkan halaman yang belum ditranskripsi.
4. Bila ada konsep yang tidak muat, catat di laporan dan tawarkan sheet terpisah.
5. Membaca gambar sering menemukan koreksi, misalnya root split yang berbeda dari dugaan. Bawa koreksi itu ke `references/` skill mata kuliah juga.

## Membangun

```bash
python3 build_mindmap.py mindmap/<nama>.json --product <produk> --transkripsi mindmap/transkripsi.json -o <output>/mindmap_<nama>.xmind
```

Jangan membuka aplikasi Xmind milik pengguna. Biarkan pengguna membukanya sendiri.
