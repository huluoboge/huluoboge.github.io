from pathlib import Path
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
output = root / 'figures' / 'anchor-snapshot.png'
font_path = subprocess.check_output(
    ['fc-match', '-f', '%{file}', 'Noto Sans CJK SC'], text=True
).strip()
scale = 2
image = Image.new('RGB', (1200 * scale, 470 * scale), '#ffffff')
draw = ImageDraw.Draw(image)


def xy(point):
    return tuple(round(value * scale) for value in point)


def font(size):
    return ImageFont.truetype(font_path, size * scale)


def centered(label, x, y, size, color='#1f2937'):
    draw.text(xy((x, y)), label, font=font(size), fill=color, anchor='mm')


def box(x, y, fill, outline, title, subtitle):
    draw.rounded_rectangle(xy((x, y, x + 195, y + 100)), radius=15 * scale,
                           fill=fill, outline=outline, width=2 * scale)
    centered(title, x + 97.5, y + 38, 24)
    centered(subtitle, x + 97.5, y + 73, 17, '#475569')


def arrow(points, color, width=4):
    points = [xy(point) for point in points]
    draw.line(points, fill=color, width=width * scale, joint='curve')
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    head = 13 * scale
    spread = 0.55
    corners = [
        (x2, y2),
        (x2 - head * math.cos(angle - spread), y2 - head * math.sin(angle - spread)),
        (x2 - head * math.cos(angle + spread), y2 - head * math.sin(angle + spread)),
    ]
    draw.polygon(corners, fill=color)


def bezier(start, control1, control2, end, steps=50):
    result = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        result.append((
            u**3 * start[0] + 3*u*u*t*control1[0] + 3*u*t*t*control2[0] + t**3*end[0],
            u**3 * start[1] + 3*u*u*t*control1[1] + 3*u*t*t*control2[1] + t**3*end[1],
        ))
    return result


centered('查询时刻 t = 2：箭头表示信息流向', 600, 45, 24)
box(50, 100, '#e0f2fe', '#0284c7', '锚点 R0', '已编码的 rig token')
box(350, 100, '#e2e8f0', '#64748b', '历史 R1', '已更新并缓存 KV')
box(650, 100, '#dcfce7', '#16a34a', '当前 R2', '本次查询 token')
box(960, 100, '#ede9fe', '#7c3aed', '位姿头', '输出 T0←2')
box(650, 290, '#fef3c7', '#d97706', '快照 A2', 'R0 的逐查询副本')

arrow(bezier((190, 201), (290, 315), (465, 337), (645, 337)), '#d97706')
centered('复制锚点 token', 379, 288, 17, '#92400e')
arrow([(548, 150), (644, 150)], '#64748b')
centered('缓存历史', 596, 125, 17, '#475569')
arrow([(718, 204), (718, 283)], '#16a34a')
centered('快照读取当前', 610, 249, 17, '#166534')
arrow([(784, 285), (784, 206)], '#d97706')
centered('当前读取快照', 882, 250, 17, '#92400e')
arrow([(850, 150), (954, 150)], '#7c3aed')
centered('读出位姿', 902, 125, 17, '#6d28d9')
centered('原始 R0 与已缓存 R1 不接收未来 R2；快照 A2 只为本次查询创建。', 600, 438, 17, '#475569')

image.save(output)
print(output)
