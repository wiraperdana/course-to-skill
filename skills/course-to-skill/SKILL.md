---
name: course-to-skill
description: Mengubah folder mata kuliah (slide PDF/PPTX, catatan kuliah, worksheet, soal, silabus) menjadi skill per mata kuliah yang menjawab dengan rujukan nomor slide, misalnya /data-science untuk KASDAD. Membangun korpus berhash dengan ekstrak teks per halaman, peta materi, lembar rumus, pola ujian, lalu memasang skill secara global. Juga membuat mindmap xmind multi-sheet dengan catatan isi slide, aplikasi web simulasi ujian (set soal JSON dan perender HTML), dan catatan ujian A4 bolak-balik untuk ditulis tangan. Pakai saat pengguna menyebut course-to-skill, "jadikan mata kuliah ini skill", "buat skill dari materi kuliah", atau meminta mindmap, simulasi ujian, atau catatan ujian dari materi kuliah.
argument-hint: "[buat <folder kuliah> | update <skill> | mindmap <skill> <cakupan> [--isi penjelasan|ringkasan] [--alur kronologi|konsep] | simulasi <skill> <cakupan> | catatan <skill> <cakupan> | audit <skill>]"
---

# /course-to-skill

Skill ini mengubah satu mata kuliah menjadi **skill yang bisa dipercaya saat ujian**. Analoginya asisten dosen yang membawa slide ke ruang konsultasi. Ia boleh tahu banyak, tetapi setiap jawabannya harus bisa ditunjuk ke slide yang dipakai di kelas. Itu penting karena ujian menilai versi materi yang diajarkan dosen, termasuk notasi dan konvensinya. Pengetahuan umum yang benar pun bisa salah di ujian.

Contoh hidup hasil skill ini adalah `/data-science` (produk `kasdad`). Baca `references/lessons.md` sebelum mulai. Semua butir di sana pernah terjadi.

## Isi skill ini

| Berkas | Fungsi |
|---|---|
| `scripts/new_course.py` | Membuat produk mata kuliah baru: folder, `topics.json` dari slide `[NN]`, skill dari template, symlink |
| `scripts/sync_sources.py` | Menyalin materi berdasarkan SHA-256, tanpa menghapus versi lama; ekstrak teks per halaman; `--check` |
| `scripts/build_mindmap.py` | Membangun xmind multi-sheet dengan opsi `--isi` dan `--alur`; konsep dipecah ke elemen penjelasan yang dipilih; catatan berisi teks slide |
| `scripts/build_exam_app.py` | Memvalidasi set soal JSON dan memasang aplikasi simulasi ujian |
| `scripts/build_notes_a4.py` | Mengompilasi catatan A4 LaTeX dan memastikan tepat 2 halaman |
| `assets/exam-app/index.html` | Perender simulasi ujian: pembahasan di samping soal, timer, autograde, rubrik essay, tema terang/gelap |
| `assets/notes-a4/template.tex` | Template catatan A4 tiga kolom |
| `assets/skill-template/` | Template SKILL.md dan tiga referensi untuk skill mata kuliah |
| `references/` | `exam-set-schema.md`, `mindmap-spec.md`, `notes-a4-guide.md`, `lessons.md` |

Path skrip di bawah relatif terhadap folder skill ini, yaitu tempat `SKILL.md` berada. Resolve symlink bila perlu.

## Mode

### 1. Buat skill mata kuliah (`buat <folder kuliah>`, default)

**Fase 0, klarifikasi.** Tetapkan folder kuliah, nama perintah (`/<command>`), slug produk, judul, kode, dan kata kunci pemicu. Bila pengguna menyebut nama perintah yang berbeda dari nama skill, folder skill = perintah dan folder produk = slug. Di workspace WiraOS, produk tinggal di `Business/InnovationKit/Products/<slug>/`.

**Fase 1, kerangka.**
```bash
python3 scripts/new_course.py --course-dir '<folder kuliah>' --products-dir '<induk produk>' \
  --slug <slug> --command <command> --title "<judul>" --code <kode> --keywords "<kata kunci>" --link
```
Di WiraOS, jalankan juga `python3 _system/scripts/scaffold.py new-project --area Business --entity InnovationKit --parent Products --slug <slug> ...` agar produk punya `AGENTS.md` dan `STATUS.md` yang lolos skema. Jalankan scaffold lebih dulu bila folder belum ada, karena scaffold menolak `AGENTS.md` yang sudah ada.

**Fase 2, korpus.**
```bash
python3 <produk>/scripts/sync_sources.py --course-dir '<folder kuliah>'
```
Baca setiap catatan dan worksheet `unassigned`, petakan topiknya di `sources/topics.json`, lalu sinkronkan ulang sampai `--check` melaporkan `0 masalah`. Untuk berkas yang sudah tersalin, perbaiki `topics` langsung di `manifest.json`.

**Fase 3, baca semuanya.** Baca seluruh slide, catatan, worksheet, soal, dan silabus, termasuk setiap halaman `[TANPA TEKS]` sebagai gambar (`pdftoppm -png -r 60 -f N -l N`). Untuk materi besar, kerjakan per topik dan catat temuan langsung ke referensi.

**Fase 4, referensi** di `skills/<command>/references/`:
1. `course-map.md`: per topik, rentang halaman slide dan isinya, angka contoh slide, catatan kelas berlabel, tabel latihan, materi yang belum terbit.
2. `formulas.md`: rumus dengan rujukan dan **angka kontrol** dari slide.
3. `exam-patterns.md`: komponen nilai dan format ujian, bentuk worksheet, sinyal dosen dari catatan, **tabel selisih sumber**, kebiasaan menjawab.

Lalu spot-check 20 sampai 30 rujukan secara otomatis, yaitu kata kunci harus ada di halaman yang disebut (`lessons.md` butir 10).

**Fase 5, pasang.** Pastikan symlink ada di `~/.claude/skills/<command>` dan `~/.agents/skills/<command>`. Di WiraOS: `python3 _system/scripts/codex_prompts.py --only <command>`, catat skill baru di daftar skill global `_memory/preferences.md`, dan simpan satu memori proyek.

**Fase 6, git.** `git init` di produk, commit tanpa trailer atribusi bila pengguna melarangnya. Slide dosen berhak cipta, jadi bila diminta push, buat repo GitHub **private** (`gh repo create <owner>/<slug> --private --source . --push`). Di WiraOS, tambahkan `/Business/InnovationKit/Products/<slug>/` ke `.gitignore` root.

**Fase 7, laporan.** Sampaikan lokasi produk dan skill, jumlah sumber, topik yang terpetakan, selisih sumber yang ditemukan, dan cara memanggil `/<command>`.

### 2. Update (`update <command>`)
Jalankan mode **tambah materi** di skill mata kuliah itu: sinkronkan, petakan, baca, perbarui tiga referensi, `--check`, lalu commit.

### 3. Mindmap (`mindmap <command> <cakupan>`)
**Jelaskan opsi lebih dulu.** Sebelum menyusun outline, tampilkan tabel opsi di `references/mindmap-spec.md` §1, lalu satu baris `Dipakai: --isi <nilai> --alur <nilai>`. Bila pengguna tidak menyebut opsi, pakai default (`penjelasan`, `kronologi`) lalu lanjutkan.

Ikuti `references/mindmap-spec.md`. Tulis outline di `<produk>/mindmap/<nama>.json`, atau generator `gen_<nama>.py` bila outline diturunkan dari outline lain. Transkripsi gambar masuk ke `<produk>/mindmap/transkripsi.json`. Lalu:
```bash
python3 scripts/build_mindmap.py <produk>/mindmap/<nama>.json --product <produk> \
  --transkripsi <produk>/mindmap/transkripsi.json --isi <isi> --alur <alur> -o <folder output>/mindmap_<nama>.xmind
```
Ulangi sampai semua sheet `LOLOS` dan tidak ada halaman bergambar yang belum ditranskripsi.

### 4. Simulasi ujian (`simulasi <command> <cakupan>`)
Ikuti `references/exam-set-schema.md`. Lihat dulu worksheet dan soal resmi agar level dan bentuknya sama. Tulis generator `<produk>/exams/gen_<id>.py` yang menghitung semua kunci, jalankan, lalu:
```bash
python3 scripts/build_exam_app.py build <produk>/exams/<id>.json \
  --out <folder output>/simulasi-<id> --inline <folder output>/simulasi-<id>.html
```
Uji perilaku dengan jsdom (`lessons.md` butir 14). Menjawab semua kunci harus memberi nilai penuh.

### 5. Catatan ujian A4 (`catatan <command> <cakupan>`)
Ikuti `references/notes-a4-guide.md`. Salin `assets/notes-a4/template.tex` ke `<produk>/notes-a4/<nama>.tex`, isi, lalu:
```bash
python3 scripts/build_notes_a4.py <produk>/notes-a4/<nama>.tex --out <folder output>/catatan-<nama>-a4.pdf --preview /tmp/prev
```
Lihat pratinjau, seimbangkan kedua sisi, ulangi sampai tepat 2 halaman tanpa kolom kosong besar.

### 6. Audit (`audit <command>`)
Jalankan `sync_sources.py --check`, spot-check rujukan, cari em dash di referensi, dan pastikan setiap konsep "luar slide" memang tidak ada di ekstrak teks. Laporkan temuan per butir.

## Aturan

1. Jawaban dan keluaran bersumber dari korpus. Isi di luar korpus wajib berlabel **di luar materi kuliah**.
2. Jangan mengarang nomor slide. Bila belum dicek, tulis "lokasi slide belum dicek".
3. Jangan menghapus `sources/files/`. Versi lama adalah jejak audit.
4. Kunci soal dan angka contoh dihitung kode, bukan diketik dari kepala.
5. Ikuti aturan gaya global pengguna: bahasa permintaan, istilah teknis Inggris didefinisikan pada pemakaian pertama, tanpa em dash.
6. Jangan membuka aplikasi milik pengguna (Xmind, browser). Biarkan pengguna membukanya sendiri.
