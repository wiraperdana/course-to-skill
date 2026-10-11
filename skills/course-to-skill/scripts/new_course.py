#!/usr/bin/env python3
"""Buat produk mata kuliah baru: korpus, skill, dan folder keluaran.

Pemakaian:

    python3 new_course.py --course-dir '<folder kuliah>' --products-dir '<folder induk produk>' \\
        --slug kasdad --command data-science --title "Kecerdasan Artifisial dan Sains Data Dasar" \\
        --code CSGE603130 --keywords "KASDAD, KASDD" [--link] [--dry-run]

Hasil di <products-dir>/<slug>/:
    README.md, .gitignore
    scripts/sync_sources.py        salinan, bisa dijalankan tanpa course-to-skill
    sources/topics.json            topik terdeteksi dari slide berawalan [NN]
    skills/<command>/SKILL.md      dari assets/skill-template
    skills/<command>/references/   course-map.md, formulas.md, exam-patterns.md (kerangka)
    skills/<command>/agents/openai.yaml
    exams/ mindmap/ notes-a4/      tempat set simulasi, outline mindmap, catatan A4

--link memasang symlink skills/<command> ke ~/.claude/skills dan ~/.agents/skills.
Skrip menolak menimpa folder atau symlink yang sudah ada.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
TPL = SKILL_ROOT / "assets" / "skill-template"
SLIDE = re.compile(r"^\[(\w+)\]\s*(.+?)\.(pdf|pptx)$", re.I)


def detect_topics(course: Path) -> list[dict]:
    topics = []
    for f in sorted(course.iterdir()):
        m = SLIDE.match(f.name)
        if m:
            title = re.sub(r"[_ ](updated|final|v\d+)$", "", m.group(2), flags=re.I).strip()
            topics.append({"id": m.group(1), "title": title, "match": [f"[{m.group(1).lower()}]"]})
    return topics


def render(text: str, v: dict) -> str:
    for k, val in v.items():
        text = text.replace("{{" + k + "}}", val)
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--course-dir", type=Path, required=True)
    ap.add_argument("--products-dir", type=Path, required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--command", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--code", default="")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--link", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    for nm, val in [("slug", a.slug), ("command", a.command)]:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", val):
            raise SystemExit(f"--{nm} harus kebab-case huruf kecil: {val}")
    course = a.course_dir.resolve()
    if not course.is_dir():
        raise SystemExit(f"Folder kuliah tidak ada: {course}")
    prod = (a.products_dir / a.slug).resolve()
    if (prod / "skills" / a.command / "SKILL.md").exists():
        raise SystemExit(f"Skill sudah ada di {prod}. Pakai mode update, jangan buat ulang.")

    topics = detect_topics(course)
    v = {"COMMAND": a.command, "COURSE_TITLE": a.title, "COURSE_CODE": a.code or "kode belum diisi",
         "COURSE_KEYWORDS": a.keywords or a.slug.upper(), "PRODUCT_DIR": str(prod), "COURSE_DIR": str(course),
         "SLUG": a.slug, "TODAY": date.today().isoformat()}
    plan = [f"produk  {prod}", f"skill   {prod}/skills/{a.command}", f"topik   {len(topics)} slide terdeteksi: " + ", ".join(t["id"] for t in topics)]
    print("\n".join(plan))
    if a.dry_run:
        return 0

    sk = prod / "skills" / a.command
    for d in ["scripts", "sources", "exams", "mindmap", "notes-a4", sk / "references", sk / "agents"]:
        (prod / d if isinstance(d, str) else d).mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "sync_sources.py", prod / "scripts" / "sync_sources.py")
    topics_cfg = {
        "schema_version": 1,
        "keterangan": "Peta topik. Tiap aturan mencocokkan potongan path relatif berkas di folder kuliah, huruf kecil. Berkas tanpa kecocokan menjadi 'unassigned' dan wajib dipetakan.",
        "topics": topics + [{"id": "tugas", "title": "Tugas dan latihan", "match": ["soal", "worksheet", "tugas"]}],
        "kinds": [
            {"kind": "worked-answer", "match": ["jawaban-"], "ext": [".md", ".html"]},
            {"kind": "exercise", "match": ["soal", "worksheet", "ws"], "ext": [".pdf", ".png", ".jpg"]},
            {"kind": "syllabus", "match": ["silabus", "syllabus", "rps"], "ext": [".md", ".pdf"]},
            {"kind": "lecture-note-comprehensive", "match": ["komprehensif"], "ext": [".md"]},
            {"kind": "lecture-note", "match": ["notes/"], "ext": [".md"]},
            {"kind": "slide", "match": ["["], "ext": [".pdf", ".pptx"]}],
        "include": ["*.pdf", "*.PDF", "*.pptx", "*.md", "notes/*.md", "ws*/*.png", "worksheet*.png", "_output/jawaban-*.md", "_output/jawaban-*.html"],
    }
    (prod / "sources" / "topics.json").write_text(json.dumps(topics_cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (sk / "SKILL.md").write_text(render((TPL / "SKILL.md.tmpl").read_text(encoding="utf-8"), v), encoding="utf-8")
    for f in ["course-map.md", "formulas.md", "exam-patterns.md"]:
        (sk / "references" / f).write_text(render((TPL / f"{f}.tmpl").read_text(encoding="utf-8"), v), encoding="utf-8")
    (sk / "agents" / "openai.yaml").write_text(
        f'interface:\n  display_name: "{a.title}"\n  short_description: "Materi, soal, simulasi, dan catatan {a.slug.upper()} berbasis slide kuliah"\n'
        f'  default_prompt: "Gunakan korpus {a.slug} untuk menjawab dengan rujukan nomor slide."\n', encoding="utf-8")
    (prod / ".gitignore").write_text(".DS_Store\n__pycache__/\n*.pyc\n~$*\n", encoding="utf-8")
    (prod / "README.md").write_text(
        f"# {a.title}, skill /{a.command}\n\nKorpus kuliah {a.title} dan skill `/{a.command}`, dibuat dengan `/course-to-skill` pada {v['TODAY']}.\n\n"
        f"Sinkronkan materi: `python3 scripts/sync_sources.py --course-dir '{course}'`, lalu `--check`.\n", encoding="utf-8")
    print(f"Dibuat: {prod}")

    if a.link:
        for root in [Path.home() / ".claude" / "skills", Path.home() / ".agents" / "skills"]:
            root.mkdir(parents=True, exist_ok=True)
            dst = root / a.command
            if dst.exists() or dst.is_symlink():
                print(f"LEWATI: {dst} sudah ada")
                continue
            dst.symlink_to(sk)
            print(f"Symlink: {dst} -> {sk}")
    print("Berikutnya: sync_sources.py, baca semua materi, isi references/, lalu commit di repo produk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
