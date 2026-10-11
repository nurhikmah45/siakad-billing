#!/usr/bin/env bash
# The Fresh Clone Test: clone repo ke folder kosong, install dari lockfile,
# salin .env.example -> .env, lalu jalankan lint + test.
# Pakai: bash scripts/fresh_clone_test.sh <URL-atau-path-repo>
set -euo pipefail

REPO="${1:-$(git rev-parse --show-toplevel)}"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

echo "==> [1/5] Clone ke folder bersih: $WORKDIR"
git clone --quiet "$REPO" "$WORKDIR/repo"
cd "$WORKDIR/repo"

echo "==> [2/5] Install dependensi persis sesuai lockfile (uv sync --frozen)"
uv sync --frozen

echo "==> [3/5] Siapkan konfigurasi: cp .env.example .env"
cp .env.example .env

echo "==> [4/5] Lint (ruff)"
uv run ruff check .

echo "==> [5/5] Test (pytest) + demo"
uv run pytest -q
uv run python -m siakad_billing

echo ""
echo "FRESH CLONE TEST: LULUS"
