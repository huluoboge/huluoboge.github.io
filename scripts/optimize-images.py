#!/usr/bin/env python3
"""Optimize PNG/JPEG assets for faster mobile browsing.

Each file is processed at most once per content hash. Re-running the script
skips files that are already recorded in the manifest, which avoids repeated
lossy JPEG compression.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install with: python3 -m pip install Pillow"
    ) from exc

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path(__file__).resolve().parent / ".optimize-images-manifest.json"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__"}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest() -> dict[str, str]:
    if not MANIFEST.exists():
        return {}
    with MANIFEST.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_manifest(manifest: dict[str, str]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", encoding="utf-8") as handle:
        json.dump(dict(sorted(manifest.items())), handle, indent=2)
        handle.write("\n")


def iter_images(root: Path) -> list[Path]:
    images: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        images.append(path)
    return images


def max_width_for(path: Path) -> int:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "assets/hu-yang.jpg":
        return 640
    if rel.startswith("assets/projects/"):
        return 960
    return 1400


def jpeg_quality_for(path: Path) -> int:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "assets/hu-yang.jpg":
        return 88
    return 82


def resize_if_needed(image: Image.Image, max_width: int) -> Image.Image:
    width, height = image.size
    if width <= max_width:
        return image
    new_height = max(1, round(height * max_width / width))
    return image.resize((max_width, new_height), Image.Resampling.LANCZOS)


def optimize_png(path: Path, max_width: int) -> tuple[int, int]:
    original_size = path.stat().st_size
    backup = path.with_suffix(path.suffix + ".orig")
    shutil.copy2(path, backup)
    with Image.open(path) as image:
        image = resize_if_needed(image.convert("RGBA"), max_width)

    try:
        if shutil.which("pngquant"):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            try:
                image.save(tmp_path, format="PNG")
                result = subprocess.run(
                    [
                        "pngquant",
                        "--quality=55-90",
                        "--speed",
                        "1",
                        "--strip",
                        "--force",
                        "--output",
                        str(path),
                        str(tmp_path),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode not in (0,):
                    if result.returncode == 99:
                        image.save(path, format="PNG", optimize=True)
                    else:
                        stderr = result.stderr.strip() or result.stdout.strip()
                        raise RuntimeError(stderr or f"pngquant failed with code {result.returncode}")
            finally:
                tmp_path.unlink(missing_ok=True)
        else:
            image.save(path, format="PNG", optimize=True)

        if path.stat().st_size >= original_size:
            shutil.move(backup, path)
        else:
            backup.unlink(missing_ok=True)
    except Exception:
        shutil.move(backup, path)
        raise

    return original_size, path.stat().st_size


def optimize_jpeg(path: Path, max_width: int, quality: int) -> tuple[int, int]:
    original_size = path.stat().st_size
    backup = path.with_suffix(path.suffix + ".orig")
    shutil.copy2(path, backup)
    try:
        with Image.open(path) as image:
            image = image.convert("RGB")
            image = resize_if_needed(image, max_width)
            image.save(path, format="JPEG", quality=quality, optimize=True, progressive=True)

        if path.stat().st_size >= original_size:
            shutil.move(backup, path)
        else:
            backup.unlink(missing_ok=True)
    except Exception:
        shutil.move(backup, path)
        raise

    return original_size, path.stat().st_size


def optimize_file(path: Path) -> tuple[int, int] | None:
    suffix = path.suffix.lower()
    max_width = max_width_for(path)
    if suffix == ".png":
        return optimize_png(path, max_width)
    return optimize_jpeg(path, max_width, jpeg_quality_for(path))


def human_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.2f} MB"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to scan (default: project root)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-optimize even when the manifest already records this file hash",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would be optimized without writing changes",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = load_manifest()
    images = iter_images(root)

    if not shutil.which("pngquant"):
        png_count = sum(1 for path in images if path.suffix.lower() == ".png")
        if png_count:
            print("Warning: pngquant is not installed; PNG files will use Pillow only.", file=sys.stderr)

    changed = 0
    skipped = 0
    saved = 0

    for path in images:
        rel = path.relative_to(root).as_posix()
        digest = file_hash(path)
        if not args.force and manifest.get(rel) == digest:
            skipped += 1
            continue

        if args.dry_run:
            print(f"would optimize: {rel} ({human_size(path.stat().st_size)})")
            changed += 1
            continue

        before, after = optimize_file(path)
        new_digest = file_hash(path)
        manifest[rel] = new_digest
        delta = before - after
        saved += max(delta, 0)
        changed += 1
        sign = "-" if delta >= 0 else "+"
        print(
            f"optimized: {rel}  {human_size(before)} -> {human_size(after)} "
            f"({sign}{human_size(abs(delta))})"
        )

    if not args.dry_run:
        save_manifest(manifest)

    print(
        f"done: {changed} optimized, {skipped} skipped, "
        f"{human_size(saved)} saved"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
