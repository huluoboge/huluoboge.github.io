
<svg width="600" height="100" viewBox="-3 -1 7 2">
  <!-- 网格 -->
  <g stroke="black" stroke-width="0.02">
    <line x1="-3" y1="0" x2="3" y2="0"/>
    <line x1="-2" y1="-0.5" x2="-2" y2="0.5"/>
    <line x1="-1" y1="-0.5" x2="-1" y2="0.5"/>
    <line x1="0" y1="-0.5" x2="0" y2="0.5"/>
    <line x1="1" y1="-0.5" x2="1" y2="0.5"/>
    <line x1="2" y1="-0.5" x2="2" y2="0.5"/>
  </g>

  <!-- 中心节点 -->
  <rect x="-0.5" y="-0.5" width="1" height="1" fill="blue" />
  <text x="0" y="-0.6" font-size="0.15" text-anchor="middle">中心</text>

  <!-- 左右邻居 -->
  <rect x="-1.5" y="-0.5" width="1" height="1" fill="red" opacity="0.5" />
  <rect x="0.5" y="-0.5" width="1" height="1" fill="red" opacity="0.5" />

  <!-- 支持域虚线 -->
  <line x1="-1.5" y1="0.7" x2="1.5" y2="0.7" stroke="green" stroke-width="0.05" stroke-dasharray="0.1,0.05"/>
  <line x1="-1.5" y1="0.75" x2="-1.5" y2="0.65" stroke="green" stroke-width="0.05"/>
  <line x1="1.5" y1="0.75" x2="1.5" y2="0.65" stroke="green" stroke-width="0.05"/>
  <text x="0" y="0.9" font-size="0.15" text-anchor="middle" fill="green">支持域 [-1.5,1.5]</text>
</svg>


