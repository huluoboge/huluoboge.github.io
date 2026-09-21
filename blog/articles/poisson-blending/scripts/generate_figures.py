#!/usr/bin/env python3
"""Generate SVG figures for the Poisson blending blog post."""

from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
NAVY = "#20344d"
BLUE = "#4e8dd8"
GREEN = "#55a868"
ORANGE = "#dd8452"
RED = "#c75b5b"
GRAY = "#e9edf3"
DARK = "#2f3640"
MUTED = "#6b7280"
WHITE = "#ffffff"


def rect(x, y, w, h, fill, stroke="#34495e", sw=1.5, rx=10):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def text(x, y, s, size=20, fill=DARK, weight="500", anchor="middle"):
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" '
        f'font-size="{size}" fill="{fill}" font-weight="{weight}">{s}</text>'
    )


def line(x1, y1, x2, y2, color=MUTED, sw=2, dash="", marker=True):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    marker_attr = ' marker-end="url(#arrow)"' if marker else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="{sw}"{marker_attr}{dash_attr}/>'
    )


def defs():
    return """<defs>
  <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
    <path d="M2,2 L10,6 L2,10 z" fill="#6b7280"/>
  </marker>
</defs>"""


def write_svg(path: Path, width: int, height: int, body: list[str]) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        defs(),
        rect(0, 0, width, height, WHITE, stroke=WHITE, sw=0, rx=0),
        *body,
        "</svg>",
    ]
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def fig_hard_vs_poisson() -> None:
    w, h = 1120, 620
    body = []
    body.append(text(w / 2, 42, "直接贴像素与梯度域融合的差别", 28, NAVY, "800"))
    body.append(
        text(
            w / 2,
            74,
            "左侧保留源图绝对亮度，边界容易断裂；右侧保留源图梯度，边界由目标图约束",
            16,
            MUTED,
            "500",
        )
    )

    # Left panel: hard paste
    # Background labels sit above the inset so they are never covered.
    body.append(rect(48, 110, 480, 460, "#f8fafc", stroke="#c5ccd6", sw=1.5, rx=16))
    body.append(text(288, 148, "直接贴像素", 22, NAVY, "800"))

    body.append(rect(90, 180, 400, 210, "#dce8f8", stroke=BLUE, sw=2, rx=12))
    body.append(text(290, 208, "目标图背景", 18, NAVY, "700"))
    body.append(text(290, 232, "边界亮度已经固定", 15, MUTED, "500"))
    body.append(rect(170, 250, 180, 110, "#ffe0c8", stroke=ORANGE, sw=2.5, rx=8))
    body.append(text(260, 295, "源图块", 18, NAVY, "800"))
    body.append(text(260, 325, "原样写入亮度", 14, MUTED, "500"))

    body.append(rect(90, 420, 400, 110, "#fde8e8", stroke=RED, sw=1.5, rx=10))
    body.append(text(290, 460, "边界处亮度突变", 18, RED, "700"))
    body.append(text(290, 492, "视觉上形成明显接缝或色差环", 15, MUTED, "500"))

    # Right panel: Poisson
    body.append(rect(592, 110, 480, 460, "#f8fafc", stroke="#c5ccd6", sw=1.5, rx=16))
    body.append(text(832, 148, "Poisson 融合", 22, NAVY, "800"))

    body.append(rect(634, 180, 400, 210, "#dce8f8", stroke=BLUE, sw=2, rx=12))
    body.append(text(834, 208, "目标图背景", 18, NAVY, "700"))
    body.append(text(834, 232, "边界亮度作为 Dirichlet 条件", 15, MUTED, "500"))
    body.append(rect(714, 250, 180, 110, "#dff3e4", stroke=GREEN, sw=2.5, rx=8))
    body.append(text(804, 295, "求解区域 Ω", 18, NAVY, "800"))
    body.append(text(804, 325, "内部保留源图梯度", 14, MUTED, "500"))

    body.append(rect(634, 420, 400, 110, "#e8f6ec", stroke=GREEN, sw=1.5, rx=10))
    body.append(text(834, 460, "边界连续，内部结构来自源图", 18, GREEN, "700"))
    body.append(text(834, 492, "绝对亮度被边界重新锚定", 15, MUTED, "500"))

    write_svg(OUT / "hard-paste-vs-poisson.svg", w, h, body)


def fig_poisson_flow() -> None:
    w, h = 1180, 720
    body = []
    body.append(text(w / 2, 42, "Poisson 融合的信息流", 28, NAVY, "800"))
    body.append(
        text(
            w / 2,
            74,
            "源图提供引导梯度，目标图提供边界亮度，求解 Poisson 方程得到融合结果",
            16,
            MUTED,
            "500",
        )
    )

    # Inputs
    body.append(rect(60, 130, 220, 100, "#ffe6d7", stroke=ORANGE, sw=2, rx=14))
    body.append(text(170, 172, "源图 g", 22, NAVY, "800"))
    body.append(text(170, 202, "待贴入内容", 15, MUTED, "500"))

    body.append(rect(60, 280, 220, 100, "#d9e9ff", stroke=BLUE, sw=2, rx=14))
    body.append(text(170, 322, "目标图 f*", 22, NAVY, "800"))
    body.append(text(170, 352, "背景与边界", 15, MUTED, "500"))

    body.append(rect(60, 430, 220, 100, GRAY, stroke="#8a8f98", sw=2, rx=14))
    body.append(text(170, 472, "区域 Ω / mask", 20, NAVY, "800"))
    body.append(text(170, 502, "内部待求解像素", 15, MUTED, "500"))

    # Middle steps
    body.append(rect(380, 130, 260, 100, "#fff4e8", stroke=ORANGE, sw=2, rx=14))
    body.append(text(510, 172, "引导场 v = ∇g", 20, NAVY, "800"))
    body.append(text(510, 202, "或混合梯度等变体", 15, MUTED, "500"))

    body.append(rect(380, 280, 260, 100, "#e8f0ff", stroke=BLUE, sw=2, rx=14))
    body.append(text(510, 322, "边界条件", 20, NAVY, "800"))
    body.append(text(510, 352, "∂Ω 上 f = f*", 15, MUTED, "500"))

    body.append(rect(380, 430, 260, 100, "#eef2f7", stroke="#7b8794", sw=2, rx=14))
    body.append(text(510, 472, "构造右端项", 20, NAVY, "800"))
    body.append(text(510, 502, "div v = Δg", 15, MUTED, "500"))

    # Solver
    body.append(rect(740, 240, 360, 180, "#e8f6ec", stroke=GREEN, sw=2.5, rx=16))
    body.append(text(920, 290, "求解 Poisson 方程", 22, NAVY, "800"))
    body.append(text(920, 330, "Δf = div v    在 Ω 内", 18, DARK, "600"))
    body.append(text(920, 365, "f|∂Ω = f*", 18, DARK, "600"))
    body.append(text(920, 400, "得到稀疏线性系统", 15, MUTED, "500"))

    # Output
    body.append(rect(800, 500, 240, 100, "#d9e9ff", stroke=BLUE, sw=2, rx=14))
    body.append(text(920, 542, "融合结果 f", 22, NAVY, "800"))
    body.append(text(920, 572, "边界贴合、内部保结构", 15, MUTED, "500"))

    # Arrows
    body.append(line(280, 180, 370, 180))
    body.append(line(280, 330, 370, 330))
    body.append(line(280, 480, 370, 480))
    body.append(line(640, 180, 740, 290))
    body.append(line(640, 330, 740, 330))
    body.append(line(640, 480, 740, 370))
    body.append(line(920, 420, 920, 500))

    write_svg(OUT / "poisson-blending-flow.svg", w, h, body)


def fig_discrete_stencil() -> None:
    w, h = 980, 560
    body = []
    body.append(text(w / 2, 42, "离散 Poisson：四点邻域拉普拉斯", 28, NAVY, "800"))
    body.append(
        text(
            w / 2,
            74,
            "每个内部像素的方程只连接自己和上下左右四个邻居",
            16,
            MUTED,
            "500",
        )
    )

    # Grid illustration
    cx, cy = 280, 310
    step = 90
    nodes = {
        "c": (cx, cy),
        "l": (cx - step, cy),
        "r": (cx + step, cy),
        "u": (cx, cy - step),
        "d": (cx, cy + step),
    }
    labels = {"c": "f_p", "l": "f_l", "r": "f_r", "u": "f_u", "d": "f_d"}
    for key, (x, y) in nodes.items():
        fill = "#dff3e4" if key == "c" else "#d9e9ff"
        stroke = GREEN if key == "c" else BLUE
        body.append(rect(x - 36, y - 28, 72, 56, fill, stroke=stroke, sw=2, rx=10))
        body.append(text(x, y + 6, labels[key], 18, NAVY, "800"))

    for a, b in [("c", "l"), ("c", "r"), ("c", "u"), ("c", "d")]:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        body.append(line(x1, y1, x2, y2, color="#9aa4b2", sw=2, marker=False))

    # Equation box
    body.append(rect(520, 160, 400, 280, "#f8fafc", stroke="#c5ccd6", sw=1.5, rx=14))
    body.append(text(720, 210, "中心像素方程", 20, NAVY, "800"))
    body.append(text(720, 260, "4 f_p − f_l − f_r − f_u − f_d", 18, DARK, "600"))
    body.append(text(720, 300, "= div v |_p", 18, DARK, "600"))
    body.append(text(720, 350, "边界像素直接写成", 16, MUTED, "500"))
    body.append(text(720, 385, "f_q = f*_q", 18, NAVY, "700"))

    write_svg(OUT / "discrete-poisson-stencil.svg", w, h, body)


if __name__ == "__main__":
    fig_hard_vs_poisson()
    fig_poisson_flow()
    fig_discrete_stencil()
