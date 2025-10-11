import matplotlib
from matplotlib import font_manager
import platform

def list_chinese_fonts():
    """枚举出系统中支持中文的字体"""
    chinese_fonts = []
    for f in font_manager.fontManager.ttflist:
        # 尝试检测字体名中是否包含常见中文关键字
        if any(k in f.name for k in ['Sim', 'Hei', 'Song', 'Kai', 'Fang', 'PingFang', 'YaHei', 'CJK', 'WenQuanYi', 'Noto', 'Li']):
            chinese_fonts.append(f.name)
            continue
        # 或者检测字体能否渲染中文（更准确但稍慢）
        try:
            if f.prop.get_name() and f.prop.get_family():
                font = font_manager.FontProperties(fname=f.fname)
                if font.get_name():
                    # 用字体绘制一个中文字符测试
                    import PIL.Image, PIL.ImageDraw, PIL.ImageFont
                    try:
                        pil_font = PIL.ImageFont.truetype(f.fname, 16)
                        w, h = pil_font.getsize("中")
                        if w > 0:
                            chinese_fonts.append(f.name)
                    except Exception:
                        pass
        except Exception:
            pass

    chinese_fonts = sorted(set(chinese_fonts))
    print("系统中支持中文的字体有：")
    for name in chinese_fonts:
        print(" -", name)

    print("\nMatplotlib 默认字体：", matplotlib.rcParams['font.sans-serif'])
    return chinese_fonts


def setup_chinese_font(permanent=False):
    """智能自动配置 Matplotlib 中文字体（跨 Windows / macOS / Linux）"""
    system = platform.system()

    # 不同系统常见中文字体优先级表
    preferred_fonts = {
        "Windows": ["Microsoft YaHei", "SimHei"],
        "Darwin": ["PingFang SC", "Heiti TC", "Songti SC"],
        "Linux": ["Noto Sans CJK SC", "WenQuanYi Micro Hei", "AR PL UMing CN"]
    }

    # 1️⃣ 获取系统可用字体列表
    available_fonts = [f.name for f in font_manager.fontManager.ttflist]
    
    # 2️⃣ 选择系统内可用的中文字体
    candidates = preferred_fonts.get(system, [])  # 当前系统的优先表
    selected_font = None
    for font_name in candidates:
        if font_name in available_fonts:
            selected_font = font_name
            break

    if not selected_font:
        chinese_fonts = list_chinese_fonts()
        if not chinese_fonts:
            print("⚠️ 未检测到中文字体，请自行安装字体")
        else:
            selected_font = chinese_fonts[0]
    # 4️⃣ 最后，如果还没找到，就用默认字体
    if not selected_font:
        chinese_fonts = list_chinese_fonts()
        selected_font = matplotlib.rcParams['font.sans-serif'][0]
        print("⚠️ 未检测到中文字体，使用默认字体：", selected_font)
    else:
        print("✅ 使用中文字体：", selected_font)

    # 5️⃣ 应用到 Matplotlib
    matplotlib.rcParams['font.sans-serif'] = [selected_font]
    matplotlib.rcParams['axes.unicode_minus'] = False  # 让负号正常显示

    # 6️⃣ 可选：写入配置文件（永久生效）
    if permanent:
        rcfile = matplotlib.matplotlib_fname()
        with open(rcfile, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(rcfile, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.startswith('font.sans-serif'):
                    f.write(f"font.sans-serif : {selected_font}\n")
                elif line.startswith('axes.unicode_minus'):
                    f.write("axes.unicode_minus : False\n")
                else:
                    f.write(line)
        print(f"🧩 已写入到 Matplotlib 配置文件：{rcfile}")

# 示例使用
if __name__ == "__main__":
    setup_chinese_font(permanent=False)

    import matplotlib.pyplot as plt
    plt.title("中文测试：你好，Matplotlib！")
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.show()
