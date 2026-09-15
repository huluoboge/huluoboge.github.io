from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIGURE = ROOT / "figures" / "esikf-three-systems.svg"


def box(x, y, w, h, title, lines, fill, stroke):
    if isinstance(lines, str):
        lines = [lines]
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
        f'<text x="{x + w / 2}" y="{y + 27}" text-anchor="middle" class="box-title">{title}</text>',
    ]
    for idx, line in enumerate(lines):
        parts.append(f'<text x="{x + w / 2}" y="{y + 56 + idx * 22}" text-anchor="middle" class="box-text">{line}</text>')
    return "\n".join(parts)


def arrow(x1, y1, x2, y2, label=""):
    text = ""
    if label:
        text = f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 11}" text-anchor="middle" class="arrow-label">{label}</text>'
    return f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="#44546A" stroke-width="2.1" marker-end="url(#arrow)"/>\n{text}'


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="780" viewBox="0 0 1300 780" role="img" aria-labelledby="title desc">
  <title id="title">FAST-LIO2、R3LIVE 与 FAST-LIVO2 的 ESIKF 信息流</title>
  <desc id="desc">图示三类系统中 IMU 传播、外部观测残差、迭代误差状态更新和地图反馈的共同结构。</desc>
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
  <rect width="1300" height="780" fill="#FFFFFF"/>
  <text x="650" y="46" text-anchor="middle" class="title">同一个 ESIKF 主干，三种外部观测组织</text>
  <text x="650" y="76" text-anchor="middle" class="subtitle">IMU 负责传播；LiDAR 和视觉负责构造当前观测残差；地图在更新后继续反馈</text>

  {box(70, 150, 190, 96, '高频 IMU', ['角速度', '比力', '时间戳'], '#FFF7E8', '#C47A2C')}
  {box(325, 137, 220, 122, '状态传播', ['名义状态', '协方差', '运动补偿初值'], '#FFF3E0', '#C47A2C')}
  {box(620, 137, 230, 122, 'ESIKF 更新', ['残差与 H', '多轮误差注入', '输出后验状态'], '#EEF6FF', '#4B83C4')}
  {box(940, 137, 235, 122, '地图反馈', ['更新局部地图', '维护颜色或视觉信息', '提供下一帧查询'], '#F2F8F2', '#4C9B58')}

  {arrow(260, 198, 325, 198, '预测')}
  {arrow(545, 198, 620, 198, '先验')}
  {arrow(850, 198, 940, 198, '后验')}
  <path d="M 1040 259 C 995 330, 790 340, 735 259" fill="none" stroke="#4C9B58" stroke-width="2.1" marker-end="url(#arrow)"/>
  <text x="905" y="340" text-anchor="middle" class="arrow-label">地图参与下一轮残差</text>

  {box(95, 430, 220, 92, 'FAST-LIO2', ['LiDAR 点到地图几何', '直接扫描到地图更新'], '#F7FCF7', '#4C9B58')}
  {box(390, 430, 220, 92, 'R3LIVE', ['LiDAR 几何估计', '视觉颜色与纹理更新'], '#F7F3FF', '#7D68B3')}
  {box(685, 430, 230, 92, 'FAST-LIVO2', ['LiDAR 几何约束', '视觉直接约束'], '#F7FAFF', '#4B83C4')}
  {box(990, 420, 220, 112, '公共读法', ['传感器进来', '残差进入 Hδx', '状态回到地图'], '#F5F7FA', '#8795A1')}

  {arrow(205, 430, 635, 259, 'LiDAR 残差')}
  {arrow(500, 430, 710, 259, '几何 + 颜色')}
  {arrow(800, 430, 775, 259, '几何 + 视觉')}
  {arrow(990, 476, 850, 236, '统一估计骨架')}

  <rect x="80" y="625" width="1095" height="86" rx="8" fill="#F8FAFC" stroke="#D9E2EC" stroke-width="1.5"/>
  <text x="108" y="657" class="note">阅读顺序可以保持一致：先找 IMU 传播，再找当前观测残差，随后看误差状态迭代，最后追踪地图反馈。</text>
  <text x="108" y="687" class="note">三类系统的主要差异在外部观测和地图表达；公共主干是传播、线性化、求解、注入和反馈。</text>
</svg>
'''

FIGURE.write_text(svg, encoding="utf-8")
print(FIGURE.relative_to(ROOT))
