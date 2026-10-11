# Panduan catatan ujian A4 bolak-balik

Untuk ujian open notes satu lembar A4 bolak-balik yang ditulis tangan. PDF menjadi model yang disalin, jadi isinya harus realistis untuk ditulis ulang.

## Prioritas isi

1. **Aturan main hitungan** di pojok pertama: pembulatan, pembagi (n − 1 atau N), definisi kelas positif, konstanta konversi (log₂x = ln x / 0,6931), larangan metodologis, dan cek silang.
2. **Rumus dengan simbol slide**, satu blok per topik, berurutan mengikuti cakupan ujian.
3. **Aturan keputusan** yang tidak bisa diturunkan cepat, misalnya ambang borderline, partisi biner kategorikal, atau pemilihan jumlah komponen.
4. **Tabel nilai siap pakai** untuk kalkulator standalone, misalnya −p log₂ p untuk pecahan umum. Hitung dengan Python.
5. **Urutan isian soal berantai** per tipe soal worksheet, di sisi 2.
6. Jangan menyalin definisi panjang yang bisa dipahami. Tulis kata kunci, rumus, dan angka.

## Teknis

1. Salin `assets/notes-a4/template.tex`, ganti `__JUDUL__`, isi `\sect{...}` per topik.
2. Tiga kolom per sisi, rata kiri, `\fontsize` sekitar 7,5 sampai 8 pt. Sisi 2 dimulai dengan `\newpage` dan `multicols*` baru.
3. `python3 build_notes_a4.py notes-a4/<nama>.tex --out <output>/catatan-<nama>-a4.pdf --preview /tmp/prev`.
4. Wajib tepat 2 halaman. Lihat gambar pratinjau: isi kolom kosong dengan materi bernilai tinggi, pindahkan bagian antar sisi agar seimbang, rapikan baris yang menjorok lebih dari 5 pt.
