"""Reproduce MoGe paper figure crops from the authors' published PDFs.

Sources:
  CVPR 2025: https://openaccess.thecvf.com/content/CVPR2025/papers/
    Wang_MoGe_Unlocking_Accurate_Monocular_Geometry_Estimation_for_Open-Domain_Images_with_CVPR_2025_paper.pdf
  arXiv v3: https://arxiv.org/pdf/2410.19115v3

Usage:
  python tools/paper-figures/extract_moge_figures.py /path/to/cvpr.pdf /path/to/arxiv-v3.pdf

The PDFs are inputs only; keep them outside the repository.
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "blog/articles/moge/figures"

# (PDF, page, output name, crop in PDF coordinates rendered at 150 dpi).
CROPS = (
    ("cvpr", 1, "paper-figure-1.png", (128, 455, 1150, 817)),
    ("cvpr", 2, "paper-figure-2.png", (120, 155, 615, 445)),
    ("cvpr", 7, "paper-figure-6.png", (120, 155, 1155, 335)),
    ("cvpr", 8, "paper-figure-7.png", (120, 145, 1155, 930)),
    ("arxiv", 18, "paper-supp-figure-9.png", (640, 1197, 1167, 1344)),
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cvpr_pdf", type=Path)
    parser.add_argument("arxiv_pdf", type=Path)
    args = parser.parse_args()

    sources = {"cvpr": args.cvpr_pdf, "arxiv": args.arxiv_pdf}
    OUTPUT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="moge-figures-") as tmp:
        for source, page, name, crop_150dpi in CROPS:
            rendered = Path(tmp) / f"{source}-{page}.png"
            subprocess.run(
                [
                    "gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE",
                    "-sDEVICE=png16m", "-r300",
                    f"-dFirstPage={page}", f"-dLastPage={page}",
                    f"-sOutputFile={rendered}", str(sources[source]),
                ],
                check=True,
            )
            with Image.open(rendered) as image:
                box = tuple(coordinate * 2 for coordinate in crop_150dpi)
                image.crop(box).save(OUTPUT / name, optimize=True)
            print(OUTPUT / name)


if __name__ == "__main__":
    main()
