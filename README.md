# course-to-skill

Skill `/course-to-skill`, yang mengubah folder mata kuliah menjadi skill bersumber slide seperti `/data-science`. Skill ini juga bisa membuat mindmap xmind multi-sheet, aplikasi simulasi ujian, dan catatan ujian A4 bolak-balik. Prosedur lengkap ada di [`skills/course-to-skill/SKILL.md`](skills/course-to-skill/SKILL.md).

## Mulai cepat

```sh
S=skills/course-to-skill/scripts
python3 $S/new_course.py --course-dir '<folder kuliah>' --products-dir '<induk produk>' --slug <slug> --command <perintah> --title "<judul>" --link
python3 '<induk produk>/<slug>/scripts/sync_sources.py' --course-dir '<folder kuliah>'
```

Simulasi ujian: tulis set JSON sesuai `references/exam-set-schema.md`, lalu `python3 $S/build_exam_app.py build <set.json> --out <folder>`. Perender `assets/exam-app/index.html` dipakai ulang lintas mata kuliah, dengan tema terang/gelap dan pembahasan di samping soal.
