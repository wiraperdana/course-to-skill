# Skema set soal simulasi ujian

Perender `assets/exam-app/index.html` tidak pernah diubah per mata kuliah. Setiap ujian adalah satu berkas `sets/<id>.json`. Validasi dengan `scripts/build_exam_app.py check <set.json>` sebelum dipasang.

## Struktur

```json
{
  "id": "kasdad-uts-simulasi-2",            // kebab-case, juga kunci penyimpanan jawaban di browser
  "title": "Simulasi UTS ...",
  "duration_minutes": 150,
  "rules": ["Aturan 1 (HTML boleh)", "..."],
  "sections": [{"id": "A", "title": "Bagian A, autograde", "points": 70},
               {"id": "B", "title": "Bagian B, essay", "points": 30}],
  "groups": [{"id": "K1", "title": "Studi kasus 1. PCA", "stem": "Data dan instruksi bersama (HTML, boleh tabel)"}],
  "questions": [ ... ]
}
```

Total `points` semua soal harus sama dengan total `points` section (toleransi 0,05).

## Soal

| Field | Wajib | Keterangan |
|---|---|---|
| `id` | ya | unik dalam set |
| `section` | ya | id section |
| `group` | tidak | id group; stem group tampil sekali sebelum soal pertamanya |
| `topic` | disarankan | label rekap nilai per topik |
| `kind` | ya | `num`, `mc`, `multi`, atau `essay` |
| `prompt` | ya | HTML |
| `options` | mc, multi | daftar teks opsi |
| `answer` | num, mc, multi | angka; indeks opsi; daftar indeks |
| `decimals` | num | default 4; 0 untuk bilangan bulat |
| `tolerance` | tidak | menimpa toleransi default max(0,5×10⁻ᵈ, 0,1% × jawaban) |
| `solution` | ya | cara pengerjaan langkah demi langkah (HTML) |
| `source` | disarankan | rujukan slide, misalnya `[06] s24-31; worksheet 1` |
| `rubric`, `model_answer` | essay | kriteria dinilai 0, 0,5, atau 1; jawaban model |
| `points` | ya | bobot soal |

Penilaian: `num` benar bila |x − answer| ≤ toleransi (koma atau titik desimal diterima); `mc` tepat sama; `multi` nilai (benar − salah)/jumlah kunci, minimum 0; `essay` rata-rata rubrik yang diisi peserta sendiri.

## Aturan menulis set

1. **Gaya mengikuti contoh resmi mata kuliah.** Bila worksheet berupa studi kasus berantai, pakai `groups` dan pecah rantai menjadi banyak isian berurutan.
2. **Data baru, bukan angka slide.** Cari data yang memberi jawaban tunggal: tanpa nilai seri (cost split, jarak KNN, vote), eigenvalue yang bisa dihitung tangan (matriks blok-diagonal).
3. **Semua kunci dihitung oleh kode** di generator `exams/gen_<id>.py`. Cek silang dengan pustaka independen (numpy, scipy, sklearn) dan sisipkan `assert` untuk identitas (Sv = λv, Σλ = trace, SSE = (n−1)Σλ dibuang).
4. **Pembahasan memakai angka dari kode yang sama**, bukan ketikan ulang.
5. Nilai sangat kecil: minta mantisa dengan satuan ×10⁻ᵏ, seperti worksheet SCeLE.
6. Uji perilaku aplikasi dengan menjawab semua kunci: nilai harus penuh.

## Memasang

```bash
python3 build_exam_app.py build exams/<id>.json --out <output>/simulasi-<id> --inline <output>/simulasi-<id>.html
```

Folder hasil berisi `index.html`, `sets/<id>.json`, dan `sets/<id>.js` (bungkus untuk klik ganda). Beberapa set bisa dipasang sekaligus; pilih lewat `?set=<id>` atau tombol "Buka set JSON". Versi `--inline` satu berkas cocok untuk dikirim.
