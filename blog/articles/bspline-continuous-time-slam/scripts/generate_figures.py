#!/usr/bin/env python3
"""Generate SVG figures for the B-spline continuous-time SLAM article."""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def write(name: str, svg: str) -> None:
    path = OUT / name
    path.write_text(svg.strip() + "\n", encoding="utf-8")
    print(f"wrote {path}")


# ---------------------------------------------------------------------------
# Shared style
# ---------------------------------------------------------------------------
STYLE = """
  <style>
    text { font-family: 'Noto Sans CJK SC', 'Source Han Sans SC', 'PingFang SC', Arial, sans-serif; }
    .title { font-size: 15px; font-weight: 700; fill: #1f2937; }
    .lbl { font-size: 13px; font-weight: 600; fill: #374151; }
    .small { font-size: 12px; font-weight: 500; fill: #4b5563; }
    .math { font-size: 13px; font-weight: 600; fill: #1f2937;
            font-family: 'Times New Roman', 'Noto Serif', serif; }
    .axis { stroke: #9ca3af; stroke-width: 1.2; fill: none; }
    .grid { stroke: #e5e7eb; stroke-width: 1; fill: none; }
  </style>
"""


def discrete_vs_continuous() -> str:
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="360" viewBox="0 0 1080 360">
  <rect width="1080" height="360" fill="#fbfcfe"/>
  {STYLE}
  <defs>
    <marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
      <path d="M0,0 L7,3.5 L0,7 Z" fill="#6b7280"/>
    </marker>
  </defs>

  <!-- Left: discrete -->
  <text class="title" x="250" y="36" text-anchor="middle">离散关键帧位姿</text>
  <line class="axis" x1="60" y1="280" x2="440" y2="280"/>
  <line class="axis" x1="60" y1="280" x2="60" y2="70"/>
  <text class="small" x="445" y="285">t</text>
  <text class="small" x="48" y="70">姿态</text>

  <line x1="110" y1="210" x2="180" y2="150" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5 4"/>
  <line x1="180" y1="150" x2="260" y2="190" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5 4"/>
  <line x1="260" y1="190" x2="340" y2="120" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5 4"/>
  <line x1="340" y1="120" x2="410" y2="160" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5 4"/>

  <circle cx="110" cy="210" r="7" fill="#2563eb"/>
  <circle cx="180" cy="150" r="7" fill="#2563eb"/>
  <circle cx="260" cy="190" r="7" fill="#2563eb"/>
  <circle cx="340" cy="120" r="7" fill="#2563eb"/>
  <circle cx="410" cy="160" r="7" fill="#2563eb"/>
  <text class="math" x="110" y="235" text-anchor="middle">T₁</text>
  <text class="math" x="180" y="140" text-anchor="middle">T₂</text>
  <text class="math" x="260" y="215" text-anchor="middle">T₃</text>
  <text class="math" x="340" y="110" text-anchor="middle">T₄</text>
  <text class="math" x="410" y="185" text-anchor="middle">T₅</text>
  <text class="small" x="250" y="320" text-anchor="middle">中间时刻只能靠插值或常速假设补全</text>

  <!-- Right: continuous -->
  <text class="title" x="800" y="36" text-anchor="middle">连续时间 B 样条轨迹</text>
  <line class="axis" x1="560" y1="280" x2="1020" y2="280"/>
  <line class="axis" x1="560" y1="280" x2="560" y2="70"/>
  <text class="small" x="1025" y="285">t</text>
  <text class="small" x="548" y="70">姿态</text>

  <path d="M610,210 C650,210 670,150 710,150 C760,150 780,200 830,185
           C880,170 900,110 950,125 C980,135 1000,155 1010,160"
        fill="none" stroke="#0f766e" stroke-width="2.4"/>

  <!-- control points -->
  <circle cx="610" cy="220" r="5" fill="#f59e0b"/>
  <circle cx="700" cy="130" r="5" fill="#f59e0b"/>
  <circle cx="820" cy="200" r="5" fill="#f59e0b"/>
  <circle cx="930" cy="105" r="5" fill="#f59e0b"/>
  <circle cx="1010" cy="170" r="5" fill="#f59e0b"/>
  <line x1="610" y1="220" x2="700" y2="130" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="3 3"/>
  <line x1="700" y1="130" x2="820" y2="200" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="3 3"/>
  <line x1="820" y1="200" x2="930" y2="105" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="3 3"/>
  <line x1="930" y1="105" x2="1010" y2="170" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="3 3"/>

  <!-- sensor samples -->
  <circle cx="680" cy="158" r="4" fill="#2563eb"/>
  <circle cx="760" cy="168" r="4" fill="#2563eb"/>
  <circle cx="840" cy="178" r="4" fill="#dc2626"/>
  <circle cx="900" cy="140" r="4" fill="#dc2626"/>
  <text class="small" x="800" y="320" text-anchor="middle">任意时刻可求值；IMU / 激光点可落在同一条曲线上</text>

  <rect x="560" y="335" width="12" height="12" fill="#f59e0b"/>
  <text class="small" x="578" y="346">控制点</text>
  <circle cx="670" cy="341" r="4" fill="#2563eb"/>
  <text class="small" x="680" y="346">IMU 采样</text>
  <circle cx="780" cy="341" r="4" fill="#dc2626"/>
  <text class="small" x="790" y="346">激光 / 图像观测</text>
</svg>
"""


def basis_functions_fixed() -> str:
    """Uniform B-spline basis shapes for degrees 0..3."""

    def eval_basis(d: int, n: int = 240):
        # Closed-form uniform cardinal B-splines on [0, d+1]
        # Use recursive definition with caching
        from functools import lru_cache

        @lru_cache(None)
        def N(i: int, deg: int, t: float) -> float:
            if deg == 0:
                return 1.0 if (i <= t < i + 1) else 0.0
            a = 0.0
            b = 0.0
            if deg > 0:
                a = ((t - i) / deg) * N(i, deg - 1, t)
                b = ((i + deg + 1 - t) / deg) * N(i + 1, deg - 1, t)
            return a + b

        xs, ys = [], []
        support = d + 1
        for k in range(n + 1):
            t = support * k / n
            # at right endpoint of last interval, include value via left-continuity tweak
            if k == n:
                t = support - 1e-12
            xs.append(t)
            ys.append(N(0, d, t))
        return xs, ys, support

    panels = [
        (0, "0 次：矩形窗", "#2563eb"),
        (1, "1 次：折线三角", "#0f766e"),
        (2, "2 次：分段二次", "#b45309"),
        (3, "3 次：分段三次（常用）", "#7c3aed"),
    ]
    W, H = 1080, 420
    parts = [f'<rect width="{W}" height="{H}" fill="#fbfcfe"/>', STYLE]

    for idx, (d, title, color) in enumerate(panels):
        ox, oy, pw, ph = 40 + idx * 260, 80, 220, 250
        xs, ys, support = eval_basis(d)
        parts.append(
            f'<text class="title" x="{ox + pw/2}" y="36" text-anchor="middle">{title}</text>'
        )
        parts.append(
            f'<line class="axis" x1="{ox}" y1="{oy+ph}" x2="{ox+pw}" y2="{oy+ph}"/>'
        )
        parts.append(
            f'<line class="axis" x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy+ph}"/>'
        )
        pts = []
        for t, y in zip(xs, ys):
            x = ox + (t / support) * pw
            yy = oy + ph - y * (ph - 18)
            pts.append(f"{x:.2f},{yy:.2f}")
        fill = [f"{ox:.2f},{oy+ph}"] + pts + [f"{ox+pw:.2f},{oy+ph}"]
        parts.append(
            f'<polygon points="{" ".join(fill)}" fill="{color}" opacity="0.12"/>'
        )
        parts.append(
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.2"/>'
        )
        parts.append(
            f'<text class="math" x="{ox + pw/2}" y="{oy+ph+28}" text-anchor="middle">N₀,{d}(t)</text>'
        )
        parts.append(
            f'<text class="small" x="{ox + pw/2}" y="{oy+ph+48}" text-anchor="middle">支撑宽度 = {support}</text>'
        )

    parts.append(
        f'<text class="small" x="{W/2}" y="400" text-anchor="middle">'
        "次数升高：连续性更好，支撑变宽，每个时刻受影响的控制点更多</text>"
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(parts) + "</svg>"


def local_support() -> str:
    # The picture deliberately separates two readings of the same support:
    # each row fixes i and shows [t_i, t_{i+4}); the blue column fixes the
    # query interval [t_5,t_6) and makes the four active rows visible.
    x0, dx = 90, 95
    knots = " ".join(
        f'<line x1="{x0+i*dx}" y1="315" x2="{x0+i*dx}" y2="327" '
        'stroke="#6b7280" stroke-width="1.3"/>'
        for i in range(10)
    )
    labels = " ".join(
        f'<text class="math" x="{x0+i*dx}" y="347" text-anchor="middle">t_{i}</text>'
        for i in range(10)
    )
    rows = []
    for row, i in enumerate(range(1, 7)):
        y = 99 + row * 38
        x1, x2 = x0 + i * dx, x0 + (i + 4) * dx
        active = 2 <= i <= 5
        color = ["#2563eb", "#0f766e", "#d97706", "#7c3aed"][i - 2] if active else "#9ca3af"
        rows.append(
            f'<text class="math" x="55" y="{y+5}" text-anchor="end">N_{{{i},3}}</text>'
            f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" '
            f'stroke="{color}" stroke-width="10" stroke-linecap="butt" opacity="{0.82 if active else 0.55}"/>'
            f'<text class="small" x="{(x1+x2)/2}" y="{y-9}" text-anchor="middle">[t_{i}, t_{i+4})</text>'
        )
    active_coeffs = " ".join(
        f'<circle cx="{x0+i*dx}" cy="382" r="7" fill="#f59e0b"/>'
        f'<text class="math" x="{x0+i*dx}" y="404" text-anchor="middle">c_{i}</text>'
        for i in range(2, 6)
    )
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="460" viewBox="0 0 1080 460">
  <rect width="1080" height="460" fill="#fbfcfe"/>
  {STYLE}
  <text class="title" x="540" y="30" text-anchor="middle">固定区间后，哪些三次基函数会参与计算</text>
  <text class="small" x="540" y="52" text-anchor="middle">每一行先固定一个基函数编号 i，再画出它的支撑 [t_i, t_{{i+4}})</text>

  <!-- query interval [t_5,t_6) -->
  <rect x="{x0+5*dx}" y="77" width="{dx}" height="258" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text class="lbl" x="{x0+5.5*dx}" y="91" text-anchor="middle">当前区间</text>
  <text class="math" x="{x0+5.5*dx}" y="108" text-anchor="middle">[t_5,t_6)</text>
  <line x1="{x0+5.5*dx}" y1="77" x2="{x0+5.5*dx}" y2="327" stroke="#2563eb" stroke-width="1.6" stroke-dasharray="4 3"/>

  {''.join(rows)}
  <line class="axis" x1="{x0}" y1="321" x2="{x0+9*dx}" y2="321"/>
  {knots}
  {labels}

  <text class="lbl" x="540" y="370" text-anchor="middle">灰色支撑在区间边界结束或开始；覆盖当前区间的是中间这 4 个基函数</text>
  {active_coeffs}
  <text class="small" x="540" y="445" text-anchor="middle">因此 f(t)=c₂N₂,₃(t)+c₃N₃,₃(t)+c₄N₄,₃(t)+c₅N₅,₃(t)，其余系数在这里权重为 0</text>
</svg>
"""


def control_polygon() -> str:
    # Draw a cubic B-spline approximation of a few control points in 2D
    # Using uniform cubic basis matrix evaluation
    M = [
        [1, 4, 1, 0],
        [-3, 0, 3, 0],
        [3, -6, 3, 0],
        [-1, 3, -3, 1],
    ]
    # scale 1/6
    M = [[c / 6 for c in row] for row in M]
    ctrl = [(80, 260), (180, 80), (320, 300), (460, 100), (600, 280), (740, 90), (880, 240), (980, 140)]

    def eval_seg(i: int, u: float):
        P = ctrl[i : i + 4]
        # p = P * M^T * u_vec  (column form) => sum_j w_j P_j
        uvec = [1, u, u * u, u * u * u]
        # weights = u^T M
        w = [0, 0, 0, 0]
        for j in range(4):
            for k in range(4):
                w[j] += uvec[k] * M[k][j]
        x = sum(w[j] * P[j][0] for j in range(4))
        y = sum(w[j] * P[j][1] for j in range(4))
        return x, y

    curve_pts = []
    for i in range(len(ctrl) - 3):
        for s in range(40):
            u = s / 40
            curve_pts.append(eval_seg(i, u))
    curve_pts.append(eval_seg(len(ctrl) - 4, 1.0 - 1e-9))

    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in ctrl)
    curve = " ".join(f"{x:.1f},{y:.1f}" for x, y in curve_pts)
    dots = "".join(
        f'<circle cx="{x}" cy="{y}" r="7" fill="#f59e0b"/><text class="math" x="{x}" y="{y-12}" text-anchor="middle">p{i}</text>'
        for i, (x, y) in enumerate(ctrl)
    )

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="380" viewBox="0 0 1080 380">
  <rect width="1080" height="380" fill="#fbfcfe"/>
  {STYLE}
  <text class="title" x="540" y="32" text-anchor="middle">控制多边形与均匀三次 B 样条曲线（逼近，一般不过控制点）</text>
  <polyline points="{poly}" fill="none" stroke="#fbbf24" stroke-width="1.6" stroke-dasharray="5 4"/>
  <polyline points="{curve}" fill="none" stroke="#0f766e" stroke-width="2.6"/>
  {dots}
  <rect x="80" y="340" width="18" height="4" fill="#0f766e"/>
  <text class="small" x="105" y="345">样条曲线 p(t)</text>
  <line x1="250" y1="342" x2="280" y2="342" stroke="#fbbf24" stroke-width="1.6" stroke-dasharray="5 4"/>
  <text class="small" x="290" y="345">控制多边形</text>
  <circle cx="460" cy="342" r="5" fill="#f59e0b"/>
  <text class="small" x="475" y="345">控制点（优化变量）</text>
</svg>
"""


def basis_weighted_curve() -> str:
    """Show one uniform cubic span as four weighted basis contributions."""
    W, H = 1080, 500
    left, right = 90, 1000
    top, bottom = 70, 245
    colors = ["#2563eb", "#059669", "#d97706", "#dc2626"]
    coeffs = [0.6, 1.6, 0.9, 1.3]

    def weights(u):
        return [
            (1 - u) ** 3 / 6,
            (3 * u**3 - 6 * u**2 + 4) / 6,
            (-3 * u**3 + 3 * u**2 + 3 * u + 1) / 6,
            u**3 / 6,
        ]

    def point(u, y, scale=1.0, baseline=bottom):
        x = left + u * (right - left)
        yy = baseline - y * scale
        return f"{x:.1f},{yy:.1f}"

    basis_lines = []
    weighted_lines = []
    total = []
    scale = 470
    for j, color in enumerate(colors):
        pts = []
        for k in range(81):
            u = k / 80
            pts.append(point(u, weights(u)[j], scale))
        basis_lines.append(
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.5" opacity="0.75">'
            f'<animate attributeName="stroke-width" values="2.5;4.5;2.5" dur="8s" begin="{j*2}s" repeatCount="indefinite"/></polyline>'
        )
        pts_w = []
        for k in range(81):
            u = k / 80
            pts_w.append(point(u, coeffs[j] * weights(u)[j], 70, 440))
        weighted_lines.append(
            f'<polyline points="{" ".join(pts_w)}" fill="none" stroke="{color}" stroke-width="2" opacity="0.55"/>'
        )
    for k in range(81):
        u = k / 80
        total.append(point(u, sum(coeffs[j] * weights(u)[j] for j in range(4)), 70, 440))

    knots = " ".join(
        f'<line x1="{left + (right-left)*u:.1f}" y1="{bottom-6}" x2="{left + (right-left)*u:.1f}" y2="{bottom+6}" stroke="#6b7280"/>'
        for u in [0, 1/3, 2/3, 1]
    )
    labels = " ".join(
        f'<text class="math" x="{left + (right-left)*u:.1f}" y="{bottom+28}" text-anchor="middle">t_{i}</text>'
        for i, u in enumerate([0, 1/3, 2/3, 1])
    )
    query_u = 0.35
    query_x = left + query_u * (right - left)
    coeff_text = "；".join(f"c_{i}={v}" for i, v in enumerate(coeffs))
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#fbfcfe"/>
  {STYLE}
  <text class="title" x="540" y="30" text-anchor="middle">均匀节点下：同一组基函数的加权和形成 f(t)</text>
  <text class="lbl" x="90" y="55">上图：在一个节点区间内，四个基函数给出随 u 变化的四个权重</text>
  <line class="axis" x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}"/>
  <line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>
  {knots}
  {labels}
  {"".join(basis_lines)}
  <line x1="{query_x:.1f}" y1="{top}" x2="{query_x:.1f}" y2="{bottom}" stroke="#111827" stroke-width="1.8" stroke-dasharray="4 3"/>
  <text class="small" x="{query_x + 8:.1f}" y="{top + 16}" text-anchor="start">u=0.35</text>
  <line x1="{left + (right-left)*0.5:.1f}" y1="{top}" x2="{left + (right-left)*0.5:.1f}" y2="{bottom}" stroke="#111827" stroke-dasharray="4 3">
    <animate attributeName="x1" values="{left};{right};{left}" dur="8s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="{left};{right};{left}" dur="8s" repeatCount="indefinite"/>
  </line>
  <text class="small" x="{right}" y="{top+12}" text-anchor="end">b₀(u), b₁(u), b₂(u), b₃(u)</text>
  <text class="lbl" x="90" y="305">下图：控制系数改变每个基函数的幅值，四个局部贡献相加成为曲线</text>
  <line class="axis" x1="{left}" y1="440" x2="{right}" y2="440"/>
  <line class="axis" x1="{left}" y1="325" x2="{left}" y2="440"/>
  {"".join(weighted_lines)}
  <polyline points="{" ".join(total)}" fill="none" stroke="#111827" stroke-width="3.5">
    <animate attributeName="stroke-dasharray" values="0,1200;1200,0" dur="8s" repeatCount="indefinite"/>
  </polyline>
  <text class="math" x="{right-8}" y="350" text-anchor="end">f(t)=Σ cᵢNᵢ,₃(t)</text>
  <text class="small" x="540" y="480" text-anchor="middle">局部区间对应全局 t*=t₃+0.35Δt；{coeff_text}；黑色曲线是四个彩色贡献的和</text>
</svg>
"""


def global_basis_fit_animation() -> str:
    """Macro view: a bank of translated cubic bases, sparse contributions, and f(t)."""
    W, H = 1120, 720
    left, right = 80, 1040
    n = 7
    coeffs = [0.4, 1.1, 1.8, 0.8, 1.5, 0.7, 1.2]
    colors = ["#2563eb", "#0f766e", "#d97706", "#dc2626", "#7c3aed", "#0891b2", "#be123c"]

    def b3(x):
        ax = abs(x)
        if ax >= 2:
            return 0.0
        if ax > 1:
            return (2 - ax) ** 3 / 6
        return (4 - 6 * x * x + 3 * ax**3) / 6

    def xpix(q):
        return left + (q / 7) * (right - left)

    def polyline(values, baseline, scale):
        return " ".join(f"{xpix(q):.1f},{baseline - v * scale:.1f}" for q, v in values)

    qs = [7 * k / 240 for k in range(241)]
    basis = [[(q, b3(q - i - 2)) for q in qs] for i in range(n)]
    total = [(q, sum(coeffs[i] * b3(q - i - 2) for i in range(n))) for q in qs]

    top_base, mid_base, bot_base = 200, 425, 650
    top_scale, mid_scale, bot_scale = 170, 105, 125
    basis_svg = []
    contrib_svg = []
    for i in range(n):
        # Bases outside the active window remain visible but muted.
        basis_svg.append(
            f'<polyline points="{polyline(basis[i], top_base, top_scale)}" fill="none" stroke="{colors[i]}" stroke-width="2.2" opacity="0.42">'
            f'<animate attributeName="opacity" values="0.42;0.95;0.42" dur="8s" begin="{i*0.7:.1f}s" repeatCount="indefinite"/></polyline>'
        )
        contrib = [(q, coeffs[i] * b3(q - i - 2)) for q in qs]
        contrib_svg.append(
            f'<polyline points="{polyline(contrib, mid_base, mid_scale)}" fill="none" stroke="{colors[i]}" stroke-width="2" opacity="0.52"/>'
        )

    knots = " ".join(
        f'<line x1="{xpix(i):.1f}" y1="{top_base+6}" x2="{xpix(i):.1f}" y2="{top_base+14}" stroke="#6b7280"/>'
        for i in range(8)
    )
    knot_labels = " ".join(
        f'<text class="math" x="{xpix(i):.1f}" y="{top_base+35}" text-anchor="middle">t_{i}</text>'
        for i in range(8)
    )
    query_x = xpix(3.35)
    query_q = "3.35"
    query_line = f'''<line x1="{query_x:.1f}" y1="55" x2="{query_x:.1f}" y2="650" stroke="#111827" stroke-width="1.8" stroke-dasharray="5 4">
      <animate attributeName="x1" values="{xpix(0.25):.1f};{xpix(6.75):.1f};{xpix(0.25):.1f}" dur="10s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="{xpix(0.25):.1f};{xpix(6.75):.1f};{xpix(0.25):.1f}" dur="10s" repeatCount="indefinite"/>
    </line>'''
    target_qs = [0.4, 1.4, 2.4, 3.4, 4.4, 5.4, 6.4]
    target = [
        (q, sum(coeffs[i] * b3(q - i - 2) for i in range(n)) + delta)
        for q, delta in zip(target_qs, [0.05, -0.04, 0.03, -0.05, 0.04, -0.03, 0.02])
    ]
    target_svg = " ".join(f'<circle cx="{xpix(q):.1f}" cy="{bot_base-y*bot_scale:.1f}" r="4.5" fill="#111827"/>' for q, y in target)
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#fbfcfe"/>
  {STYLE}
  <text class="title" x="560" y="28" text-anchor="middle">全局视图：7 个基函数、局部稀疏贡献与合成曲线 f(t)</text>
  <text class="lbl" x="80" y="52">上层：每个 Nᵢ,₃ 是同一个三次模板的平移，支撑覆盖 4 个节点区间</text>
  <line class="axis" x1="{left}" y1="{top_base}" x2="{right}" y2="{top_base}"/>
  {knots}{knot_labels}{"".join(basis_svg)}
  <text class="small" x="{right}" y="75" text-anchor="end">查询时刻 t* 只激活附近 4 个基函数</text>
  <text class="lbl" x="80" y="285">中层：每个基函数乘以控制系数 cᵢ，远处贡献严格为 0</text>
  <line class="axis" x1="{left}" y1="{mid_base}" x2="{right}" y2="{mid_base}"/>
  {"".join(contrib_svg)}
  <text class="small" x="{right}" y="305" text-anchor="end">彩色曲线 = cᵢNᵢ,₃(t)</text>
  <text class="lbl" x="80" y="505">下层：所有局部贡献相加得到 f(t)，黑点是观测值</text>
  <line class="axis" x1="{left}" y1="{bot_base}" x2="{right}" y2="{bot_base}"/>
  <polyline points="{polyline(total, bot_base, bot_scale)}" fill="none" stroke="#111827" stroke-width="3.2"/>
  {target_svg}
  {query_line}
  <text class="math" x="{right-8}" y="535" text-anchor="end">f(t)=Σᵢ cᵢNᵢ,₃(t)</text>
  <text class="small" x="560" y="700" text-anchor="middle">拟合就是调整 cᵢ，使黑色合成曲线在观测时刻靠近黑点；每个时刻只涉及附近 4 个 cᵢ</text>
</svg>
"""


def cumulative_form() -> str:
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="420" viewBox="0 0 1080 420">
  <rect width="1080" height="420" fill="#fbfcfe"/>
  {STYLE}
  <defs>
    <marker id="a1" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
      <path d="M0,0 L7,3.5 L0,7 Z" fill="#4b5563"/>
    </marker>
  </defs>

  <text class="title" x="540" y="34" text-anchor="middle">标准形式与累积形式：同一条曲线，两种写法</text>

  <!-- Left box -->
  <rect x="40" y="60" width="480" height="300" rx="12" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5"/>
  <text class="lbl" x="280" y="95" text-anchor="middle">标准形式（欧氏空间）</text>
  <text class="math" x="280" y="150" text-anchor="middle">p(t) = Σ Bᵢ(t) pᵢ</text>
  <text class="small" x="280" y="190" text-anchor="middle">对控制点做凸组合加权</text>
  <text class="small" x="280" y="220" text-anchor="middle">适合 ℝ³ 平移样条</text>
  <text class="small" x="280" y="260" text-anchor="middle">加法结构清晰，求导即对基函数求导</text>
  <circle cx="160" cy="310" r="14" fill="#2563eb"/>
  <circle cx="230" cy="310" r="14" fill="#2563eb"/>
  <circle cx="300" cy="310" r="14" fill="#2563eb"/>
  <circle cx="370" cy="310" r="14" fill="#2563eb"/>
  <text class="small" x="265" y="345" text-anchor="middle">pᵢ 直接相加</text>

  <!-- Right box -->
  <rect x="560" y="60" width="480" height="300" rx="12" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.5"/>
  <text class="lbl" x="800" y="95" text-anchor="middle">累积形式（通向李群）</text>
  <text class="math" x="800" y="145" text-anchor="middle">p(t) = pᵢ + Σ λ̃ⱼ(u) (pᵢ₊ⱼ − pᵢ₊ⱼ₋₁)</text>
  <text class="small" x="800" y="190" text-anchor="middle">从左侧锚点出发，叠加相邻差分</text>
  <text class="small" x="800" y="220" text-anchor="middle">差分 ↔ 相对旋转 / 相对位姿</text>
  <text class="small" x="800" y="260" text-anchor="middle">经 Exp(λ log(·)) 推广到 SO(3)、SE(3)</text>
  <circle cx="680" cy="310" r="14" fill="#0f766e"/>
  <text class="math" x="720" y="315" fill="#0f766e">→</text>
  <circle cx="760" cy="310" r="14" fill="#14b8a6"/>
  <text class="math" x="800" y="315" fill="#0f766e">→</text>
  <circle cx="840" cy="310" r="14" fill="#5eead4"/>
  <text class="math" x="880" y="315" fill="#0f766e">→</text>
  <circle cx="920" cy="310" r="14" fill="#99f6e4"/>
  <text class="small" x="800" y="345" text-anchor="middle">连乘相对增量</text>

  <text class="small" x="540" y="395" text-anchor="middle">
    欧氏空间中两种形式数值等价；旋转几乎总是写累积型，因为控制点不能做普通向量加法
  </text>
</svg>
"""


def split_vs_se3() -> str:
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="440" viewBox="0 0 1080 440">
  <rect width="1080" height="440" fill="#fbfcfe"/>
  {STYLE}

  <text class="title" x="540" y="34" text-anchor="middle">刚体轨迹的两种参数化</text>

  <!-- Split -->
  <rect x="40" y="60" width="480" height="320" rx="12" fill="#eff6ff" stroke="#60a5fa" stroke-width="1.6"/>
  <text class="lbl" x="280" y="95" text-anchor="middle">拆分表示  ℝ³ × SO(3)</text>

  <rect x="80" y="120" width="180" height="70" rx="8" fill="#dbeafe" stroke="#3b82f6"/>
  <text class="blk" x="170" y="150" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">平移样条</text>
  <text class="math" x="170" y="172" text-anchor="middle">p(t) ∈ ℝ³</text>

  <rect x="300" y="120" width="180" height="70" rx="8" fill="#dbeafe" stroke="#3b82f6"/>
  <text class="blk" x="390" y="150" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">旋转样条</text>
  <text class="math" x="390" y="172" text-anchor="middle">R(t) ∈ SO(3)</text>

  <text class="small" x="280" y="230" text-anchor="middle">平移与旋转各自插值，互不强制耦合</text>
  <text class="small" x="280" y="260" text-anchor="middle">线加速度 = p̈(t)，与姿态解耦</text>
  <text class="small" x="280" y="290" text-anchor="middle">适合手持、机载、一般自由运动</text>
  <text class="small" x="280" y="330" text-anchor="middle">Ovrén &amp; Forssén、Haarbach 等均倾向此选择</text>

  <!-- SE3 -->
  <rect x="560" y="60" width="480" height="320" rx="12" fill="#fff7ed" stroke="#fb923c" stroke-width="1.6"/>
  <text class="lbl" x="800" y="95" text-anchor="middle">联合表示  SE(3)</text>

  <rect x="670" y="120" width="260" height="70" rx="8" fill="#ffedd5" stroke="#f97316"/>
  <text class="blk" x="800" y="150" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">位姿样条</text>
  <text class="math" x="800" y="172" text-anchor="middle">T(t) ∈ SE(3)</text>

  <text class="small" x="800" y="230" text-anchor="middle">相对增量是螺旋运动（screw）</text>
  <text class="small" x="800" y="260" text-anchor="middle">平移方向与瞬时转轴隐式耦合</text>
  <text class="small" x="800" y="290" text-anchor="middle">更贴近机械臂末端一类“绕轴拧”的运动</text>
  <text class="small" x="800" y="330" text-anchor="middle">求加速度时姿态会渗入平移通道</text>

  <text class="small" x="540" y="415" text-anchor="middle">
    连续时间视觉–惯性与多数标定问题中，拆分表示通常更稳、更快、更易解释
  </text>
</svg>
"""


def slam_pipeline() -> str:
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="420" viewBox="0 0 1180 420">
  <rect width="1180" height="420" fill="#fbfcfe"/>
  {STYLE}
  <defs>
    <marker id="arrp" markerWidth="9" markerHeight="9" refX="8" refY="3.5" orient="auto">
      <path d="M0,0 L8,3.5 L0,7 Z" fill="#4b5563"/>
    </marker>
  </defs>

  <text class="title" x="590" y="36" text-anchor="middle">样条如何接入连续时间 SLAM / 标定</text>

  <!-- sensors -->
  <rect x="40" y="80" width="160" height="260" rx="12" fill="#eff6ff" stroke="#93c5fd"/>
  <text class="lbl" x="120" y="115" text-anchor="middle">传感器</text>
  <rect x="60" y="140" width="120" height="40" rx="6" fill="#dbeafe" stroke="#3b82f6"/>
  <text class="small" x="120" y="165" text-anchor="middle">IMU ω, a</text>
  <rect x="60" y="200" width="120" height="40" rx="6" fill="#dbeafe" stroke="#3b82f6"/>
  <text class="small" x="120" y="225" text-anchor="middle">相机 / 事件</text>
  <rect x="60" y="260" width="120" height="40" rx="6" fill="#dbeafe" stroke="#3b82f6"/>
  <text class="small" x="120" y="285" text-anchor="middle">LiDAR 点</text>

  <line x1="200" y1="210" x2="260" y2="210" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arrp)"/>

  <!-- spline -->
  <rect x="260" y="80" width="280" height="260" rx="12" fill="#ecfdf5" stroke="#6ee7b7"/>
  <text class="lbl" x="400" y="115" text-anchor="middle">连续时间轨迹</text>
  <text class="math" x="400" y="160" text-anchor="middle">p(t), R(t)</text>
  <text class="small" x="400" y="195" text-anchor="middle">均匀三次 B 样条</text>
  <text class="small" x="400" y="225" text-anchor="middle">控制点 = 优化变量</text>
  <text class="small" x="400" y="255" text-anchor="middle">任意 t 求值 / 求导</text>
  <text class="small" x="400" y="295" text-anchor="middle">ω(t), a(t) 由导数给出</text>

  <line x1="540" y1="160" x2="600" y2="130" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arrp)"/>
  <line x1="540" y1="210" x2="600" y2="210" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arrp)"/>
  <line x1="540" y1="260" x2="600" y2="290" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arrp)"/>

  <!-- residuals -->
  <rect x="600" y="70" width="240" height="280" rx="12" fill="#fff7ed" stroke="#fdba74"/>
  <text class="lbl" x="720" y="105" text-anchor="middle">残差</text>
  <rect x="620" y="125" width="200" height="50" rx="6" fill="#ffedd5" stroke="#f97316"/>
  <text class="small" x="720" y="155" text-anchor="middle">IMU：ω̂−ω(t), â−a(t)</text>
  <rect x="620" y="195" width="200" height="50" rx="6" fill="#ffedd5" stroke="#f97316"/>
  <text class="small" x="720" y="225" text-anchor="middle">视觉：重投影 / 卷帘行时</text>
  <rect x="620" y="265" width="200" height="50" rx="6" fill="#ffedd5" stroke="#f97316"/>
  <text class="small" x="720" y="295" text-anchor="middle">激光：点到面 / 去畸变</text>

  <line x1="840" y1="210" x2="900" y2="210" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arrp)"/>

  <!-- opt -->
  <rect x="900" y="130" width="240" height="160" rx="12" fill="#f5f3ff" stroke="#c4b5fd"/>
  <text class="lbl" x="1020" y="175" text-anchor="middle">批优化 / 滑窗</text>
  <text class="small" x="1020" y="215" text-anchor="middle">更新控制点</text>
  <text class="small" x="1020" y="245" text-anchor="middle">外参 · 零偏 · 地图</text>

  <text class="small" x="590" y="390" text-anchor="middle">
    高频与异步观测不再需要先对齐到同一组关键帧；它们在各自时间戳上约束同一条曲线
  </text>
</svg>
"""


def box_to_triangle_animation() -> str:
    """Animated SVG: two boxes slide, overlap area traces the tent B1(x)."""
    # Coordinate maps
    # Top panel τ ∈ [-1.6, 1.6] → x_svg; bottom x ∈ [-1.2, 1.2]
    W, H = 960, 560
    # top plot
    tx0, ty0, tw, th = 80, 70, 700, 160
    # bottom plot
    bx0, by0, bw, bh = 80, 320, 700, 160

    def top_x(tau: float) -> float:
        return tx0 + (tau + 1.6) / 3.2 * tw

    def top_y(val: float) -> float:
        # val in [0,1] → box height
        return ty0 + th - val * (th - 20)

    def bot_x(xv: float) -> float:
        return bx0 + (xv + 1.2) / 2.4 * bw

    def bot_y(val: float) -> float:
        return by0 + bh - val * (bh - 24)

    # Sample sweep x from -1.15 to 1.15
    n = 49
    xs = [-1.15 + 2.3 * i / (n - 1) for i in range(n)]

    def overlap(x: float) -> tuple[float, float, float]:
        # fixed [-0.5,0.5], moving [x-0.5, x+0.5]
        lo = max(-0.5, x - 0.5)
        hi = min(0.5, x + 0.5)
        length = max(0.0, hi - lo)
        return lo, hi, length

    # Build keyframe value lists for SMIL
    move_left = []
    move_w = []
    ov_left = []
    ov_w = []
    tip_x = []
    tip_y = []
    trail_pts = []  # polyline growing: accumulate visible part of tent

    box_h = th - 20
    box_top = ty0 + 20
    unit_w_tau = tw / 3.2  # svg width per τ unit

    for x in xs:
        lo, hi, length = overlap(x)
        # moving box in τ: [x-0.5, x+0.5]
        ml = top_x(x - 0.5)
        mw = 1.0 * unit_w_tau
        move_left.append(f"{ml:.2f}")
        move_w.append(f"{mw:.2f}")
        if length > 1e-9:
            ov_left.append(f"{top_x(lo):.2f}")
            ov_w.append(f"{length * unit_w_tau:.2f}")
        else:
            ov_left.append(f"{top_x(0):.2f}")
            ov_w.append("0")
        b1 = max(0.0, 1.0 - abs(x)) if abs(x) < 1 else 0.0
        tip_x.append(f"{bot_x(x):.2f}")
        tip_y.append(f"{bot_y(b1):.2f}")
        trail_pts.append(f"{bot_x(x):.1f},{bot_y(b1):.1f}")

    # Full tent path for underlay
    tent_samples = []
    for i in range(81):
        xx = -1.2 + 2.4 * i / 80
        yy = max(0.0, 1.0 - abs(xx)) if abs(xx) <= 1 else 0.0
        tent_samples.append(f"{bot_x(xx):.1f},{bot_y(yy):.1f}")
    tent_poly = " ".join(tent_samples)

    values = ";".join
    dur = "10s"

    # Fixed box geometry
    fixed_x = top_x(-0.5)
    fixed_w = unit_w_tau

    # Axis ticks top
    top_ticks = "".join(
        f'<line x1="{top_x(t):.1f}" y1="{ty0+th}" x2="{top_x(t):.1f}" y2="{ty0+th+6}" stroke="#6b7280"/>'
        f'<text class="small" x="{top_x(t):.1f}" y="{ty0+th+22}" text-anchor="middle">{t:g}</text>'
        for t in (-1.5, -1, -0.5, 0, 0.5, 1, 1.5)
    )
    bot_ticks = "".join(
        f'<line x1="{bot_x(t):.1f}" y1="{by0+bh}" x2="{bot_x(t):.1f}" y2="{by0+bh+6}" stroke="#6b7280"/>'
        f'<text class="small" x="{bot_x(t):.1f}" y="{by0+bh+22}" text-anchor="middle">{t:g}</text>'
        for t in (-1, -0.5, 0, 0.5, 1)
    )

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#fbfcfe"/>
  {STYLE}
  <text class="title" x="{W/2}" y="32" text-anchor="middle">几何动画：两个 box 滑动重叠 → 三角形核 B₁(x)</text>

  <!-- ===== Top panel ===== -->
  <text class="lbl" x="{tx0}" y="58">上图：被积函数 b(τ)·b(x−τ)（重叠区面积 = 卷积值）</text>
  <line class="axis" x1="{tx0}" y1="{ty0+th}" x2="{tx0+tw}" y2="{ty0+th}"/>
  <line class="axis" x1="{tx0}" y1="{ty0}" x2="{tx0}" y2="{ty0+th}"/>
  <text class="small" x="{tx0+tw+8}" y="{ty0+th+4}">τ</text>
  {top_ticks}

  <!-- fixed box b(τ) -->
  <rect x="{fixed_x:.2f}" y="{box_top}" width="{fixed_w:.2f}" height="{box_h}"
        fill="#93c5fd" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.6"/>
  <text class="math" x="{fixed_x + fixed_w/2:.1f}" y="{box_top - 8}" text-anchor="middle" fill="#1d4ed8">b(τ)</text>

  <!-- moving box b(x-τ) -->
  <rect x="{move_left[0]}" y="{box_top}" width="{move_w[0]}" height="{box_h}"
        fill="#fdba74" fill-opacity="0.45" stroke="#c2410c" stroke-width="1.6">
    <animate attributeName="x" values="{values(move_left)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </rect>
  <text class="math" x="{tx0 + tw - 20}" y="{box_top - 8}" text-anchor="end" fill="#9a3412">b(x−τ) 滑动</text>

  <!-- overlap = product = area -->
  <rect x="{ov_left[0]}" y="{box_top}" width="{ov_w[0]}" height="{box_h}"
        fill="#22c55e" fill-opacity="0.55" stroke="#15803d" stroke-width="1.4">
    <animate attributeName="x" values="{values(ov_left)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="width" values="{values(ov_w)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </rect>
  <text class="small" x="{tx0 + tw/2}" y="{ty0 + th + 48}" text-anchor="middle">
    绿色 = 两矩形重叠；高度为 1，故重叠长度 = ∫ b(τ)b(x−τ) dτ = B₁(x)
  </text>

  <!-- legend -->
  <rect x="820" y="80" width="18" height="14" fill="#93c5fd" stroke="#2563eb"/>
  <text class="small" x="844" y="92">固定 box</text>
  <rect x="820" y="110" width="18" height="14" fill="#fdba74" stroke="#c2410c"/>
  <text class="small" x="844" y="122">滑动 box</text>
  <rect x="820" y="140" width="18" height="14" fill="#22c55e" stroke="#15803d"/>
  <text class="small" x="844" y="152">重叠面积</text>

  <!-- ===== Bottom panel ===== -->
  <text class="lbl" x="{bx0}" y="300">下图：相对位移 x 扫描时，重叠面积描出 B₁(x)=1−|x|</text>
  <line class="axis" x1="{bx0}" y1="{by0+bh}" x2="{bx0+bw}" y2="{by0+bh}"/>
  <line class="axis" x1="{bx0}" y1="{by0}" x2="{bx0}" y2="{by0+bh}"/>
  <text class="small" x="{bx0+bw+8}" y="{by0+bh+4}">x</text>
  <text class="small" x="{bx0-10}" y="{by0+12}" text-anchor="end">B₁</text>
  {bot_ticks}

  <!-- faint full tent -->
  <polyline points="{tent_poly}" fill="none" stroke="#d1d5db" stroke-width="2" stroke-dasharray="4 3"/>

  <!-- vertical guide at current x -->
  <line x1="{tip_x[0]}" y1="{by0}" x2="{tip_x[0]}" y2="{by0+bh}"
        stroke="#0f766e" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.7">
    <animate attributeName="x1" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="x2" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </line>

  <!-- tracer -->
  <circle cx="{tip_x[0]}" cy="{tip_y[0]}" r="7" fill="#0f766e" stroke="#fff" stroke-width="2">
    <animate attributeName="cx" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="cy" values="{values(tip_y)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </circle>

  <text class="small" x="{W/2}" y="530" text-anchor="middle">
    相对位移 x 从左扫到右：重叠从无 → 最大（x=0）→ 无，轨迹恰为三角形
  </text>
</svg>
"""


def triangle_to_quadratic_animation() -> str:
    """Animated SVG: sliding box over tent B1, area under curve traces B2(x)."""
    W, H = 960, 560
    tx0, ty0, tw, th = 80, 70, 700, 160
    bx0, by0, bw, bh = 80, 320, 700, 160

    # Top τ ∈ [-2.0, 2.0]; bottom x ∈ [-1.7, 1.7]
    t_lo, t_hi = -2.0, 2.0
    x_lo, x_hi = -1.7, 1.7

    def top_x(tau: float) -> float:
        return tx0 + (tau - t_lo) / (t_hi - t_lo) * tw

    def top_y(val: float) -> float:
        # B1 max = 1
        return ty0 + th - val * (th - 20)

    def bot_x(xv: float) -> float:
        return bx0 + (xv - x_lo) / (x_hi - x_lo) * bw

    def bot_y(val: float) -> float:
        # B2 max = 0.75
        return by0 + bh - (val / 0.75) * (bh - 24)

    def b1(tau: float) -> float:
        a = abs(tau)
        return 1.0 - a if a < 1.0 else 0.0

    def b2(x: float) -> float:
        a = abs(x)
        if a > 1.5:
            return 0.0
        if a <= 0.5:
            return 0.75 - x * x
        return 0.5 * (1.5 - a) ** 2

    def window(x: float) -> tuple[float, float]:
        return max(-1.0, x - 0.5), min(1.0, x + 0.5)

    def clip_polygon_points(x: float) -> str:
        """Area under B1 inside the sliding box; fixed vertex count for SMIL."""
        lo, hi = window(x)
        n_curve = 17  # must be constant across frames for animate points
        if hi <= lo + 1e-9:
            # degenerate: collapse to a baseline stub (still n_curve+2 verts)
            cx, cy = top_x(0.0), top_y(0.0)
            pts = [f"{cx:.1f},{cy:.1f}"] * n_curve
            pts.append(f"{cx:.1f},{cy:.1f}")
            pts.append(f"{cx:.1f},{cy:.1f}")
            return " ".join(pts)
        curve = []
        for k in range(n_curve):
            t = lo + (hi - lo) * k / (n_curve - 1)
            curve.append(f"{top_x(t):.1f},{top_y(b1(t)):.1f}")
        curve.append(f"{top_x(hi):.1f},{top_y(0):.1f}")
        curve.append(f"{top_x(lo):.1f},{top_y(0):.1f}")
        return " ".join(curve)

    n = 53
    xs = [x_lo + 0.05 + (x_hi - x_lo - 0.1) * i / (n - 1) for i in range(n)]

    move_left, tip_x, tip_y, poly_vals = [], [], [], []
    unit_w = tw / (t_hi - t_lo)
    box_h = th - 20
    box_top = ty0 + 20

    for x in xs:
        move_left.append(f"{top_x(x - 0.5):.2f}")
        tip_x.append(f"{bot_x(x):.2f}")
        tip_y.append(f"{bot_y(b2(x)):.2f}")
        poly_vals.append(clip_polygon_points(x))

    # Fixed tent outline
    tent_outline = []
    for i in range(81):
        tt = -1.0 + 2.0 * i / 80
        tent_outline.append(f"{top_x(tt):.1f},{top_y(b1(tt)):.1f}")
    tent_outline_s = " ".join(tent_outline)

    # Full B2 underlay
    b2_poly = []
    for i in range(97):
        xx = -1.6 + 3.2 * i / 96
        b2_poly.append(f"{bot_x(xx):.1f},{bot_y(b2(xx)):.1f}")
    b2_poly_s = " ".join(b2_poly)

    values = ";".join
    dur = "12s"

    top_ticks = "".join(
        f'<line x1="{top_x(t):.1f}" y1="{ty0+th}" x2="{top_x(t):.1f}" y2="{ty0+th+6}" stroke="#6b7280"/>'
        f'<text class="small" x="{top_x(t):.1f}" y="{ty0+th+22}" text-anchor="middle">{t:g}</text>'
        for t in (-1.5, -1, -0.5, 0, 0.5, 1, 1.5)
    )
    bot_ticks = "".join(
        f'<line x1="{bot_x(t):.1f}" y1="{by0+bh}" x2="{bot_x(t):.1f}" y2="{by0+bh+6}" stroke="#6b7280"/>'
        f'<text class="small" x="{bot_x(t):.1f}" y="{by0+bh+22}" text-anchor="middle">{t:g}</text>'
        for t in (-1.5, -1, -0.5, 0, 0.5, 1, 1.5)
    )

    # Escape carefully: polygon points contain spaces/commas — fine in attribute
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#fbfcfe"/>
  {STYLE}
  <text class="title" x="{W/2}" y="32" text-anchor="middle">几何动画：box 扫过三角形 → 二阶核 B₂(x)</text>

  <text class="lbl" x="{tx0}" y="58">上图：被积函数 B₁(τ)·b(x−τ)（窗内三角形下的面积 = 卷积值）</text>
  <line class="axis" x1="{tx0}" y1="{ty0+th}" x2="{tx0+tw}" y2="{ty0+th}"/>
  <line class="axis" x1="{tx0}" y1="{ty0}" x2="{tx0}" y2="{ty0+th}"/>
  <text class="small" x="{tx0+tw+8}" y="{ty0+th+4}">τ</text>
  {top_ticks}

  <!-- fixed tent B1 -->
  <polyline points="{tent_outline_s}" fill="none" stroke="#2563eb" stroke-width="2.4"/>
  <polygon points="{top_x(-1):.1f},{top_y(0):.1f} {tent_outline_s} {top_x(1):.1f},{top_y(0):.1f}"
           fill="#93c5fd" fill-opacity="0.25"/>
  <text class="math" x="{top_x(0):.1f}" y="{top_y(1) - 10:.1f}" text-anchor="middle" fill="#1d4ed8">B₁(τ)</text>

  <!-- sliding box -->
  <rect x="{move_left[0]}" y="{box_top}" width="{unit_w:.2f}" height="{box_h}"
        fill="#fdba74" fill-opacity="0.35" stroke="#c2410c" stroke-width="1.6">
    <animate attributeName="x" values="{values(move_left)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </rect>
  <text class="math" x="{tx0 + tw - 8}" y="{box_top - 8}" text-anchor="end" fill="#9a3412">b(x−τ) 滑动窗</text>

  <!-- area under tent inside window -->
  <polygon points="{poly_vals[0]}" fill="#22c55e" fill-opacity="0.55" stroke="#15803d" stroke-width="1.2">
    <animate attributeName="points" values="{values(poly_vals)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </polygon>

  <text class="small" x="{tx0 + tw/2}" y="{ty0 + th + 48}" text-anchor="middle">
    绿色 = 滑动窗截取的三角形面积；∫ B₁(τ)b(x−τ) dτ = B₂(x)
  </text>

  <rect x="820" y="80" width="18" height="14" fill="#93c5fd" stroke="#2563eb"/>
  <text class="small" x="844" y="92">固定三角 B₁</text>
  <rect x="820" y="110" width="18" height="14" fill="#fdba74" stroke="#c2410c"/>
  <text class="small" x="844" y="122">滑动 box</text>
  <rect x="820" y="140" width="18" height="14" fill="#22c55e" stroke="#15803d"/>
  <text class="small" x="844" y="152">窗内面积</text>

  <text class="lbl" x="{bx0}" y="300">下图：窗内面积随 x 变化，描出光滑凸形 B₂</text>
  <line class="axis" x1="{bx0}" y1="{by0+bh}" x2="{bx0+bw}" y2="{by0+bh}"/>
  <line class="axis" x1="{bx0}" y1="{by0}" x2="{bx0}" y2="{by0+bh}"/>
  <text class="small" x="{bx0+bw+8}" y="{by0+bh+4}">x</text>
  <text class="small" x="{bx0-10}" y="{by0+12}" text-anchor="end">B₂</text>
  {bot_ticks}

  <polyline points="{b2_poly_s}" fill="none" stroke="#d1d5db" stroke-width="2" stroke-dasharray="4 3"/>

  <line x1="{tip_x[0]}" y1="{by0}" x2="{tip_x[0]}" y2="{by0+bh}"
        stroke="#0f766e" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.7">
    <animate attributeName="x1" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="x2" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </line>
  <circle cx="{tip_x[0]}" cy="{tip_y[0]}" r="7" fill="#0f766e" stroke="#fff" stroke-width="2">
    <animate attributeName="cx" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="cy" values="{values(tip_y)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </circle>

  <text class="small" x="{W/2}" y="530" text-anchor="middle">
    与一阶动画相同的几何：积分仍是面积；被积函数从“高度 1 的重叠”换成“窗内三角形的高度曲线”
  </text>
</svg>
"""


def quadratic_to_cubic_animation() -> str:
    """Animated SVG: sliding box over B2, area under curve traces B3(x)."""
    W, H = 960, 560
    tx0, ty0, tw, th = 80, 70, 700, 160
    bx0, by0, bw, bh = 80, 320, 700, 160

    t_lo, t_hi = -2.5, 2.5
    x_lo, x_hi = -2.2, 2.2

    def top_x(tau: float) -> float:
        return tx0 + (tau - t_lo) / (t_hi - t_lo) * tw

    def top_y(val: float) -> float:
        # B2 max = 0.75
        return ty0 + th - (val / 0.75) * (th - 20)

    def bot_x(xv: float) -> float:
        return bx0 + (xv - x_lo) / (x_hi - x_lo) * bw

    def bot_y(val: float) -> float:
        # B3 max = 4/6 = 2/3
        return by0 + bh - (val / (4.0 / 6.0)) * (bh - 24)

    def b2(tau: float) -> float:
        a = abs(tau)
        if a > 1.5:
            return 0.0
        if a <= 0.5:
            return 0.75 - tau * tau
        return 0.5 * (1.5 - a) ** 2

    def b3(x: float) -> float:
        a = abs(x)
        if a >= 2.0:
            return 0.0
        if a <= 1.0:
            return (4.0 - 6.0 * x * x + 3.0 * (a ** 3)) / 6.0
        return ((2.0 - a) ** 3) / 6.0

    def window(x: float) -> tuple[float, float]:
        return max(-1.5, x - 0.5), min(1.5, x + 0.5)

    def clip_polygon_points(x: float) -> str:
        lo, hi = window(x)
        n_curve = 21
        if hi <= lo + 1e-9:
            cx, cy = top_x(0.0), top_y(0.0)
            pts = [f"{cx:.1f},{cy:.1f}"] * n_curve
            pts += [f"{cx:.1f},{cy:.1f}", f"{cx:.1f},{cy:.1f}"]
            return " ".join(pts)
        curve = []
        for k in range(n_curve):
            t = lo + (hi - lo) * k / (n_curve - 1)
            curve.append(f"{top_x(t):.1f},{top_y(b2(t)):.1f}")
        curve.append(f"{top_x(hi):.1f},{top_y(0):.1f}")
        curve.append(f"{top_x(lo):.1f},{top_y(0):.1f}")
        return " ".join(curve)

    n = 57
    xs = [x_lo + 0.08 + (x_hi - x_lo - 0.16) * i / (n - 1) for i in range(n)]

    move_left, tip_x, tip_y, poly_vals = [], [], [], []
    unit_w = tw / (t_hi - t_lo)
    box_h = th - 20
    box_top = ty0 + 20

    for x in xs:
        move_left.append(f"{top_x(x - 0.5):.2f}")
        tip_x.append(f"{bot_x(x):.2f}")
        tip_y.append(f"{bot_y(b3(x)):.2f}")
        poly_vals.append(clip_polygon_points(x))

    b2_outline = []
    for i in range(97):
        tt = -1.5 + 3.0 * i / 96
        b2_outline.append(f"{top_x(tt):.1f},{top_y(b2(tt)):.1f}")
    b2_outline_s = " ".join(b2_outline)

    b3_poly = []
    for i in range(113):
        xx = -2.1 + 4.2 * i / 112
        b3_poly.append(f"{bot_x(xx):.1f},{bot_y(b3(xx)):.1f}")
    b3_poly_s = " ".join(b3_poly)

    values = ";".join
    dur = "14s"

    top_ticks = "".join(
        f'<line x1="{top_x(t):.1f}" y1="{ty0+th}" x2="{top_x(t):.1f}" y2="{ty0+th+6}" stroke="#6b7280"/>'
        f'<text class="small" x="{top_x(t):.1f}" y="{ty0+th+22}" text-anchor="middle">{t:g}</text>'
        for t in (-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2)
    )
    bot_ticks = "".join(
        f'<line x1="{bot_x(t):.1f}" y1="{by0+bh}" x2="{bot_x(t):.1f}" y2="{by0+bh+6}" stroke="#6b7280"/>'
        f'<text class="small" x="{bot_x(t):.1f}" y="{by0+bh+22}" text-anchor="middle">{t:g}</text>'
        for t in (-2, -1, 0, 1, 2)
    )

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#fbfcfe"/>
  {STYLE}
  <text class="title" x="{W/2}" y="32" text-anchor="middle">几何动画：box 扫过 B₂ → 三次核 B₃(x)</text>

  <text class="lbl" x="{tx0}" y="58">上图：被积函数 B₂(τ)·b(x−τ)（滑动窗重叠部分的面积 = 卷积值）</text>
  <line class="axis" x1="{tx0}" y1="{ty0+th}" x2="{tx0+tw}" y2="{ty0+th}"/>
  <line class="axis" x1="{tx0}" y1="{ty0}" x2="{tx0}" y2="{ty0+th}"/>
  <text class="small" x="{tx0+tw+8}" y="{ty0+th+4}">τ</text>
  {top_ticks}

  <polyline points="{b2_outline_s}" fill="none" stroke="#2563eb" stroke-width="2.4"/>
  <polygon points="{top_x(-1.5):.1f},{top_y(0):.1f} {b2_outline_s} {top_x(1.5):.1f},{top_y(0):.1f}"
           fill="#93c5fd" fill-opacity="0.22"/>
  <text class="math" x="{top_x(0):.1f}" y="{top_y(0.75) - 10:.1f}" text-anchor="middle" fill="#1d4ed8">B₂(τ)</text>

  <rect x="{move_left[0]}" y="{box_top}" width="{unit_w:.2f}" height="{box_h}"
        fill="#fdba74" fill-opacity="0.35" stroke="#c2410c" stroke-width="1.6">
    <animate attributeName="x" values="{values(move_left)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </rect>
  <text class="math" x="{tx0 + tw - 8}" y="{box_top - 8}" text-anchor="end" fill="#9a3412">b(x−τ) 滑动窗</text>

  <polygon points="{poly_vals[0]}" fill="#22c55e" fill-opacity="0.55" stroke="#15803d" stroke-width="1.2">
    <animate attributeName="points" values="{values(poly_vals)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </polygon>

  <text class="small" x="{tx0 + tw/2}" y="{ty0 + th + 48}" text-anchor="middle">
    绿色 = 滑动窗口与 B₂ 的重叠部分面积；∫ B₂(τ)b(x−τ) dτ = B₃(x)
  </text>

  <rect x="820" y="80" width="18" height="14" fill="#93c5fd" stroke="#2563eb"/>
  <text class="small" x="844" y="92">固定 B₂</text>
  <rect x="820" y="110" width="18" height="14" fill="#fdba74" stroke="#c2410c"/>
  <text class="small" x="844" y="122">滑动 box</text>
  <rect x="820" y="140" width="18" height="14" fill="#22c55e" stroke="#15803d"/>
  <text class="small" x="844" y="152">重叠面积</text>

  <text class="lbl" x="{bx0}" y="300">下图：重叠面积随 x 变化，描出 C² 的三次核 B₃</text>
  <line class="axis" x1="{bx0}" y1="{by0+bh}" x2="{bx0+bw}" y2="{by0+bh}"/>
  <line class="axis" x1="{bx0}" y1="{by0}" x2="{bx0}" y2="{by0+bh}"/>
  <text class="small" x="{bx0+bw+8}" y="{by0+bh+4}">x</text>
  <text class="small" x="{bx0-10}" y="{by0+12}" text-anchor="end">B₃</text>
  {bot_ticks}

  <polyline points="{b3_poly_s}" fill="none" stroke="#d1d5db" stroke-width="2" stroke-dasharray="4 3"/>

  <line x1="{tip_x[0]}" y1="{by0}" x2="{tip_x[0]}" y2="{by0+bh}"
        stroke="#0f766e" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.7">
    <animate attributeName="x1" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="x2" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </line>
  <circle cx="{tip_x[0]}" cy="{tip_y[0]}" r="7" fill="#0f766e" stroke="#fff" stroke-width="2">
    <animate attributeName="cx" values="{values(tip_x)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="cy" values="{values(tip_y)}" dur="{dur}"
             repeatCount="indefinite" calcMode="linear"/>
  </circle>

  <text class="small" x="{W/2}" y="530" text-anchor="middle">
    仍是同一句话：积分 = 滑动窗口重叠部分的面积；B₂ 更光滑，故 B₃ 达到 C²
  </text>
</svg>
"""


def main() -> None:
    write("discrete-vs-continuous.svg", discrete_vs_continuous())
    write("basis-functions.svg", basis_functions_fixed())
    write("local-support.svg", local_support())
    write("control-polygon.svg", control_polygon())
    write("basis-weighted-curve-animation.svg", basis_weighted_curve())
    write("global-basis-fit-animation.svg", global_basis_fit_animation())
    write("cumulative-form.svg", cumulative_form())
    write("split-vs-se3.svg", split_vs_se3())
    write("slam-pipeline.svg", slam_pipeline())
    write("box-to-triangle-animation.svg", box_to_triangle_animation())
    write("triangle-to-quadratic-animation.svg", triangle_to_quadratic_animation())
    write("quadratic-to-cubic-animation.svg", quadratic_to_cubic_animation())


if __name__ == "__main__":
    main()
