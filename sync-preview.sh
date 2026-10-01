#!/bin/bash
# Sincroniza sitio-tournesols/ al repo preview (GitHub Pages).
# Uso: ./sync-preview.sh
# Requiere: gh auth con permiso de push en Arvure-Solutions/sitio-tournesols.
set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"
SRC="$REPO_ROOT/sitio-tournesols"
CLONE_DIR="${SITEPUB_DIR:-/tmp/sitepub}"
find "$SRC" -name "._*" -delete
if [ ! -d "$CLONE_DIR/.git" ]; then
  git clone https://github.com/Arvure-Solutions/sitio-tournesols.git "$CLONE_DIR"
fi
git -C "$CLONE_DIR" fetch origin main 2>/dev/null || true
git -C "$CLONE_DIR" reset --hard origin/main 2>/dev/null || true
rsync -a --delete --exclude=.git "$SRC/" "$CLONE_DIR/"
find "$CLONE_DIR" -name "._*" -delete
git -C "$CLONE_DIR" add -A
if git -C "$CLONE_DIR" diff --cached --quiet; then
  echo "OK: preview ya estaba al día."
else
  git -C "$CLONE_DIR" commit -m "Sync sitio $(date +%Y-%m-%d %H:%M)" >/dev/null
  git -C "$CLONE_DIR" push origin main 2>&1 | grep -vE "non-monotonic" | tail -1
  echo "OK: preview sincronizado (https://arvure-solutions.github.io/sitio-tournesols/)"
fi
