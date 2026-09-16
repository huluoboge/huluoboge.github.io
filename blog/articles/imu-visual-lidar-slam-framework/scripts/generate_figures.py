from pathlib import Path
import html


OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def esc(text):
    return html.escape(text, quote=True)


def box(x, y, w, h, text, fill="#ffffff", stroke="#2f3a4a", color="#20242a", size=15, weight="500"):
    lines = text.split("\n")
    line_h = 18
    start_y = y + h / 2 - (len(lines) - 1) * line_h / 2 + 5
    tspan = "".join(
        f'<tspan x="{x + w / 2}" y="{start_y + i * line_h}">{esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return f'''
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>
  <text font-family="Arial, 'Noto Sans CJK SC', sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="middle">{tspan}</text>'''


def line(x1, y1, x2, y2, color="#596579", width=1.3):
    return f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>'


def elbow(x1, y1, x2, y2, color="#596579"):
    mid_y = (y1 + y2) / 2
    return f'<path d="M {x1} {y1} L {x1} {mid_y} L {x2} {mid_y} L {x2} {y2}" fill="none" stroke="{color}" stroke-width="1.3"/>'


def svg(width, height, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#fbfcfe"/>
  <style>
    text {{ dominant-baseline: middle; }}
  </style>
{body}
</svg>
'''


def write_knowledge_tree():
    body = []
    body.append(box(405, 28, 270, 56, "IMU 在 SLAM 中的两种用法", fill="#1f2937", stroke="#1f2937", color="#ffffff", size=17, weight="700"))
    body.append(box(390, 112, 300, 68, "同一组惯性基础\n姿态传播 / bias / 噪声协方差 / Jacobian", fill="#f8fafc", stroke="#64748b", size=14, weight="700"))
    body.append(line(540, 84, 540, 112, color="#64748b"))

    left_x = 90
    right_x = 650
    trunk_y = 230
    body.append(elbow(540, 180, left_x + 160, trunk_y, color="#b7791f"))
    body.append(elbow(540, 180, right_x + 160, trunk_y, color="#0f766e"))
    body.append(box(left_x, trunk_y, 320, 76, "预积分因子图路线\nIMU 样本压缩为关键帧间约束\n历史状态在窗口或图中联合优化", fill="#fff4dc", stroke="#b7791f", size=14, weight="700"))
    body.append(box(right_x, trunk_y, 320, 76, "ESIKF 迭代更新路线\nIMU 传播当前状态和协方差\n当前帧残差反复线性化并注入", fill="#e0f7f0", stroke="#0f766e", size=14, weight="700"))

    left_nodes = [
        (70, 350, "优化式 VIO\nOKVIS / VINS-Mono / VINS-Fusion", "视觉特征重投影 + IMU 预积分"),
        (70, 465, "完整视觉惯性 SLAM\nORB-SLAM3", "局部 BA / 回环 / 多地图 + IMU"),
        (70, 580, "因子图式 LIO\nLIO-SAM", "LiDAR 里程计 / GPS / 回环 / IMU 因子"),
        (70, 695, "因子图式 LVI\nLVI-SAM", "视觉约束接入 LiDAR-Inertial smoothing"),
    ]
    right_nodes = [
        (670, 350, "特征式 LIO 滤波\nFAST-LIO", "LiDAR 特征残差 + IMU 先验"),
        (670, 465, "直接式 LIO 滤波\nFAST-LIO2", "原始点到地图残差 + ikd-Tree"),
        (670, 580, "紧耦合 LIVO\nR2LIVE", "滤波里程计 + 因子图优化"),
        (670, 695, "彩色 LIVO 建图\nR3LIVE", "LIO 几何主干 + 视觉颜色/光度"),
        (670, 810, "直接式 LIVO 滤波\nFAST-LIVO / FAST-LIVO2", "LiDAR 几何 + 视觉光度顺序更新"),
    ]

    for nodes, stroke, fill, start_x in [(left_nodes, "#b7791f", "#fffaf0", left_x), (right_nodes, "#0f766e", "#f0fdfa", right_x)]:
        body.append(line(start_x + 160, trunk_y + 76, nodes[0][0] + 160, nodes[0][1], color=stroke, width=1.6))
        for i, (x, y, title, note) in enumerate(nodes):
            body.append(box(x, y, 320, 62, title, fill=fill, stroke=stroke, size=14, weight="700"))
            body.append(box(x, y + 66, 320, 42, note, fill="#ffffff", stroke="#d6dee8", size=12))
            if i < len(nodes) - 1:
                body.append(line(x + 160, y + 108, nodes[i + 1][0] + 160, nodes[i + 1][1], color=stroke, width=1.6))

    body.append(box(430, 385, 220, 56, "分叉点\n历史保留为图\n或压缩为当前先验", fill="#ffffff", stroke="#94a3b8", size=13, weight="700"))
    body.append(line(390, 410, 430, 410, color="#94a3b8"))
    body.append(line(650, 410, 670, 410, color="#94a3b8"))

    body.append(box(430, 520, 220, 78, "共同闭环\nIMU 预测运动\n外部观测校正漂移\n地图反馈服务下一帧", fill="#ffffff", stroke="#94a3b8", size=13, weight="700"))
    body.append(line(390, 535, 430, 555, color="#94a3b8"))
    body.append(line(670, 535, 650, 555, color="#94a3b8"))

    (OUT / "knowledge-tree.svg").write_text(svg(1080, 945, "\n".join(body)), encoding="utf-8")


def write_architectures():
    body = []
    body.append(box(40, 35, 240, 50, "优化式路线", fill="#fff0d8", stroke="#b7791f", size=17, weight="700"))
    body.append(box(600, 35, 240, 50, "滤波式路线", fill="#e0f7f0", stroke="#0f766e", size=17, weight="700"))

    left = [
        (60, 130, "关键帧状态"),
        (60, 225, "IMU 预积分\n形成相邻状态因子"),
        (60, 320, "视觉 / LiDAR 因子\n重投影、点到平面、回环"),
        (60, 430, "滑动窗口或因子图\n统一重线性化和边缘化"),
        (60, 540, "代表系统\nVINS、OKVIS、ORB-SLAM3\nLIO-SAM、LVI-SAM"),
    ]
    right = [
        (620, 130, "上一帧后验状态"),
        (620, 225, "IMU 连续传播\n得到当前先验和协方差"),
        (620, 320, "当前帧观测残差\n点到地图、投影、光度"),
        (620, 430, "ESIKF 迭代更新\n局部误差求解并注入"),
        (620, 540, "代表系统\nFAST-LIO、FAST-LIO2\nR2LIVE、R3LIVE、FAST-LIVO2"),
    ]
    for seq, stroke, fill in [(left, "#b7791f", "#fffaf0"), (right, "#0f766e", "#f0fdfa")]:
        for i, (x, y, label) in enumerate(seq):
            body.append(box(x, y, 220, 64, label, fill=fill, stroke=stroke, size=14))
            if i:
                px, py, _ = seq[i - 1]
                body.append(line(px + 110, py + 64, x + 110, y, color=stroke, width=1.6))

    body.append(box(330, 250, 220, 150, "共同数学底座\n\n李群扰动\n噪声传播\nJacobian\nbias 估计\n协方差权重", fill="#f8fafc", stroke="#64748b", size=14, weight="700"))
    body.append(line(280, 462, 330, 350, color="#64748b"))
    body.append(line(620, 462, 550, 350, color="#64748b"))
    body.append(box(338, 535, 204, 50, "分歧点：历史信息保留成图，还是压缩成当前先验", fill="#ffffff", stroke="#cbd5e1", size=13))
    (OUT / "two-architectures.svg").write_text(svg(900, 620, "\n".join(body)), encoding="utf-8")


if __name__ == "__main__":
    write_knowledge_tree()
    write_architectures()
