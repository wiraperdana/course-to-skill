#!/usr/bin/env python3
"""Bangun mindmap .xmind multi-sheet dari outline konsep, dengan catatan isi slide.

Setiap konsep dipecah menjadi cabang elemen penjelasan yang diisi saja, dari
katalog 14 elemen opsional: Definisi, Jenis/komponen, Tujuan, Kapan, Asumsi,
Urutan, Langkah, Contoh, Interpretasi, Pembeda, Hubungan, Kelebihan/kekurangan,
Jebakan, Catatan. Setiap node konsep diberi catatan Xmind berisi rujukan slide
dan teks slide yang dirujuk, ditarik dari korpus produk mata kuliah
(sources/manifest.json). Halaman yang isinya hanya gambar diisi dari berkas
transkripsi; yang belum ditranskripsi dilaporkan supaya dibaca dulu.

Dua opsi menentukan bentuk mindmap (lihat references/mindmap-spec.md):

    --isi  penjelasan (default)  konsep ditulis sebagai objek berelemen
           ringkasan             label pendek saja; objek konsep ditolak
    --alur kronologi (default)   sheet dan bagian mengikuti urutan slide; bagian
                                 dan konsep diberi nomor; rujukan tidak boleh mundur
           konsep                dikelompokkan menurut topik, tanpa nomor

Pemakaian:

    python3 build_mindmap.py <outline.json> --product <folder produk> -o <hasil.xmind>
        [--isi penjelasan|ringkasan] [--alur kronologi|konsep]
        [--transkripsi gambar.json] [--paksa]

Format outline:

    {"sheets": [
      {"title": "07a. CART", "children": [
        {"title": "Algoritma CART", "sumber": "[07a] s19-23", "children": [
          {"concept": "Nama konsep", "definisi": "...", "tujuan": "...",
           "urutan": "tahap tanpa hitungan" | ["tahap 1", "tahap 2"],
           "langkah": "rumus" | ["langkah 1", "langkah 2"],
           "hubungan": "...", "sumber": "[07a] s19-27"}
        ]}
      ]}
    ]}

Pada alur kronologi, rujukan pertama di "sumber" adalah tempat konsep dibahas
pada posisinya; rujukan lain menyusul. "sumber" di node bagian menjadi catatan
rentang slide tanpa teks.

Berkas transkripsi: {"07a:39": "isi gambar yang sudah dibaca", ...}.
Aturan bentuk tiap sheet mengikuti skill buat-mindmap: 4 sampai 7 cabang
utama, maksimal 5 anak, maksimal 70 node, label level 1-2 maks 5 kata,
level 3-4 maks 10 kata (nomor urut tidak dihitung), level 4 maks 15% node,
tanpa em dash.
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
NOMOR = re.compile(r"^\d+(\.\d+)*\.?\s+")


# Katalog elemen penjelasan. Semuanya opsional; pilih yang relevan dengan jenis
# konsep (lihat references/mindmap-spec.md). Urutan di sini = urutan tampil.
ELEMENTS = [
    ("definisi", "Definisi"), ("jenis", "Jenis/komponen"), ("tujuan", "Tujuan"), ("kapan", "Kapan"),
    ("asumsi", "Asumsi"), ("urutan", "Urutan"), ("langkah", "Langkah"), ("contoh", "Contoh"),
    ("interpretasi", "Interpretasi"), ("pembeda", "Pembeda"), ("hubungan", "Hubungan"),
    ("plusminus", "Kelebihan/kekurangan"), ("jebakan", "Jebakan"), ("catatan", "Catatan"),
]
LIST_TITLE = {"langkah": "Langkah matematis", "urutan": "Urutan"}


def words(t: str) -> int:
    return len(NOMOR.sub("", t).split())


def expand(node: dict) -> dict:
    """Ubah konsep menjadi node dengan cabang elemen yang diisi saja.

    Nilai string menjadi satu label "Elemen: isi". Nilai daftar menjadi node
    elemen dengan anak per butir (level 4), misalnya langkah bertahap."""
    if "concept" not in node:
        out = {"title": node["title"]}
        if node.get("sumber"):
            out["sumber"] = node["sumber"]
        if node.get("children"):
            out["children"] = [expand(c) for c in node["children"]]
        return out
    unknown = set(node) - {k for k, _ in ELEMENTS} - {"concept", "sumber"}
    if unknown:
        raise SystemExit(f"Elemen tidak dikenal pada '{node['concept']}': {sorted(unknown)}")
    anak = []
    for key, label in ELEMENTS:
        val = node.get(key)
        if not val:
            continue
        if isinstance(val, list):
            anak.append({"title": LIST_TITLE.get(key, label), "children": [{"title": v} for v in val]})
        else:
            anak.append({"title": f"{label}: {val}"})
    if len(anak) < 2:
        raise SystemExit(f"Konsep '{node['concept']}' butuh minimal 2 elemen")
    return {"title": node["concept"], "children": anak, "sumber": node.get("sumber", ""), "_konsep": True}


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
        if words(t) > KATA.get(lv, 10):
            err.append(f"label level {lv} {words(t)} kata: '{t}'")
        if len(n.get("children", []) or []) > 5:
            err.append(f"'{t}' punya lebih dari 5 anak")
        if "\u2014" in t or "$" in t:
            err.append(f"em dash atau LaTeX di label: '{t}'")
    for c in utama:
        depth = max(lv for lv, _ in walk(c))
        if depth < 2:
            err.append(f"cabang '{c['title']}' belum mencapai level 3")
    return err


def check_isi(sheet: dict, isi: str) -> list[str]:
    konsep = sum(1 for _, n in walk(sheet) if n.get("_konsep"))
    if isi == "ringkasan" and konsep:
        return [f"--isi ringkasan, tetapi ada {konsep} objek konsep"]
    if isi == "penjelasan" and not konsep:
        return ["--isi penjelasan, tetapi tidak ada objek konsep; pakai --isi ringkasan bila disengaja"]
    return []


def posisi(sumber: str):
    """Rujukan pertama "[kode] sN" sebagai kunci urut, atau None."""
    m = re.search(r"\[(\w+)\]\s*s(\d+)", sumber or "")
    return (m.group(1), int(m.group(2))) if m else None


def check_urutan(sheet: dict) -> list[str]:
    """Alur kronologi: rujukan pertama tiap bagian dan konsep tidak boleh mundur."""
    err, lalu = [], None
    for _, n in walk(sheet):
        p = posisi(n.get("sumber", ""))
        if p is None:
            continue
        if lalu and p < lalu[0]:
            err.append(f"urutan mundur: '{n['title']}' ({n['sumber']}) setelah '{lalu[1]}' ({lalu[2]})")
        lalu = (p, n["title"], n["sumber"])
    return err


def beri_nomor(sheet: dict) -> None:
    for i, bag in enumerate(sheet.get("children") or [], 1):
        if not NOMOR.match(bag["title"]):
            bag["title"] = f"{i}. {bag['title']}"
        for j, k in enumerate(bag.get("children") or [], 1):
            if not NOMOR.match(k["title"]):
                k["title"] = f"{i}.{j} {k['title']}"


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
        # Aturan gaya pengguna melarang em dash di semua berkas, termasuk kutipan slide.
        return re.sub(r"\s+", " ", body.replace("\u2014", "-")).strip()

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
        isi = slides.catatan(n["sumber"], n["title"]) if n.get("_konsep") else f"Bagian materi: {n['sumber']}"
        t["notes"] = {"plain": {"content": isi}}
    if n.get("children"):
        t["children"] = {"attached": [topik(c, slides) for c in n["children"]]}
    return t


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outline", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--product", type=Path, help="folder produk mata kuliah (berisi sources/manifest.json)")
    ap.add_argument("--transkripsi", type=Path, help="JSON {'kode:halaman': 'isi gambar'}")
    ap.add_argument("--isi", choices=["penjelasan", "ringkasan"], default="penjelasan")
    ap.add_argument("--alur", choices=["kronologi", "konsep"], default="kronologi")
    ap.add_argument("--paksa", action="store_true", help="tulis walau ada error bentuk")
    a = ap.parse_args()

    raw = json.loads(a.outline.read_text(encoding="utf-8"))
    sheets = [expand(s) for s in raw["sheets"]]
    trans = json.loads(a.transkripsi.read_text(encoding="utf-8")) if a.transkripsi else {}
    slides = Slides(a.product, trans)

    print(f"Opsi: --isi {a.isi} --alur {a.alur}")
    gagal = 0
    for s in sheets:
        err = check(s) + check_isi(s, a.isi)
        if a.alur == "kronologi":
            err += check_urutan(s)
            beri_nomor(s)
        n = sum(1 for lv, _ in walk(s) if lv > 0)
        k = sum(1 for _, x in walk(s) if x.get("_konsep"))
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
        z.writestr("metadata.json", json.dumps({"creator": {"name": "course-to-skill", "version": "1.1.0"}}))
        z.writestr("manifest.json", json.dumps({"file-entries": {"content.json": {}, "metadata.json": {}}}))
    print(f"Ditulis: {a.out} ({len(sheets)} sheet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
