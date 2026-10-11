#!/usr/bin/env python3
"""Validasi set soal JSON dan pasang aplikasi simulasi ujian.

Perender (`assets/exam-app/index.html`) tidak pernah diubah per mata kuliah.
Yang berganti hanya set soal `sets/<id>.json`, mengikuti
`references/exam-set-schema.md`.

Pemakaian:

    python3 build_exam_app.py check <set.json> [<set.json> ...]
    python3 build_exam_app.py build <set.json> [...] --out <folder>
    python3 build_exam_app.py build <set.json> --out <folder> --inline <berkas.html>

`build` menulis ke <folder>:
    index.html            perender, set pertama menjadi default
    sets/<id>.json        set soal (sumber kebenaran)
    sets/<id>.js          bungkus JSON yang sama, agar index.html bisa dibuka
                          dengan klik ganda (file://) tanpa server
`--inline` juga menulis satu berkas HTML mandiri berisi set pertama.

Buka dengan klik ganda, atau `python3 -m http.server` di <folder> lalu
`http://localhost:8000/?set=<id>`. Set lain bisa dipilih lewat tombol
"Buka set JSON" atau parameter `?set=`.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENDERER = HERE.parent / "assets" / "exam-app" / "index.html"
KINDS = {"mc", "multi", "num", "essay"}


def check(exam: dict) -> list[str]:
    err: list[str] = []
    for k in ("id", "title", "duration_minutes", "sections", "questions"):
        if k not in exam:
            err.append(f"field wajib hilang: {k}")
    if err:
        return err
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", exam["id"]):
        err.append(f"id set harus kebab-case: {exam['id']}")
    secs = {s["id"] for s in exam["sections"]}
    groups = {g["id"] for g in exam.get("groups", [])}
    seen = set()
    for q in exam["questions"]:
        qid = q.get("id", "?")
        if qid in seen:
            err.append(f"id soal ganda: {qid}")
        seen.add(qid)
        for k in ("id", "section", "kind", "prompt", "solution", "points"):
            if k not in q:
                err.append(f"{qid}: field wajib hilang: {k}")
        if q.get("section") not in secs:
            err.append(f"{qid}: section {q.get('section')} tidak ada")
        if q.get("group") and q["group"] not in groups:
            err.append(f"{qid}: group {q['group']} tidak ada")
        kind = q.get("kind")
        if kind not in KINDS:
            err.append(f"{qid}: kind tidak dikenal: {kind}")
        elif kind == "num" and not isinstance(q.get("answer"), (int, float)):
            err.append(f"{qid}: answer num harus angka")
        elif kind == "mc" and not (isinstance(q.get("answer"), int) and 0 <= q["answer"] < len(q.get("options", []))):
            err.append(f"{qid}: answer mc harus indeks opsi yang sah")
        elif kind == "multi" and not (q.get("answer") and all(isinstance(i, int) and 0 <= i < len(q.get("options", [])) for i in q["answer"])):
            err.append(f"{qid}: answer multi harus daftar indeks opsi yang sah")
        elif kind == "essay" and not (q.get("rubric") and q.get("model_answer")):
            err.append(f"{qid}: essay butuh rubric dan model_answer")
        if "\u2014" in json.dumps(q, ensure_ascii=False):
            err.append(f"{qid}: memuat em dash")
    total = sum(q.get("points", 0) for q in exam["questions"])
    target = sum(s.get("points", 0) for s in exam["sections"])
    if target and abs(total - target) > 0.05:
        err.append(f"total poin soal {total:.2f} tidak sama dengan total section {target}")
    return err


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("sets", nargs="+", type=Path)
    b = sub.add_parser("build"); b.add_argument("sets", nargs="+", type=Path)
    b.add_argument("--out", type=Path, required=True); b.add_argument("--inline", type=Path)
    a = ap.parse_args()

    exams = [(p, load(p)) for p in a.sets]
    bad = 0
    for p, e in exams:
        err = check(e)
        n = len(e.get("questions", []))
        print(f"{p.name}: {n} soal, {'LOLOS' if not err else 'GAGAL'}")
        for x in err:
            print("   ", x)
        bad += bool(err)
    if bad or a.cmd == "check":
        return 1 if bad else 0

    out: Path = a.out
    (out / "sets").mkdir(parents=True, exist_ok=True)
    html = RENDERER.read_text(encoding="utf-8").replace("__DEFAULT_SET__", exams[0][1]["id"])
    (out / "index.html").write_text(html, encoding="utf-8")
    for p, e in exams:
        body = json.dumps(e, ensure_ascii=False, indent=1)
        (out / "sets" / f"{e['id']}.json").write_text(body + "\n", encoding="utf-8")
        (out / "sets" / f"{e['id']}.js").write_text(
            "// Dibuat build_exam_app.py dari " + e["id"] + ".json. Jangan diedit; edit JSON-nya lalu build ulang.\n"
            f"(window.EXAM_SETS = window.EXAM_SETS || {{}})[{json.dumps(e['id'])}] = {body};\n", encoding="utf-8")
    print(f"Ditulis: {out}/index.html dan {len(exams)} set di {out}/sets/")
    if a.inline:
        data = json.dumps(exams[0][1], ensure_ascii=False).replace("</", "<\\/")
        a.inline.write_text(html.replace("/*EXAM_DATA*/", data), encoding="utf-8")
        print(f"Ditulis versi satu berkas: {a.inline}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
