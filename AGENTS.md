---
schema: personal-os/agents@1
level: project
name: "course-to-skill"
area: Business
title: "Course-to-skill, pembuat skill mata kuliah"
---

# Project: Course-to-skill, pembuat skill mata kuliah

Posisi: `Business` / `InnovationKit` / `Products` / `course-to-skill`.

Slug kanonik project ini `course-to-skill`. Ikuti aturan Entity `InnovationKit`, Area `Business`, dan root. Yang di bawah ini hanya tambahan khusus project ini.

## Tujuan

Menyimpan skill `/course-to-skill`, yang mengubah folder mata kuliah menjadi skill bersumber slide (contoh: `/data-science` untuk KASDAD), lengkap dengan mindmap multi-sheet, simulasi ujian web, dan catatan ujian A4.

Project ini selesai saat skill dipakai untuk minimal satu mata kuliah selain KASDAD tanpa perbaikan manual pada skripnya.

## Struktur

| Path | Isi |
|---|---|
| `skills/course-to-skill/SKILL.md` | Prosedur enam mode |
| `skills/course-to-skill/scripts/` | `new_course.py`, `sync_sources.py`, `build_mindmap.py`, `build_exam_app.py`, `build_notes_a4.py` |
| `skills/course-to-skill/assets/` | Perender ujian, template LaTeX catatan A4, template skill mata kuliah |
| `skills/course-to-skill/references/` | Skema set soal, spesifikasi mindmap, panduan catatan A4, pelajaran |

## Konvensi lokal

Project ini punya repo Git sendiri dan diabaikan repo root. Skill dipasang sebagai symlink `course-to-skill` di `~/.claude/skills/` dan `~/.agents/skills/`.

Produk ini tidak menyimpan materi kuliah. Materi tinggal di produk per mata kuliah (misalnya `../kasdad/`), sehingga repo ini aman dibuat publik bila kelak diinginkan.

## Jangan

Jangan mengubah perender `assets/exam-app/index.html` untuk keperluan satu mata kuliah. Semua kebutuhan per ujian harus muat di set JSON, karena itulah yang membuat perender bisa dipakai ulang.

Setiap kali membuat skill mata kuliah baru, tambahkan pelajaran baru ke `references/lessons.md`. Aturan yang lahir dari kejadian nyata jauh lebih berharga daripada aturan rekaan.

## Status

Lihat `STATUS.md`. Perbarui setiap kali skrip atau skill berubah, lalu tawarkan `/monitor-refresh`.
