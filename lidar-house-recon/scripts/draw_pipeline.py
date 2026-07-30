#!/usr/bin/env python3
"""Draw the LiDAR building reconstruction pipeline figure in English."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "figures" / "fig1_pipeline.png"

YELLOW_FILL = "#FFF1B8"
YELLOW_EDGE = "#C9A227"
BLUE_FILL = "#D9EAF7"
BLUE_EDGE = "#4A7BA7"
TEXT_COLOR = "#1A1A1A"
GROUP_EDGE = "#888888"
ARROW_COLOR = "#444444"


def wrap_label(text: str, width: int = 22) -> str:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if len(trial) <= width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def draw_parallelogram(ax, center, width, height, text, facecolor, edgecolor, skew=0.18):
    cx, cy = center
    hw, hh = width / 2, height / 2
    points = [
        (cx - hw + skew, cy - hh),
        (cx + hw + skew, cy - hh),
        (cx + hw - skew, cy + hh),
        (cx - hw - skew, cy + hh),
    ]
    patch = Polygon(
        points,
        closed=True,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.2,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        cx,
        cy,
        wrap_label(text),
        ha="center",
        va="center",
        fontsize=9.5,
        color=TEXT_COLOR,
        linespacing=1.2,
        zorder=3,
    )
    return points


def draw_box(ax, center, width, height, text, facecolor, edgecolor):
    cx, cy = center
    patch = FancyBboxPatch(
        (cx - width / 2, cy - height / 2),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.2,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        cx,
        cy,
        wrap_label(text),
        ha="center",
        va="center",
        fontsize=9.5,
        color=TEXT_COLOR,
        linespacing=1.2,
        zorder=3,
    )
    return (cx, cy - height / 2), (cx, cy + height / 2)


def draw_group_box(ax, xy, width, height, label):
    x, y = xy
    patch = Rectangle(
        (x, y),
        width,
        height,
        fill=False,
        edgecolor=GROUP_EDGE,
        linewidth=1.0,
        linestyle=(0, (5, 4)),
        zorder=0,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height + 0.12,
        label,
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        color=TEXT_COLOR,
        zorder=1,
    )


def arrow(ax, start, end, connectionstyle="arc3,rad=0.0", shrink_a=4, shrink_b=4):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=11,
        linewidth=1.0,
        color=ARROW_COLOR,
        connectionstyle=connectionstyle,
        shrinkA=shrink_a,
        shrinkB=shrink_b,
        zorder=1,
    )
    ax.add_patch(patch)


def build_figure():
    fig, ax = plt.subplots(figsize=(11.5, 12.5), dpi=160)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    left_x = 2.35
    right_x = 7.45
    box_w, box_h = 3.15, 0.72
    para_w, para_h = 3.15, 0.72

    ys = [10.8, 9.85, 8.9, 7.95, 7.0, 6.05, 5.1, 4.15, 3.2, 2.25, 1.3]

    draw_group_box(ax, (0.55, 0.55), 4.35, 10.95, "Building Reconstruction")
    draw_group_box(ax, (5.55, 6.55), 4.35, 4.75, "Aerial Triangulation & Registration")

    left_nodes = [
        ("para", "Point Cloud"),
        ("box", "Preprocessing, Filtering, and Classification"),
        ("para", "Building Point Cloud"),
        ("box", "Plane Segmentation"),
        ("box", "Boundary Extraction and Regularization"),
        ("para", "Building Roof Outlines"),
        ("box", "Automatic 3D Topology Establishment"),
        ("para", "Building Vector Model"),
        ("box", "Texture Mapping"),
        ("para", "Textured Building Model"),
    ]

    right_nodes = [
        ("para", "Aerial Imagery"),
        ("box", "Image Preprocessing"),
        ("box", "Point Cloud Assisted Aerial Triangulation"),
        ("box", "POS-assisted Block Adjustment"),
        ("para", "Registered Imagery"),
    ]

    left_centers: list[tuple[float, float]] = []
    right_centers: list[tuple[float, float]] = []

    for y, (kind, label) in zip(ys[: len(left_nodes)], left_nodes):
        center = (left_x, y)
        left_centers.append(center)
        if kind == "para":
            draw_parallelogram(ax, center, para_w, para_h, label, YELLOW_FILL, YELLOW_EDGE)
        else:
            draw_box(ax, center, box_w, box_h, label, YELLOW_FILL, YELLOW_EDGE)

    for y, (kind, label) in zip(ys[: len(right_nodes)], right_nodes):
        center = (right_x, y)
        right_centers.append(center)
        if kind == "para":
            draw_parallelogram(ax, center, para_w, para_h, label, BLUE_FILL, BLUE_EDGE)
        else:
            draw_box(ax, center, box_w, box_h, label, BLUE_FILL, BLUE_EDGE)

    outline_center = (4.9, 6.05)
    draw_box(ax, outline_center, 2.35, 0.72, "Outline Correction", YELLOW_FILL, YELLOW_EDGE)

    for i in range(len(left_centers) - 1):
        if i == 4:
            continue
        arrow(ax, (left_centers[i][0], left_centers[i][1] - para_h / 2), (left_centers[i + 1][0], left_centers[i + 1][1] + para_h / 2))

    for i in range(len(right_centers) - 1):
        arrow(ax, (right_centers[i][0], right_centers[i][1] - para_h / 2), (right_centers[i + 1][0], right_centers[i + 1][1] + para_h / 2))

    arrow(
        ax,
        (left_centers[0][0] + para_w / 2 - 0.1, left_centers[0][1]),
        (right_centers[2][0] - box_w / 2 + 0.1, right_centers[2][1]),
        connectionstyle="arc3,rad=-0.18",
    )

    arrow(
        ax,
        (left_centers[4][0] + box_w / 2 - 0.05, left_centers[4][1]),
        (outline_center[0] - 1.0, outline_center[1]),
        connectionstyle="arc3,rad=0.0",
    )
    arrow(
        ax,
        (right_centers[4][0] - para_w / 2 + 0.05, right_centers[4][1]),
        (outline_center[0] + 1.0, outline_center[1]),
        connectionstyle="arc3,rad=0.0",
    )
    arrow(
        ax,
        (outline_center[0], outline_center[1] - box_h / 2),
        (left_centers[5][0], left_centers[5][1] + para_h / 2),
    )

    arrow(
        ax,
        (right_centers[4][0], right_centers[4][1] - para_h / 2),
        (left_centers[8][0] + 0.55, left_centers[8][1] + box_h / 2),
        connectionstyle="arc3,rad=-0.22",
    )

    return fig


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output PNG path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    fig.savefig(args.output, bbox_inches="tight", facecolor="white", pad_inches=0.25)
    plt.close(fig)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
