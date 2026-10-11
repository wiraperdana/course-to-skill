#!/usr/bin/env python3
"""Bangun mindmap .xmind multi-sheet dari outline konsep, dengan catatan isi slide.

Setiap konsep otomatis dipecah menjadi tiga cabang: Definisi, Kapan, Langkah.
Setiap node konsep diberi catatan Xmind berisi rujukan slide dan teks slide
yang dirujuk, ditarik dari korpus produk mata kuliah (sources/manifest.json).
Halaman yang isinya hanya gambar diisi dari berkas transkripsi; yang belum
ditranskripsi dilaporkan supaya dibaca dulu.

Pemakaian:

    python3 build_mindmap.py <outline.json> --product <folder produk> -o <hasil.xmind>
        [--transkripsi gambar.json] [--paksa]

Format outline (lihat references/mindmap-spec.md):

    {"sheets": [
      {"title": "a. Topik", "children": [
        {"title": "Kelompok", "children": [
          {"concept": "Nama konsep", "definisi": "...", "kapan": "...",
           "langkah": "satu kalimat" | ["langkah 1", "langkah 2"],
           "sumber": "[05] s41-45; catatan sesi 5"}
        ]}
      ]}
    ]}

Berkas transkripsi: {"07a:39": "isi gambar yang sudah dibaca", ...}.
Aturan bentuk tiap sheet mengikuti skill buat-mindmap: 4 sampai 7 cabang
utama, maksimal 5 anak, maksimal 70 node, label level 1-2 maks 5 kata,
level 3-4 maks 10 kata, level 4 maks 15% node, tanpa em dash.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
import zipfile
from pathlib import Path

KATA = {1: 5, 2: 5, 3: 10, 4: 10}


def expand(node: dict) -> dict:
    """Ubah konsep {concept, definisi, kapan, langkah, sumber} menjadi node bertiga cabang."""
    if "concept" not in node:
        out = {"title": node["title"]}
        if node.get("children"):
            out["children"] = [expand(c) for c in node["children"]]
        return out
    anak = [{"title": "Definisi: " + node["definisi"]}, {"title": "Kapan: " + node["kapan"]}]
    lk = node["langkah"]
    anak.append({"title": "Langkah matematis", "children": [{"title": s} for s in lk]} if isinstance(lk, list)
                else {"title": "Langkah: " + lk})
    return {"title": node["concept"], "children": anak, "sumber": node.get("sumber", "")}


def walk(n: dict, lv: int = 0):
    yield lv, n
    for c in n.get("children", []) or []:
        yield from walk(c, lv + 1)


def check(sheet: dict) -> list[str]:
    err = []
    utama = sheet.get("children", [])
    if not 4 <= len(utama) <= 7:
        err.append(f"cabang utama {len(utama)}, harus 4-7")
    nodes = [(lv, n) for lv, n in walk(sheet) if lv > 0]
    if len(nodes) > 70:
        err.append(f"{len(nodes)} node, maksimal 70")
    l4 = sum(1 for lv, _ in nodes if lv == 4)
    if nodes and l4 / len(nodes) > 0.15:
        err.append(f"level 4 {l4} node ({l4 / len(nodes):.0%}), maksimal 15%")
    for lv, n in nodes:
        t = n["title"]
        if lv > 4:
            err.append(f"level {lv} dilarang: {t}")
        if len(t.split()) > KATA.get(lv, 10):
            err.append(f"label level {lv} {len(t.split())} kata: '{t}'")
        if len(n.get("children", []) or []) > 5:
            err.append(f"'{t}' punya lebih dari 5 anak")
        if "\u2014" in t or "$" in t:
            err.append(f"em dash atau LaTeX di label: '{t}'")
    for c in utama:
        depth = max(lv for lv, _ in walk(c))
        if depth < 2:
            err.append(f"cabang '{c['title']}' belum mencapai level 3")
    return err


class Slides:
    def __init__(self, product: Path | None, transkripsi: dict):
        self.teks, self.trans, self.gambar, self.masalah = {}, transkripsi, set(), []
        if not product:
            return
        man = json.loads((product / "sources" / "manifest.json").read_text(encoding="utf-8"))
        for r in man["sources"]:
            m = re.match(r"(?:.*/)?\[(\w+)\]", r["original_path"])
            if m and r.get("kind") == "slide" and r.get("text_path") and "superseded_by" not in r:
                self.teks[m.group(1)] = (product / r["text_path"]).read_text(encoding="utf-8")

    def halaman(self, kode: str, n: int) -> str | None:
        t = self.teks.get(kode)
        if t is None:
            return None
        a = t.find(f"[Halaman {n}]")
        if a < 0:
            return None
        b = t.find(f"[Halaman {n + 1}]", a)
        body = t[a + len(f"[Halaman {n}]"): b if b > 0 else None]
        body = re.sub(r"https?://\S+|\[TANPA TEKS[^\]]*\]", "", body)
        return re.sub(r"\s+", " ", body).strip()

    def catatan(self, sumber: str, judul: str) -> str:
        baris = [f"Sumber: {sumber}", ""]
        for kode, spec in re.findall(r"\[(\w+)\]\s*s([\d\-, ]+\d)", sumber):
            for part in spec.split(","):
                m = re.match(r"\s*(\d+)(?:-(\d+))?", part)
                if not m:
                    continue
                for n in range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1):
                    h = self.halaman(kode, n)
                    if h is None:
                        self.masalah.append(f"{judul}: [{kode}] s{n} tidak ditemukan di korpus")
                        continue
                    if len(h) < 40:
                        key = f"{kode}:{n}"
                        if key in self.trans:
                            h = (h + " [gambar, dibaca] " + self.trans[key]).strip()
                        else:
                            self.gambar.add(f"[{kode}] s{n}")
                            h = (h + " [isi utama berupa gambar, buka PDF slide]").strip()
                    baris.append(f"[{kode}] slide {n}: {h[:700]}")
        return "\n".join(baris)


def topik(n: dict, slides: Slides, akar: bool = False) -> dict:
    t = {"id": uuid.uuid4().hex, "class": "topic", "title": n["title"]}
    if akar:
        t["structureClass"] = "org.xmind.ui.map.unbalanced"
    if n.get("sumber"):
        t["notes"] = {"plain": {"content": slides.catatan(n["sumber"], n["title"])}}
    if n.get("children"):
        t["children"] = {"attached": [topik(c, slides) for c in n["children"]]}
    return t


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outline", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--product", type=Path, help="folder produk mata kuliah (berisi sources/manifest.json)")
    ap.add_argument("--transkripsi", type=Path, help="JSON {'kode:halaman': 'isi gambar'}")
    ap.add_argument("--paksa", action="store_true", help="tulis walau ada error bentuk")
    a = ap.parse_args()

    raw = json.loads(a.outline.read_text(encoding="utf-8"))
    sheets = [expand(s) for s in raw["sheets"]]
    trans = json.loads(a.transkripsi.read_text(encoding="utf-8")) if a.transkripsi else {}
    slides = Slides(a.product, trans)

    gagal = 0
    for s in sheets:
        err = check(s)
        n = sum(1 for lv, _ in walk(s) if lv > 0)
        k = sum(1 for lv, x in walk(s) if x.get("sumber") is not None)
        print(f"{s['title']}: {n} node, {k} konsep, {'LOLOS' if not err else 'GAGAL'}")
        for e in err:
            print("   ", e)
        gagal += bool(err)
    konten = [{"id": uuid.uuid4().hex, "class": "sheet", "title": s["title"], "rootTopic": topik(s, slides, True),
               "topicPositioning": "fixed"} for s in sheets]
    if slides.masalah:
        print("Rujukan bermasalah:", *slides.masalah, sep="\n   ")
    if slides.gambar:
        print(f"{len(slides.gambar)} halaman bergambar belum ditranskripsi:", ", ".join(sorted(slides.gambar)))
    if (gagal or slides.masalah) and not a.paksa:
        print("File .xmind tidak ditulis. Perbaiki outline atau rujukan, lalu ulangi.")
        return 1
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.json", json.dumps(konten, ensure_ascii=False))
        z.writestr("metadata.json", json.dumps({"creator": {"name": "course-to-skill", "version": "1.0.0"}}))
        z.writestr("manifest.json", json.dumps({"file-entries": {"content.json": {}, "metadata.json": {}}}))
    print(f"Ditulis: {a.out} ({len(sheets)} sheet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
