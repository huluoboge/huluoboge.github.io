#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/optimize-images.sh [--dry-run] [--force]

Optimizes PNG and JPEG assets for faster mobile browsing.

Behavior:
  - PNG: resize when needed, then quantize with pngquant (Pillow fallback)
  - JPEG: resize and compress once per file content hash
  - Skips files already recorded in scripts/.optimize-images-manifest.json

Options:
  --dry-run   Show files that would be optimized
  --force     Re-optimize even when manifest already matches
  -h, --help  Show this help
USAGE
}

ARGS=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run|--force)
      ARGS+=("$1")
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: ${PYTHON_BIN} is required." >&2
  exit 1
fi

if ! "${PYTHON_BIN}" -c "from PIL import Image" >/dev/null 2>&1; then
  echo "Error: Pillow is required. Install with: ${PYTHON_BIN} -m pip install Pillow" >&2
  exit 1
fi

if ! command -v pngquant >/dev/null 2>&1; then
  echo "Warning: pngquant not found; PNG optimization will be weaker." >&2
  echo "Install on Debian/Ubuntu with: sudo apt install pngquant" >&2
fi

exec "${PYTHON_BIN}" "${ROOT_DIR}/scripts/optimize-images.py" "${ARGS[@]}"
