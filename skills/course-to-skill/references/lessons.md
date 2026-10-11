# Pelajaran dari pembuatan /data-science (KASDAD, Oktober 2026)

Setiap butir di bawah pernah benar-benar terjadi. Butir-butir ini menjadi aturan karena mengabaikannya menghasilkan jawaban ujian yang salah.

## Sumber

1. **Ekstraktor teks melewatkan isi gambar.** Pada KASDAD ada 42 halaman rujukan yang isinya hanya gambar: hitungan Gini, diagram AdaBoost, dan rumus dekomposisi MSE. Render halaman bertanda `[TANPA TEKS]` lalu baca secara visual.
2. **Membaca gambar menemukan kekeliruan.** Peta materi awal menyebut root contoh Ice Age adalah umur 12,5. Slide s39 menunjukkan root sebenarnya Suka Minuman Soda (Gini 0,214). Begitu pula root regression tree adalah Lab Lengkap (90,97), bukan Nonton Video. Jangan menyimpulkan dari teks sebagian.
3. **Label pihak ketiga bisa salah.** Template eksperimen menandai enam konsep sebagai "luar slide" (R², G-mean, Brier, PR-AUC, mutual information regresi, Multinomial NB), padahal semuanya ada di slide. Verifikasi dengan grep di ekstrak teks.
4. **Slide dan worksheet berbeda konvensi.** Contohnya kovarians dengan pembagi N di slide, n − 1 di worksheet, dan n di Gaussian NB pada worksheet 2. Rumus range "+1 unit" juga bertentangan dengan contoh slide. Catat di tabel selisih sumber, jangan memilih diam-diam.
5. **Soal resmi bisa memuat angka antara yang keliru.** Contohnya kovarians tercetak di `soal-pca.pdf`. Jawab dengan data mentah sebagai kebenaran, lalu sebutkan hasil bila angka tercetak dipakai.
6. **Catatan kelas hasil transkripsi** memuat "Extra tip" dan rumus yang direkonstruksi dari ucapan. Keduanya bukan kunci jawaban.

## Korpus dan skrip

7. `fnmatch` membiarkan `*` melintasi `/`, sehingga `*.pdf` menyedot PDF di dalam `.venv`. Skrip sinkronisasi menyamakan kedalaman folder pola dan berkas.
8. Nama catatan kuliah bebas, sehingga pemetaan topiknya perlu dibaca lalu ditulis di `topics.json`. Jangan dipaksa otomatis.
9. Escape ganda di kode Python yang disisipkan lewat skrip membuat regex tidak cocok. Uji fungsi hasil sisipan.
10. Spot-check rujukan secara otomatis: untuk sampel 20 sampai 30 rujukan, pastikan kata kunci ada di halaman yang disebut. Bila tidak ada, cek apakah halaman itu bergambar.

## Keluaran

11. **Bentuk soal harus meniru contoh resmi.** Set pertama berisi soal pendek lepas. Pengguna meminta gaya worksheet: studi kasus berantai dengan puluhan isian. Lihat worksheet dan soal resmi sebelum menulis set.
12. **Cari data tanpa nilai seri** dengan pencarian terprogram, misalnya untuk cost split CART dan jarak KNN. Kunci yang ambigu merusak latihan.
13. **Kunci dihitung oleh kode** dan dicek silang dengan numpy, scipy, atau sklearn. Pembahasan memakai angka dari kode yang sama.
14. **Aplikasi web diuji perilakunya, bukan hanya sintaksnya.** Dengan jsdom, jawab semua kunci lalu pastikan nilainya penuh. Uji pula tiga jalur pemuatan (file://, http, berkas hilang) dan toggle tema. Bug toggle tema baru ketahuan lewat uji ini.
15. Browser memblokir `fetch` ke berkas lokal pada `file://`. Karena itu perender memuat bungkus `sets/<id>.js` sebagai cadangan.
16. **Catatan A4 dicek visual.** Kompilasi pertama hanya mengisi 1,5 kolom di sisi 1. Seimbangkan antarsisi, isi ruang kosong dengan urutan isian soal berantai, dan pakai rata kiri.
17. Mindmap dengan tiga cabang per konsep cepat menyentuh batas 70 node. Untuk 160-an konsep perlu 9 sampai 13 sheet. Rencanakan pembagian sheet sejak awal.

## Lingkungan WiraOS

18. Sesi latar belakang menolak `Write` ke checkout bersama sebelum ada worktree. Folder produk diabaikan git root, jadi worktree tidak menjangkaunya. Tulis di staging lalu salin ke folder produk baru, dan laporkan caranya.
19. Produk dengan slide berhak cipta dipasang sebagai repo GitHub **private**. Tambahkan baris pengecualian di `.gitignore` root.
20. Pasang skill sebagai symlink di `~/.claude/skills` dan `~/.agents/skills`, lalu jalankan `python3 _system/scripts/codex_prompts.py --only <command>` agar `/<command>` muncul di Codex.
21. Perintah garis miring mengikuti nama folder skill. Bila pengguna ingin nama produk berbeda dari perintah, nama folder skill = perintah, sedangkan nama folder produk = slug.
