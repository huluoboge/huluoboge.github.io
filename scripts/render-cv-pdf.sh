#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-all}"

if command -v chromium >/dev/null 2>&1; then
  CHROME_BIN="chromium"
elif command -v chromium-browser >/dev/null 2>&1; then
  CHROME_BIN="chromium-browser"
elif command -v google-chrome >/dev/null 2>&1; then
  CHROME_BIN="google-chrome"
else
  echo "Error: chromium, chromium-browser, or google-chrome is required." >&2
  exit 1
fi

render_pdf() {
  local html_file="$1"
  local output_file="$2"

  "${CHROME_BIN}" \
    --headless \
    --disable-gpu \
    --no-sandbox \
    --print-to-pdf="${output_file}" \
    --print-to-pdf-no-header \
    "file://${html_file}"

  echo "Rendered ${output_file}"
}

case "${TARGET}" in
  all)
    render_pdf "${ROOT_DIR}/cv/index.html" "${ROOT_DIR}/assets/huyang-cv.pdf"
    render_pdf "${ROOT_DIR}/cv/en/index.html" "${ROOT_DIR}/assets/huyang-cv-en.pdf"
    ;;
  cn|zh)
    render_pdf "${ROOT_DIR}/cv/index.html" "${ROOT_DIR}/assets/huyang-cv.pdf"
    ;;
  en)
    render_pdf "${ROOT_DIR}/cv/en/index.html" "${ROOT_DIR}/assets/huyang-cv-en.pdf"
    ;;
  *)
    echo "Usage: $0 [all|cn|en]" >&2
    exit 1
    ;;
esac
