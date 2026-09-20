from pathlib import Path

out = Path(__file__).resolve().parents[1] / "pyramid-blending-flow.svg"
W, H = 1180, 880
navy = "#20344d"
blue = "#4e8dd8"
green = "#55a868"
orange = "#dd8452"
gray = "#e9edf3"
dark = "#2f3640"
muted = "#6b7280"
white = "#ffffff"

def rect(x, y, w, h, fill, stroke="#34495e", sw=1.5, rx=10):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def text(x, y, s, size=20, fill=dark, weight="500", anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="{size}" fill="{fill}" font-weight="{weight}">{s}</text>'

def line(x1, y1, x2, y2, color="#6b7280", sw=2, dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" marker-end="url(#arrow)"{dash_attr}/>'

def pyramid(x, y, label, color, levels=4):
    # Keep the four levels compact enough that the three pyramids do not
    # collide with one another or with their labels.
    parts = [text(x + 95, y - 16, label, 18, dark, "700")]
    for i in range(levels):
        ww = 190 - i * 34
        hh = 40
        yy = y + i * 50
        parts.append(rect(x + i * 17, yy, ww, hh, color, stroke="#2c3e50", sw=1.2, rx=8))
        parts.append(text(x + 95, yy + 26, f"level {i}", 15, white, "700"))
    return "\n".join(parts)

def formula_box(x, y, w, h, lines, fill="#f8fafc"):
    parts = [rect(x, y, w, h, fill, stroke="#9aa4b2", sw=1.2, rx=12)]
    for idx, s in enumerate(lines):
        parts.append(text(x + w / 2, y + 34 + idx * 30, s, 18 if idx == 0 else 16, dark if idx == 0 else muted, "700" if idx == 0 else "500"))
    return "\n".join(parts)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
svg.append('''<defs>
  <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
    <path d="M2,2 L10,6 L2,10 z" fill="#6b7280"/>
  </marker>
  <linearGradient id="maskGrad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#2f6fdd"/>
    <stop offset="45%" stop-color="#78a8e8"/>
    <stop offset="55%" stop-color="#f0b184"/>
    <stop offset="100%" stop-color="#d86c37"/>
  </linearGradient>
</defs>''')
svg.append(rect(0, 0, W, H, "#ffffff", stroke="#ffffff", sw=0, rx=0))
svg.append(text(W/2, 48, "多频段融合的信息流：分解、按尺度加权、重建", 28, navy, "800"))
svg.append(text(W/2, 80, "Laplacian band 保存每层被平滑掉的细节；Gaussian weight 决定每层细节来自哪张图", 17, muted, "500"))

# inputs
svg.append(rect(70, 125, 180, 88, "#d9e9ff", stroke=blue, sw=2, rx=14))
svg.append(text(160, 160, "图像 A", 22, navy, "800"))
svg.append(text(160, 189, "左侧/参考曝光", 15, muted, "500"))
svg.append(rect(70, 350, 180, 88, "#ffe6d7", stroke=orange, sw=2, rx=14))
svg.append(text(160, 385, "图像 B", 22, navy, "800"))
svg.append(text(160, 414, "右侧/待融合曝光", 15, muted, "500"))
svg.append(rect(70, 575, 180, 88, "url(#maskGrad)", stroke="#8a8f98", sw=2, rx=14))
svg.append(text(160, 611, "权值 W", 22, white, "800"))
svg.append(text(160, 639, "0 → B，1 → A", 15, white, "700"))

# pyramids
svg.append(pyramid(360, 125, "A 的 Laplacian 金字塔", blue))
svg.append(pyramid(360, 350, "B 的 Laplacian 金字塔", orange))
svg.append(pyramid(360, 575, "W 的 Gaussian 金字塔", green))

# arrows to pyramids
svg.append(line(250, 169, 350, 169))
svg.append(line(250, 394, 350, 394))
svg.append(line(250, 619, 350, 619))

# blend boxes
ys = [125, 187, 249, 311]
for i, y in enumerate(ys):
    svg.append(rect(650, y, 220, 45, "#f8fafc", stroke="#9aa4b2", sw=1.2, rx=9))
    svg.append(text(760, y + 29, f"F{i} = W{i}·LA{i} + (1-W{i})·LB{i}", 15, dark, "700"))
svg.append(text(760, 96, "逐层融合", 20, navy, "800"))
svg.append(line(550, 160, 640, 147))
svg.append(line(550, 425, 640, 272))
svg.append(line(550, 650, 640, 331))

# reconstruction
svg.append(formula_box(935, 160, 190, 150, ["金字塔重建", "从最粗层开始", "逐层上采样相加"], fill="#f5f7fa"))
svg.append(line(875, 218, 925, 218))
svg.append(line(875, 280, 925, 240))
svg.append(line(875, 342, 925, 262))
svg.append(rect(935, 390, 190, 90, "#eaf4ef", stroke=green, sw=2, rx=14))
svg.append(text(1030, 427, "融合结果", 23, navy, "800"))
svg.append(text(1030, 456, "纹理接缝平滑", 15, muted, "500"))
svg.append(line(1030, 310, 1030, 380))

# bottom notes
svg.append(formula_box(90, 790, 300, 76, ["分解", "L_i = G_i - Expand(G_{i+1})"], fill="#f8fbff"))
svg.append(formula_box(440, 790, 300, 76, ["融合", "F_i = W_iL_i^A + (1-W_i)L_i^B"], fill="#f8fbff"))
svg.append(formula_box(790, 790, 300, 76, ["恢复", "G_i = F_i + Expand(G_{i+1})"], fill="#f8fbff"))
svg.append('</svg>')
out.write_text("\n".join(svg), encoding="utf-8")
print(out)
