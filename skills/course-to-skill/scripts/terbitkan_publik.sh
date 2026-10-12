#!/usr/bin/env bash
# Terbitkan versi publik produk mata kuliah, tanpa materi pihak ketiga.
#
# Repo ini (private) menyimpan semuanya, termasuk slide dosen dan catatan
# kelas. Versi publik dibangun dari HEAD dengan membuang setiap path di
# berkas .publik-kecuali, lalu di-push ke remote "publik" sebagai commit
# lanjutan riwayat publik. Working tree dan riwayat private tidak disentuh,
# dan riwayat publik tidak pernah memuat materi yang dikecualikan.
#
# Pemakaian (dari root produk):
#   scripts/terbitkan_publik.sh            bangun dan push
#   scripts/terbitkan_publik.sh --cek      tampilkan isi yang akan terbit, tanpa push
#
# Persiapan sekali: git remote add publik https://github.com/<owner>/<repo-publik>.git
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
[[ -f .publik-kecuali ]] || { echo "Berkas .publik-kecuali tidak ada"; exit 1; }
KECUALI=()
while IFS= read -r baris; do KECUALI+=("$baris"); done < <(grep -v -E '^[[:space:]]*(#|$)' .publik-kecuali)

KERJA="$(mktemp -d)"
trap 'rm -rf "$KERJA"' EXIT
export GIT_INDEX_FILE="$KERJA/index"
git read-tree HEAD
git rm -r -q --cached --ignore-unmatch -- "${KECUALI[@]}"

# .gitignore publik ikut mengabaikan path yang dikecualikan, supaya korpus
# yang dibangun ulang pemakai lain tidak ikut ter-commit.
{ git show HEAD:.gitignore 2>/dev/null || true
  printf '\n# Materi pihak ketiga, tidak diterbitkan (lihat .publik-kecuali)\n'
  printf '%s\n' "${KECUALI[@]}"; } > "$KERJA/gitignore"
git update-index --add --cacheinfo "100644,$(git hash-object -w "$KERJA/gitignore"),.gitignore"
TREE="$(git write-tree)"

if [[ "${1:-}" == "--cek" ]]; then
  git ls-tree -r --name-only "$TREE"
  echo "($(git ls-tree -r --name-only "$TREE" | wc -l | tr -d ' ') berkas akan terbit)"
  exit 0
fi

git fetch -q publik 2>/dev/null || true
INDUK="$(git rev-parse -q --verify refs/remotes/publik/main || true)"
if [[ -n "$INDUK" && "$(git rev-parse "$INDUK^{tree}")" == "$TREE" ]]; then
  echo "Versi publik sudah terbaru."
  exit 0
fi
PESAN="$(git log -1 --format=%B HEAD)"
COMMIT="$(git commit-tree "$TREE" ${INDUK:+-p "$INDUK"} -m "$PESAN")"
git push -q publik "$COMMIT:refs/heads/main"
git fetch -q publik
echo "Terbit: $COMMIT"
