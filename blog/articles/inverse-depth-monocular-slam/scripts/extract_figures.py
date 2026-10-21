"""Crop the numbered figures from the published T-RO PDF.

Usage: python extract_figures.py /path/to/civera_etal_tro2008.pdf
Requires Poppler (pdftoppm) and Pillow. Crop boxes are in PDF points.
"""

from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image


FIGURES = {
    1: (4, (297, 62, 558, 237)),
    2: (5, (300, 62, 557, 153)),
    3: (5, (300, 183, 557, 321)),
    4: (7, (305, 62, 557, 197)),
    5: (8, (37, 62, 291, 244)),
    6: (8, (50, 269, 291, 369)),
    7: (8, (296, 62, 556, 266)),
    8: (9, (40, 62, 294, 439)),
    9: (9, (301, 62, 557, 145)),
    10: (10, (36, 62, 291, 467)),
    11: (10, (296, 62, 556, 286)),
    12: (11, (100, 62, 232, 179)),
    13: (11, (40, 243, 293, 514)),
    14: (11, (301, 62, 557, 211)),
    15: (12, (37, 62, 291, 248)),
}


def main():
    pdf = Path(sys.argv[1]).resolve()
    destination = Path(__file__).resolve().parent.parent / "figures"
    destination.mkdir(exist_ok=True)
    dpi = 300
    with tempfile.TemporaryDirectory(prefix="inverse-depth-figures-") as directory:
        for page in sorted({page for page, _ in FIGURES.values()}):
            prefix = Path(directory) / f"page-{page}"
            subprocess.run(
                ["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi),
                 "-singlefile", "-png", str(pdf), str(prefix)], check=True,
            )
            with Image.open(prefix.with_suffix(".png")) as image:
                for number, (figure_page, points) in FIGURES.items():
                    if page != figure_page:
                        continue
                    box = tuple(round(point * dpi / 72) for point in points)
                    output = destination / f"paper-fig-{number:02}.png"
                    image.crop(box).save(output, optimize=True)
                    print(output.name, box)


if __name__ == "__main__":
    main()
