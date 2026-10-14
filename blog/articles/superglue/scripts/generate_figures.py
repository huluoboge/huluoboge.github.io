from pathlib import Path
from html import escape


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def box(x, y, width, height, fill, title, detail):
    return f"""
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="16"
          fill="{fill}" stroke="#35516b" stroke-width="1.5"/>
    <text x="{x + width / 2}" y="{y + 34}" class="title" text-anchor="middle">{escape(title)}</text>
    <text x="{x + width / 2}" y="{y + 61}" class="detail" text-anchor="middle">{escape(detail)}</text>
    """


svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="300" viewBox="0 0 1180 300" role="img" aria-label="SuperGlue 从局部特征到部分匹配的信息流">
<defs>
  <marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
    <path d="M0,0 L9,4.5 L0,9 Z" fill="#476581"/>
  </marker>
</defs>
<style>
  text {{ font-family: "Noto Sans CJK SC", "Microsoft YaHei", sans-serif; fill: #18334d; }}
  .title {{ font-size: 19px; font-weight: 700; }}
  .detail {{ font-size: 15px; }}
  .small {{ font-size: 15px; fill: #3e5970; }}
  .arrow {{ stroke: #476581; stroke-width: 2.5; fill: none; marker-end: url(#arrow); }}
</style>
<rect x="0" y="0" width="1180" height="300" fill="#f8fbfd"/>
{box(25, 94, 155, 90, '#e4eff8', '两组局部特征', '坐标、置信度、描述符')}
{box(220, 94, 130, 90, '#e4eff8', '关键点编码', '外观 + 位置')}
{box(390, 94, 195, 90, '#d9eee8', '注意力图网络', '图内 / 图间交替')}
{box(625, 94, 125, 90, '#d9eee8', '两两评分', '描述符内积')}
{box(790, 94, 175, 90, '#f9e8d4', '最优匹配层', 'dustbin + Sinkhorn')}
{box(1005, 94, 150, 90, '#f9e8d4', '部分分配', '对应 / 无匹配')}
<path class="arrow" d="M185 139 H214"/>
<path class="arrow" d="M355 139 H384"/>
<path class="arrow" d="M590 139 H619"/>
<path class="arrow" d="M755 139 H784"/>
<path class="arrow" d="M970 139 H999"/>
<text x="490" y="224" class="small" text-anchor="middle">学习候选点对的分数：利用两幅图的上下文</text>
<path d="M390 199 H585" stroke="#4a9682" stroke-width="2"/>
<text x="875" y="224" class="small" text-anchor="middle">约束整张匹配表：一对一，允许拒配</text>
<path d="M790 199 H965" stroke="#d4924c" stroke-width="2"/>
</svg>
"""

(OUT / "superglue-information-flow.svg").write_text(svg, encoding="utf-8")
