#!/usr/bin/env python3
"""Salin materi kuliah KASDAD ke korpus skill, tanpa pernah menghapus versi lama.

Pemakaian, dari folder produk (atau tambahkan --product <folder produk>):

    python3 scripts/sync_sources.py --course-dir '<folder kasdad_agu-2026>'
    python3 scripts/sync_sources.py --course-dir '<folder>' --check

Yang dilakukan:
1. Membaca pola `include` di sources/topics.json, relatif terhadap folder kuliah.
2. Menghitung SHA-256 tiap berkas. Berkas yang hash-nya sudah tercatat dilewati.
3. Menyalin berkas baru ke sources/files/<path relatif yang sama>. Bila namanya
   sudah dipakai versi lain, salinan baru diberi akhiran 8 karakter hash, dan
   catatan lama diberi `superseded_by`.
4. Menentukan topik dan jenis dari aturan di topics.json. Berkas tanpa topik
   ditandai `unassigned` dan dilaporkan, supaya peta topiknya dilengkapi dulu.
5. Untuk PDF, menulis ekstrak teks per halaman ke sources/text/<id>.txt dengan
   penanda `[Halaman N]`, lewat `pdftotext -layout`. Halaman tanpa teks diberi
   penanda `[TANPA TEKS]` agar dibaca lewat gambar.

`--check` tidak menyalin apa pun. Ia memeriksa hash semua salinan dan
melaporkan berkas di folder kuliah yang belum masuk korpus.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

# Folder produk mata kuliah. Default: induk folder scripts/ tempat skrip ini disalin.
# Dari course-to-skill, panggil dengan --product <folder produk>.
REPO = Path(__file__).resolve().parents[1]
SOURCES = MANIFEST = TOPICS = None


def set_product(path: Path) -> None:
    global REPO, SOURCES, MANIFEST, TOPICS
    REPO = path.resolve(); SOURCES = REPO / "sources"
    MANIFEST = SOURCES / "manifest.json"; TOPICS = SOURCES / "topics.json"
    if not TOPICS.exists():
        raise SystemExit(f"Tidak ada {TOPICS}. Buat produk dulu dengan new_course.py.")


# Ekstraktor .pptx/.docx/.xlsx milik skill buat-mindmap, bila terpasang.
EKSTRAK = Path.home() / ".claude" / "skills" / "buat-mindmap" / "scripts" / "ekstrak_teks.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_config() -> dict:
    return json.loads(TOPICS.read_text(encoding="utf-8"))


def candidates(course_dir: Path, patterns: list[str]) -> list[Path]:
    found: set[Path] = set()
    for path in course_dir.rglob("*"):
        if not path.is_file() or path.name.startswith((".", "~$")):
            continue
        rel = path.relative_to(course_dir).as_posix()
        # `*` di fnmatch melintasi `/`. Kedalaman folder pola dan berkas wajib
        # sama, supaya `*.pdf` tidak menyedot PDF di dalam .venv atau subfolder lain.
        if any(rel.count("/") == pat.count("/") and fnmatch.fnmatchcase(rel, pat) for pat in patterns):
            found.add(path)
    return sorted(found)


def classify(rel: str, cfg: dict) -> tuple[list[str], str]:
    low = rel.lower()
    topics = [t["id"] for t in cfg["topics"] if any(m in low for m in t["match"])]
    kind = "other"
    for rule in cfg["kinds"]:
        if Path(low).suffix in rule["ext"] and any(m in low for m in rule["match"]):
            kind = rule["kind"]
            break
    return topics or ["unassigned"], kind


def extract_pdf(src: Path, dst: Path) -> int:
    if not shutil.which("pdftotext"):
        print(f"PERINGATAN: pdftotext tidak ada, ekstrak teks {src.name} dilewati", file=sys.stderr)
        return 0
    out = subprocess.run(["pdftotext", "-layout", str(src), "-"], capture_output=True, text=True)
    pages = out.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    parts = []
    for i, page in enumerate(pages, 1):
        body = page.rstrip()
        marker = "" if len(body.strip()) > 20 else "\n[TANPA TEKS: baca halaman ini sebagai gambar]"
        parts.append(f"[Halaman {i}]\n{body}{marker}\n")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(f"Sumber: {src.name}\n\n" + "\n".join(parts), encoding="utf-8")
    return len(pages)


def html_to_text(src: Path) -> str:
    raw = src.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S | re.I)
    raw = re.sub(r"<br\s*/?>|</(p|div|h[1-6]|li|tr)>", "\n", raw, flags=re.I)
    raw = html.unescape(re.sub(r"<[^>]+>", "", raw))
    raw = re.sub(r"\n\s*\n+", "\n\n", raw).strip()
    return f"Sumber: {src.name}\n\n{raw}\n"


def sync(course_dir: Path) -> dict:
    cfg = load_config()
    prior = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"schema_version": 1, "sources": []}
    records = prior["sources"]
    known = {r["sha256"] for r in records}
    for src in candidates(course_dir, cfg["include"]):
        rel = src.relative_to(course_dir).as_posix()
        digest = sha256(src)
        if digest in known:
            continue
        topics, kind = classify(rel, cfg)
        target = SOURCES / "files" / rel
        if target.exists() and sha256(target) != digest:
            target = target.with_name(f"{target.stem}-{digest[:8]}{target.suffix}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        rid = f"{topics[0]}-{digest[:12]}"
        record = {
            "id": rid,
            "topics": topics,
            "kind": kind,
            "path": target.relative_to(REPO).as_posix(),
            "original_path": rel,
            "sha256": digest,
            "bytes": target.stat().st_size,
            "added_on": date.today().isoformat(),
        }
        if src.suffix.lower() == ".pdf":
            text = SOURCES / "text" / f"{rid}.txt"
            record["pages"] = extract_pdf(target, text)
            record["text_path"] = text.relative_to(REPO).as_posix()
        elif src.suffix.lower() == ".md":
            record["text_path"] = record["path"]
        elif src.suffix.lower() in {".html", ".htm"}:
            text = SOURCES / "text" / f"{rid}.txt"
            text.parent.mkdir(parents=True, exist_ok=True)
            text.write_text(html_to_text(target), encoding="utf-8")
            record["text_path"] = text.relative_to(REPO).as_posix()
        elif src.suffix.lower() in {".pptx", ".docx", ".xlsx"} and EKSTRAK.exists():
            text = SOURCES / "text" / f"{rid}.txt"
            text.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([sys.executable, str(EKSTRAK), str(target), "-o", str(text)], capture_output=True)
            record["text_path"] = text.relative_to(REPO).as_posix()
        else:
            record["needs_vision"] = True
        for old in records:
            if old["original_path"] == rel and "superseded_by" not in old:
                old["superseded_by"] = rid
        records.append(record)
        known.add(digest)
        flag = "  <-- PETAKAN TOPIKNYA di sources/topics.json" if topics == ["unassigned"] else ""
        print(f"ADDED {rid} [{kind}] {rel}{flag}")
    prior["sources"] = sorted(records, key=lambda r: (r["topics"][0], r["kind"], r["path"]))
    MANIFEST.write_text(json.dumps(prior, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return prior


def check(course_dir: Path) -> int:
    cfg = load_config()
    prior = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems = 0
    for r in prior["sources"]:
        p = REPO / r["path"]
        if not p.exists() or sha256(p) != r["sha256"]:
            print(f"RUSAK {r['id']} {r['path']}")
            problems += 1
        if r["topics"] == ["unassigned"]:
            print(f"BELUM DIPETAKAN {r['id']} {r['original_path']}")
            problems += 1
    known = {r["sha256"] for r in prior["sources"]}
    for src in candidates(course_dir, cfg["include"]):
        if sha256(src) not in known:
            print(f"BELUM MASUK {src.relative_to(course_dir).as_posix()}")
            problems += 1
    print(f"{len(prior['sources'])} sumber tercatat, {problems} masalah")
    return 1 if problems else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--course-dir", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--product", type=Path, help="folder produk mata kuliah; default induk folder skrip")
    a = ap.parse_args()
    set_product(a.product or Path(__file__).resolve().parents[1])
    if not a.course_dir.is_dir():
        raise SystemExit(f"Folder kuliah tidak ada: {a.course_dir}")
    if a.check:
        raise SystemExit(check(a.course_dir))
    result = sync(a.course_dir)
    print(f"TOTAL {len(result['sources'])} sumber")
