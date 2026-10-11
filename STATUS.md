---
schema: personal-os/status@1
level: project
project: course-to-skill
title: "Course-to-skill, pembuat skill mata kuliah"
area: Business
entity: InnovationKit
stage: active
started: 2026-10-12
owner: wira
last_updated: 2026-10-12
next_action: "Pakai /course-to-skill untuk mata kuliah berikutnya dan perbarui lessons.md dari pengalamannya."
blockers: []
tags: [skill, kuliah, mindmap, simulasi-ujian]
tasks:
  - id: T1
    title: "Angkat skrip korpus, mindmap, simulasi ujian, dan catatan A4 dari pengalaman KASDAD"
    status: done
  - id: T2
    title: "Tulis SKILL.md, template skill mata kuliah, dan empat referensi"
    status: done
  - id: T3
    title: "Uji ujung ke ujung dengan folder kuliah KASDAD"
    status: done
  - id: T4
    title: "Pakai untuk mata kuliah kedua dan perbarui lessons.md"
    status: backlog
---
# Catatan

## Dari mana status ini disimpulkan

Bagian ini wajib diisi, dan ia yang membuat file ini bisa dipercaya.

Sebutkan bukti untuk tiap task: file apa di disk yang membuat Anda menyimpulkan
status itu. Kalau sebuah task tidak punya bukti, jangan dikarang. Tandai
judulnya dengan `[TANYA WIRA]` dan biarkan ia jadi pertanyaan terbuka.

| Task | Bukti di disk |
|---|---|
| T1 | `skills/course-to-skill/scripts/` berisi lima skrip, semuanya lolos `py_compile`. |
| T2 | `SKILL.md`, `assets/skill-template/`, dan `references/` berisi empat dokumen. |
| T3 | Pada 2026-10-12, `new_course.py` mendeteksi 16 slide KASDAD, sinkronisasi menyalin 65 sumber, mindmap UTS terbangun ulang identik (9 sheet, 130 konsep), dan aplikasi ujian lolos uji jsdom dengan nilai 100/100. |
| T4 | Belum ada mata kuliah kedua per 2026-10-12. |

## Yang belum pasti

- Ekstraksi `.pptx` dan `.docx` bergantung pada skrip `buat-mindmap` dan belum diuji dengan materi PowerPoint sungguhan.
- Pemetaan topik catatan kuliah sengaja manual, karena nama berkas catatan bebas.
