#!/usr/bin/env python3
"""Kompilasi catatan ujian A4 bolak-balik (LaTeX) dan pastikan tepat 2 halaman.

Pemakaian:
    python3 build_notes_a4.py <catatan.tex> [--out <hasil.pdf>] [--preview <folder>]

Mesin yang dicoba berurutan: tectonic, latexmk -pdf, pdflatex. Skrip gagal bila
hasil bukan 2 halaman A4, dan melaporkan baris yang menjorok (Overfull > 5pt)
supaya dirapikan. --preview merender PNG tiap halaman untuk dicek secara visual.
Template awal: assets/notes-a4/template.tex. Panduan isi: references/notes-a4-guide.md.
"""
from __future__ import annotations
import argparse, re, shutil, subprocess, sys
from pathlib import Path

def compile_tex(tex: Path) -> tuple[Path, str]:
    for cmd in (["tectonic", tex.name], ["latexmk", "-pdf", "-interaction=nonstopmode", tex.name], ["pdflatex", "-interaction=nonstopmode", tex.name]):
        if shutil.which(cmd[0]):
            r = subprocess.run(cmd, cwd=tex.parent, capture_output=True, text=True)
            log = r.stdout + r.stderr
            pdf = tex.with_suffix(".pdf")
            if r.returncode == 0 and pdf.exists():
                return pdf, log
            print(log[-3000:]); raise SystemExit(f"Kompilasi gagal dengan {cmd[0]}")
    raise SystemExit("Tidak ada mesin LaTeX (tectonic, latexmk, pdflatex). Pasang tectonic: brew install tectonic")

def pages(pdf: Path) -> int:
    if shutil.which("pdfinfo"):
        m = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout)
        if m: return int(m.group(1))
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex", type=Path); ap.add_argument("--out", type=Path); ap.add_argument("--preview", type=Path)
    a = ap.parse_args()
    src = a.tex.read_text(encoding="utf-8")
    if "\u2014" in src or "---" in src:
        print("PERINGATAN: ada em dash di sumber; ganti dengan koma atau titik.")
    pdf, log = compile_tex(a.tex.resolve())
    over = [(float(m.group(1)), m.group(0)) for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*", log)]
    for w, line in sorted(set(over), reverse=True):
        if w > 5: print("RAPIKAN:", line)
    n = pages(pdf)
    print(f"{pdf.name}: {n} halaman")
    if a.out:
        shutil.copy2(pdf, a.out); print("Disalin ke", a.out)
    if a.preview and shutil.which("pdftoppm"):
        a.preview.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-png", "-r", "90", str(pdf), str(a.preview / "halaman")])
        print("Pratinjau di", a.preview, "; lihat gambarnya untuk cek kolom kosong atau teks bertumpuk.")
    if n != 2:
        print("GAGAL: catatan harus tepat 2 halaman (1 lembar bolak-balik). Kurangi isi atau perkecil fontsize."); return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
