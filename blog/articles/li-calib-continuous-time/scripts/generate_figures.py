#!/usr/bin/env python3
"""Generate SVG figures for the LI-Calib blog article."""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def write(name: str, svg: str) -> None:
    path = OUT / name
    path.write_text(svg.strip() + "\n", encoding="utf-8")
    print(f"wrote {path}")


def pipeline_svg() -> str:
    """Redraw paper Fig. 2: LI-Calib pipeline (Chinese labels for the blog)."""
    return r"""
<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="520" viewBox="0 0 1180 520">
  <rect width="1180" height="520" fill="#fbfcfe"/>
  <defs>
    <marker id="arr" markerWidth="9" markerHeight="9" refX="8" refY="3.5" orient="auto">
      <path d="M0,0 L8,3.5 L0,7 Z" fill="#4b5563"/>
    </marker>
    <marker id="arrd" markerWidth="9" markerHeight="9" refX="8" refY="3.5" orient="auto">
      <path d="M0,0 L8,3.5 L0,7 Z" fill="#6b7280"/>
    </marker>
  </defs>
  <style>
    text { font-family: 'Noto Sans CJK SC', 'Source Han Sans SC', 'PingFang SC', Arial, sans-serif; }
    .cap { font-size: 15px; font-weight: 700; fill: #1f2937; }
    .stg { font-size: 13px; font-weight: 700; fill: #374151; }
    .blk { font-size: 13px; font-weight: 600; fill: #1f2937; }
    .math { font-size: 12px; font-weight: 600; fill: #1f2937; font-family: 'Times New Roman', 'Noto Serif', serif; }
    .sensor { font-size: 14px; font-weight: 700; fill: #1e3a5f; }
  </style>

  <!-- Sensors -->
  <circle cx="70" cy="175" r="36" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.6"/>
  <text class="sensor" x="70" y="180" text-anchor="middle">IMU</text>
  <circle cx="70" cy="390" r="36" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.6"/>
  <text class="sensor" x="70" y="395" text-anchor="middle">LiDAR</text>

  <!-- LiDAR odometry (standalone, bottom-left of init area) -->
  <rect x="150" y="365" width="150" height="50" rx="6" fill="#fde68a" stroke="#b45309" stroke-width="1.3"/>
  <text class="blk" x="225" y="395" text-anchor="middle">LiDAR 里程计</text>

  <!-- ========== Initialization ========== -->
  <rect x="150" y="70" width="250" height="230" rx="14" fill="none" stroke="#9ca3af" stroke-width="1.5"/>
  <text class="stg" x="275" y="95" text-anchor="middle">初始化</text>

  <rect x="175" y="120" width="200" height="48" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.3"/>
  <text class="blk" x="275" y="149" text-anchor="middle">旋转曲线</text>

  <rect x="175" y="210" width="200" height="58" rx="6" fill="#f59e0b" stroke="#b45309" stroke-width="1.3"/>
  <text class="blk" x="275" y="233" text-anchor="middle">初始外参旋转</text>
  <text class="math" x="275" y="254" text-anchor="middle"><tspan baseline-shift="super" font-size="9">I</tspan><tspan baseline-shift="sub" font-size="9">L</tspan>q</text>

  <!-- ========== Data association ========== -->
  <rect x="440" y="70" width="250" height="230" rx="14" fill="none" stroke="#9ca3af" stroke-width="1.5"/>
  <text class="stg" x="565" y="95" text-anchor="middle">数据关联</text>

  <rect x="465" y="125" width="200" height="58" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.3"/>
  <text class="blk" x="565" y="148" text-anchor="middle">带运动预测的</text>
  <text class="blk" x="565" y="168" text-anchor="middle">LiDAR 里程计</text>

  <rect x="465" y="215" width="200" height="48" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.3"/>
  <text class="blk" x="565" y="244" text-anchor="middle">曲面片地图</text>

  <!-- ========== Refinement ========== -->
  <rect x="730" y="55" width="420" height="420" rx="14" fill="none" stroke="#9ca3af" stroke-width="1.5"/>
  <text class="stg" x="940" y="80" text-anchor="middle">精化</text>

  <rect x="820" y="105" width="240" height="48" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.3"/>
  <text class="blk" x="940" y="134" text-anchor="middle">关联点</text>

  <rect x="790" y="195" width="300" height="48" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.3"/>
  <text class="blk" x="940" y="224" text-anchor="middle">连续时间批优化</text>

  <!-- dashed parameter group -->
  <rect x="790" y="275" width="300" height="110" rx="8" fill="none" stroke="#b45309" stroke-width="1.5" stroke-dasharray="6 4"/>
  <rect x="810" y="290" width="260" height="36" rx="5" fill="#f59e0b" stroke="#b45309" stroke-width="1.2"/>
  <text class="blk" x="940" y="313" text-anchor="middle">B 样条控制点</text>
  <rect x="810" y="336" width="260" height="36" rx="5" fill="#f59e0b" stroke="#b45309" stroke-width="1.2"/>
  <text class="blk" x="940" y="351" text-anchor="middle">外参 <tspan class="math"><tspan baseline-shift="super" font-size="9">I</tspan><tspan baseline-shift="sub" font-size="9">L</tspan>q , <tspan baseline-shift="super" font-size="9">I</tspan>p<tspan baseline-shift="sub" font-size="9">L</tspan></tspan></text>

  <rect x="820" y="420" width="240" height="40" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.3"/>
  <text class="blk" x="940" y="445" text-anchor="middle">精化后的曲面片地图</text>

  <!-- ===== Arrows ===== -->
  <!-- IMU -> rotation curve -->
  <path d="M106,175 H150 V144 H175" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- IMU -> batch opt -->
  <path d="M70,139 V40 H940 V195" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- LiDAR -> lidar odom -->
  <path d="M106,390 H150" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- LiDAR -> refined surfels -->
  <path d="M70,426 V490 H940 V460" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- lidar odom -> initial extrinsic -->
  <path d="M225,365 V268" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- rotation curve -> initial extrinsic -->
  <path d="M275,168 V210" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- init -> data assoc (to motion-pred odom) -->
  <path d="M400,239 H440 V154 H465" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- motion-pred odom -> surfels map -->
  <path d="M565,183 V215" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- surfels map -> associated points (dashed) -->
  <path d="M665,239 H790 V129 H820" fill="none" stroke="#6b7280" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#arrd)"/>
  <!-- associated points -> batch opt -->
  <path d="M940,153 V195" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- batch opt -> control points -->
  <path d="M940,243 V290" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- params -> refined surfels -->
  <path d="M940,385 V420" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>
  <!-- refined surfels -> associated points (feedback left) -->
  <path d="M820,440 H760 V129 H820" fill="none" stroke="#4b5563" stroke-width="1.6" marker-end="url(#arr)"/>

  <text class="cap" x="40" y="32">LI-Calib 流程（对照论文 Fig. 2）</text>
</svg>
""".strip()



def frames_svg() -> str:
    return """
<svg xmlns="http://www.w3.org/2000/svg" width="980" height="420" viewBox="0 0 980 420">
  <rect width="980" height="420" fill="#fbfcfe"/>
  <style>
    text { font-family: 'Noto Sans CJK SC', 'Source Han Sans SC', 'PingFang SC', sans-serif; }
    .title { font-size: 15px; font-weight: 600; fill: #1f2937; }
    .label { font-size: 13px; fill: #334155; }
    .note { font-size: 12px; fill: #64748b; }
    .axis { stroke-width: 2.2; fill: none; marker-end: url(#ah); }
  </style>
  <defs>
    <marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#475569"/>
    </marker>
  </defs>
  <text x="40" y="36" class="title">坐标系与连续时间轨迹</text>

  <!-- I0 world-like -->
  <rect x="40" y="70" width="280" height="300" rx="10" fill="#eef4fb" stroke="#3b6ea5"/>
  <text x="180" y="100" text-anchor="middle" class="title">参考系 I₀</text>
  <line class="axis" x1="100" y1="280" x2="220" y2="280" stroke="#dc2626"/>
  <line class="axis" x1="100" y1="280" x2="100" y2="160" stroke="#16a34a"/>
  <text x="230" y="285" class="label">x</text>
  <text x="90" y="150" class="label">z</text>
  <path d="M120,250 C160,180 220,200 250,150" fill="none" stroke="#2563eb" stroke-width="3"/>
  <circle cx="160" cy="210" r="5" fill="#2563eb"/>
  <circle cx="220" cy="175" r="5" fill="#2563eb"/>
  <text x="180" y="330" text-anchor="middle" class="note">B 样条轨迹 p(t), q(t)</text>
  <text x="180" y="350" text-anchor="middle" class="note">任意时刻可求姿态与导数量</text>

  <!-- IMU / LiDAR rigid -->
  <rect x="360" y="70" width="280" height="300" rx="10" fill="#f3f7ef" stroke="#4f7a3e"/>
  <text x="500" y="100" text-anchor="middle" class="title">刚体外参</text>
  <rect x="410" y="150" width="80" height="55" rx="6" fill="#fff" stroke="#3b6ea5"/>
  <text x="450" y="182" text-anchor="middle" class="label">IMU</text>
  <rect x="510" y="220" width="80" height="55" rx="6" fill="#fff" stroke="#a16207"/>
  <text x="550" y="252" text-anchor="middle" class="label">LiDAR</text>
  <line x1="490" y1="178" x2="520" y2="230" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="500" y="320" text-anchor="middle" class="note">q_L^I , p_L^I</text>
  <text x="500" y="342" text-anchor="middle" class="note">标定目标：6-DoF 外参</text>

  <!-- Map L0 -->
  <rect x="680" y="70" width="260" height="300" rx="10" fill="#f8f1e8" stroke="#a16207"/>
  <text x="810" y="100" text-anchor="middle" class="title">地图系 L₀</text>
  <rect x="720" y="150" width="180" height="90" rx="6" fill="#fff" stroke="#a16207"/>
  <text x="810" y="185" text-anchor="middle" class="label">曲面片平面 π</text>
  <text x="810" y="210" text-anchor="middle" class="note">nᵀx + d = 0</text>
  <circle cx="760" cy="280" r="4" fill="#dc2626"/>
  <circle cx="800" cy="300" r="4" fill="#dc2626"/>
  <circle cx="840" cy="275" r="4" fill="#dc2626"/>
  <text x="810" y="340" text-anchor="middle" class="note">点变换到 L₀ 后</text>
  <text x="810" y="360" text-anchor="middle" class="note">构造点到面残差</text>
</svg>
""".strip()


def residual_svg() -> str:
    return """
<svg xmlns="http://www.w3.org/2000/svg" width="980" height="360" viewBox="0 0 980 360">
  <rect width="980" height="360" fill="#fbfcfe"/>
  <style>
    text { font-family: 'Noto Sans CJK SC', 'Source Han Sans SC', 'PingFang SC', sans-serif; }
    .title { font-size: 15px; font-weight: 600; fill: #1f2937; }
    .label { font-size: 13px; fill: #334155; }
    .note { font-size: 12px; fill: #64748b; }
    .box { fill: #eef4fb; stroke: #3b6ea5; stroke-width: 1.4; }
  </style>
  <text x="40" y="36" class="title">批优化中的三类残差如何共同约束状态</text>

  <rect class="box" x="40" y="80" width="220" height="120" rx="8"/>
  <text x="150" y="115" text-anchor="middle" class="title">陀螺残差</text>
  <text x="150" y="145" text-anchor="middle" class="note">ω_m − ω(t) − b_g</text>
  <text x="150" y="170" text-anchor="middle" class="note">约束旋转样条与零偏</text>

  <rect class="box" x="300" y="80" width="220" height="120" rx="8"/>
  <text x="410" y="115" text-anchor="middle" class="title">加速度残差</text>
  <text x="410" y="145" text-anchor="middle" class="note">a_m − a(t) − b_a</text>
  <text x="410" y="170" text-anchor="middle" class="note">约束平移样条、重力与零偏</text>

  <rect class="box" x="560" y="80" width="380" height="120" rx="8"/>
  <text x="750" y="115" text-anchor="middle" class="title">点到曲面片残差</text>
  <text x="750" y="145" text-anchor="middle" class="note">[p^{L₀}ᵀ , 1] π</text>
  <text x="750" y="170" text-anchor="middle" class="note">约束外参、整条轨迹与地图一致性</text>

  <rect x="160" y="250" width="660" height="70" rx="8" fill="#f3f7ef" stroke="#4f7a3e"/>
  <text x="490" y="280" text-anchor="middle" class="title">联合最小二乘</text>
  <text x="490" y="302" text-anchor="middle" class="note">状态含外参、样条控制点、加速度/陀螺零偏；LM 迭代求解</text>
</svg>
""".strip()


if __name__ == "__main__":
    write("pipeline.svg", pipeline_svg())
    write("frames-and-trajectory.svg", frames_svg())
    write("residuals.svg", residual_svg())
