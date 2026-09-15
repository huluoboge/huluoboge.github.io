from html import escape
from pathlib import Path


OUT = Path(__file__).resolve().parents[1] / "figures" / "preintegration-three-systems.svg"


def multiline_text(x, y, lines, cls, size=15):
    rendered = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else size
        rendered.append(
            f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>'
        )
    return f'<text x="{x}" y="{y}" text-anchor="middle" class="{cls}">{"".join(rendered)}</text>'


def box(x, y, w, h, title, subtitle, fill, stroke="#333333"):
    subtitle_lines = subtitle if isinstance(subtitle, list) else [subtitle]
    subtitle_y = y + 50 if len(subtitle_lines) == 1 else y + 45
    return f'''
  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>
    <text x="{x + w/2}" y="{y + 25}" text-anchor="middle" class="box-title">{escape(title)}</text>
    {multiline_text(x + w/2, subtitle_y, subtitle_lines, 'box-sub', 16)}
  </g>'''


def arrow(x1, y1, x2, y2, label="", color="#333333"):
    midx = (x1 + x2) / 2
    midy = (y1 + y2) / 2 - 9
    text = f'<text x="{midx}" y="{midy}" text-anchor="middle" class="arrow-label">{label}</text>' if label else ""
    return f'''
  <g>
    <path d="M {x1} {y1} C {(x1+x2)/2} {y1}, {(x1+x2)/2} {y2}, {x2} {y2}" fill="none" stroke="{color}" stroke-width="1.4" marker-end="url(#arrow)"/>
    {text}
  </g>'''


def main():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="720" viewBox="0 0 1180 720" role="img" aria-labelledby="title desc">
  <title id="title">VINS、LIO-SAM 与 LVI-SAM 中的预积分信息流</title>
  <desc id="desc">图示三类系统中 IMU 预积分因子与视觉、激光约束的关系。</desc>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#333333"/>
    </marker>
    <style>
      .title {{ font: 700 26px 'Noto Sans CJK SC', 'Microsoft YaHei', Arial, sans-serif; fill: #111111; }}
      .subtitle {{ font: 15px 'Noto Sans CJK SC', 'Microsoft YaHei', Arial, sans-serif; fill: #555555; }}
      .section {{ font: 700 18px 'Noto Sans CJK SC', 'Microsoft YaHei', Arial, sans-serif; fill: #222222; }}
      .box-title {{ font: 700 17px 'Noto Sans CJK SC', 'Microsoft YaHei', Arial, sans-serif; fill: #111111; }}
      .box-sub {{ font: 13px 'Noto Sans CJK SC', 'Microsoft YaHei', Arial, sans-serif; fill: #444444; }}
      .arrow-label {{ font: 12px 'Noto Sans CJK SC', 'Microsoft YaHei', Arial, sans-serif; fill: #555555; }}
      .note {{ font: 13px 'Noto Sans CJK SC', 'Microsoft YaHei', Arial, sans-serif; fill: #444444; }}
      .lane {{ fill: none; stroke: #D8D8D8; stroke-width: 1; stroke-dasharray: 6 6; }}
    </style>
  </defs>

  <rect width="1180" height="720" fill="#FFFFFF"/>
  <text x="590" y="42" text-anchor="middle" class="title">同一段 IMU 预积分，在三种系统中的落点</text>
  <text x="590" y="70" text-anchor="middle" class="subtitle">预积分因子保持同一语义；视觉、激光与状态管理决定系统形态</text>

  <text x="70" y="120" class="section">输入时间流</text>
  <text x="365" y="120" class="section">区间测量与因子</text>
  <text x="720" y="120" class="section">三个案例中的后端组织</text>

  <line x1="45" y1="330" x2="1135" y2="330" class="lane"/>
  <line x1="45" y1="520" x2="1135" y2="520" class="lane"/>

{box(70, 150, 190, 70, '图像帧', '特征跟踪 / 关键帧', '#EAF3FF', '#4B83C4')}
{box(70, 270, 190, 70, '高频 IMU', '角速度 / 比力', '#FFF3E0', '#C47A2C')}
{box(70, 390, 190, 70, '激光帧', '特征提取 / 扫描匹配', '#EAF7EA', '#4C9B58')}

{box(340, 270, 230, 78, '关键帧区间预积分', 'ΔR, Δv, Δp, J, Σ', '#FFF7E8', '#C47A2C')}
{box(610, 160, 210, 72, '视觉重投影因子', '像素观测约束位姿', '#EAF3FF', '#4B83C4')}
{box(610, 390, 210, 72, '激光几何因子', '米制结构约束位姿', '#EAF7EA', '#4C9B58')}
{box(610, 275, 210, 72, 'IMU 预积分因子', '连接相邻关键帧状态', '#FFF3E0', '#C47A2C')}

{box(900, 140, 215, 82, 'VINS', ['视觉因子 + IMU 因子', '滑动窗口优化'], '#F7FAFF', '#4B83C4')}
{box(900, 270, 215, 82, 'LIO-SAM', ['激光因子 + IMU 因子', '因子图平滑'], '#F7FCF7', '#4C9B58')}
{box(900, 420, 215, 88, 'LVI-SAM', ['视觉 + 激光 + IMU', '联合平滑估计'], '#F7F3FF', '#7D68B3')}

{arrow(260, 185, 610, 195, '形成视觉约束')}
{arrow(260, 305, 340, 309, '区间内累积')}
{arrow(570, 309, 610, 311, '构造因子')}
{arrow(260, 425, 610, 426, '形成激光约束')}

{arrow(820, 196, 900, 181, '')}
{arrow(820, 311, 900, 181, '')}
{arrow(820, 311, 900, 311, '')}
{arrow(820, 426, 900, 311, '')}
{arrow(820, 196, 900, 462, '')}
{arrow(820, 311, 900, 462, '')}
{arrow(820, 426, 900, 462, '')}

  <text x="92" y="575" class="note">读案例时可固定 IMU 主线：样本缓存 → 区间封存 → 因子残差 → 状态更新。</text>
  <text x="92" y="602" class="note">系统差异来自外部几何约束：VINS 看图像，LIO-SAM 看点云，LVI-SAM 同时接入图像与点云。</text>
  <text x="92" y="629" class="note">优化结果会继续反馈到下一关键帧初值、bias 修正、重新预积分和历史状态管理。</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
