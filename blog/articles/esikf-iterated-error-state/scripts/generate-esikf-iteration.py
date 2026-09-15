from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIGURE = ROOT / "figures" / "esikf-iteration-loop.svg"


def box(x, y, w, h, title, lines, fill, stroke):
    if isinstance(lines, str):
        lines = [lines]
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
        f'<text x="{x + w / 2}" y="{y + 28}" text-anchor="middle" class="box-title">{title}</text>',
    ]
    for idx, line in enumerate(lines):
        parts.append(f'<text x="{x + w / 2}" y="{y + 58 + idx * 24}" text-anchor="middle" class="box-text">{line}</text>')
    return "\n".join(parts)


def arrow(x1, y1, x2, y2, label=""):
    text = ""
    if label:
        text = f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 12}" text-anchor="middle" class="arrow-label">{label}</text>'
    return f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="#44546A" stroke-width="2.2" marker-end="url(#arrow)"/>\n{text}'


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="720" viewBox="0 0 1240 720" role="img" aria-labelledby="title desc">
  <title id="title">ESIKF 的一次观测内部迭代</title>
  <desc id="desc">图示预测先验、残差线性化、误差状态求解、误差注入和重新线性化之间的关系。</desc>
  <defs>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
      <path d="M2,2 L10,6 L2,10 Z" fill="#44546A"/>
    </marker>
    <style>
      .title {{ font: 700 28px Arial, 'Noto Sans CJK SC', sans-serif; fill: #1F2933; }}
      .subtitle {{ font: 16px Arial, 'Noto Sans CJK SC', sans-serif; fill: #52616B; }}
      .box-title {{ font: 700 18px Arial, 'Noto Sans CJK SC', sans-serif; fill: #1F2933; }}
      .box-text {{ font: 15px Arial, 'Noto Sans CJK SC', sans-serif; fill: #334E68; }}
      .arrow-label {{ font: 14px Arial, 'Noto Sans CJK SC', sans-serif; fill: #52616B; }}
      .note {{ font: 15px Arial, 'Noto Sans CJK SC', sans-serif; fill: #334E68; }}
    </style>
  </defs>
  <rect width="1240" height="720" fill="#FFFFFF"/>
  <text x="620" y="48" text-anchor="middle" class="title">ESIKF：一次观测内部的误差状态迭代</text>
  <text x="620" y="78" text-anchor="middle" class="subtitle">历史信息形成预测先验；当前观测形成非线性残差；迭代在局部误差状态上完成</text>

  {box(60, 160, 210, 104, 'IMU 传播', ['预测名义状态', '预测协方差'], '#FFF3E0', '#C47A2C')}
  {box(330, 150, 230, 124, '当前线性化点', ['第 l 轮名义状态', '局部误差坐标'], '#F5F7FA', '#8795A1')}
  {box(620, 140, 245, 144, '观测线性化', ['残差 r(l)', 'Jacobian H(l)', '先验偏差 δxp(l)'], '#EEF6FF', '#4B83C4')}
  {box(925, 150, 235, 124, '求解误差增量', ['带先验最小二乘', '得到 η(l)'], '#F7F3FF', '#7D68B3')}

  {arrow(270, 212, 330, 212, '先验锚点')}
  {arrow(560, 212, 620, 212, '评价残差')}
  {arrow(865, 212, 925, 212, '正规方程')}

  {box(450, 410, 265, 120, '误差注入', ['X(l+1) = X(l) ⊞ η(l)', '重置误差均值'], '#F2F8F2', '#4C9B58')}
  {box(790, 410, 245, 120, '停止或继续', ['增量足够小', '达到迭代上限'], '#FFF7E8', '#C47A2C')}

  {arrow(1042, 274, 675, 410, '注入')}
  {arrow(715, 470, 790, 470, '检查')}
  <path d="M 790 500 C 625 610, 405 575, 445 274" fill="none" stroke="#44546A" stroke-width="2.2" marker-end="url(#arrow)"/>
  <text x="545" y="608" text-anchor="middle" class="arrow-label">继续时回到新的线性化点</text>
  <path d="M 1035 470 L 1135 470 L 1135 595" fill="none" stroke="#44546A" stroke-width="2.2" marker-end="url(#arrow)"/>
  <text x="1110" y="452" text-anchor="middle" class="arrow-label">停止</text>

  <rect x="65" y="595" width="780" height="72" rx="8" fill="#F8FAFC" stroke="#D9E2EC" stroke-width="1.5"/>
  <text x="92" y="626" class="note">每一轮都求局部误差增量，完整状态通过注入动作更新。</text>
  <text x="92" y="654" class="note">先验始终来自传播结果，观测项随当前线性化点重新计算。</text>
  <rect x="910" y="590" width="250" height="82" rx="8" fill="#F2F8F2" stroke="#4C9B58" stroke-width="2"/>
  <text x="1035" y="624" text-anchor="middle" class="box-title">后验状态</text>
  <text x="1035" y="654" text-anchor="middle" class="box-text">进入下一轮 IMU 传播</text>
</svg>
'''

FIGURE.write_text(svg, encoding="utf-8")
print(FIGURE.relative_to(ROOT))
