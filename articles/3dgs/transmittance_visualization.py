import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
import matplotlib.font_manager as fm
from matplotlib import rcParams

# 设置中文字体 - 直接使用字体文件路径
try:
    # 使用Noto Sans CJK字体文件
    font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    font_prop = fm.FontProperties(fname=font_path)
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = [font_prop.get_name()]
    rcParams['axes.unicode_minus'] = False
    print(f"中文字体设置成功：使用 {font_path}")
except Exception as e:
    print(f"中文字体设置失败: {e}，尝试备用方案")
    try:
        rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
        rcParams['axes.unicode_minus'] = False
        print("使用备用英文字体")
    except:
        print("使用默认字体")

# 设置绘图风格
plt.style.use('seaborn-v0_8-whitegrid')

def plot_transmittance_analysis():
    """绘制透射率积分的完整分析"""
    
    # 创建距离参数 s（从0到10）
    s = np.linspace(0, 10, 1000)
    
    # 创建图形
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    fig.suptitle('透射率积分 T(t) = exp(-∫₀ᵗ σ(s) ds) 的可视化分析', fontsize=16, fontweight='bold')
    
    # 案例1: 均匀密度（常数σ）
    sigma1 = 0.5 * np.ones_like(s)  # 常数密度 σ = 0.5
    integral1 = cumtrapz(sigma1, s, initial=0)
    transmittance1 = np.exp(-integral1)
    
    # 案例2: 高斯分布密度
    center = 5.0
    width = 1.5
    sigma2 = 1.0 * np.exp(-(s - center)**2 / (2 * width**2))
    integral2 = cumtrapz(sigma2, s, initial=0)
    transmittance2 = np.exp(-integral2)
    
    # 案例3: 阶跃函数密度（模拟物体表面）
    threshold = 6.0
    sigma3 = np.where(s < threshold, 0.1, 1.5)  # 在s=6处密度突变
    integral3 = cumtrapz(sigma3, s, initial=0)
    transmittance3 = np.exp(-integral3)
    
    # 绘制案例1
    axes[0, 0].plot(s, sigma1, 'b-', linewidth=2, label='σ(s)')
    axes[0, 0].set_title('案例1: 均匀密度\n原函数 σ(s) = 常数')
    axes[0, 0].set_ylabel('密度 σ(s)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].plot(s, integral1, 'r-', linewidth=2, label='∫σ(s)ds')
    axes[0, 1].set_title('积分函数 ∫₀ᵗ σ(s) ds')
    axes[0, 1].set_ylabel('累积光学深度')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[0, 2].plot(s, transmittance1, 'g-', linewidth=2, label='T(t)')
    axes[0, 2].set_title('透射率 T(t) = exp(-∫σ(s)ds)')
    axes[0, 2].set_ylabel('透射概率')
    axes[0, 2].set_ylim(0, 1.1)
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # 绘制案例2
    axes[1, 0].plot(s, sigma2, 'b-', linewidth=2, label='σ(s)')
    axes[1, 0].set_title('案例2: 高斯分布密度\n原函数 σ(s) = 高斯函数')
    axes[1, 0].set_ylabel('密度 σ(s)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].plot(s, integral2, 'r-', linewidth=2, label='∫σ(s)ds')
    axes[1, 1].set_title('积分函数 ∫₀ᵗ σ(s) ds')
    axes[1, 1].set_ylabel('累积光学深度')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    axes[1, 2].plot(s, transmittance2, 'g-', linewidth=2, label='T(t)')
    axes[1, 2].set_title('透射率 T(t) = exp(-∫σ(s)ds)')
    axes[1, 2].set_ylabel('透射概率')
    axes[1, 2].set_ylim(0, 1.1)
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)
    
    # 绘制案例3
    axes[2, 0].plot(s, sigma3, 'b-', linewidth=2, label='σ(s)')
    axes[2, 0].set_title('案例3: 阶跃函数密度\n原函数 σ(s) = 阶跃函数')
    axes[2, 0].set_xlabel('距离 s')
    axes[2, 0].set_ylabel('密度 σ(s)')
    axes[2, 0].legend()
    axes[2, 0].grid(True, alpha=0.3)
    
    axes[2, 1].plot(s, integral3, 'r-', linewidth=2, label='∫σ(s)ds')
    axes[2, 1].set_title('积分函数 ∫₀ᵗ σ(s) ds')
    axes[2, 1].set_xlabel('距离 t')
    axes[2, 1].set_ylabel('累积光学深度')
    axes[2, 1].legend()
    axes[2, 1].grid(True, alpha=0.3)
    
    axes[2, 2].plot(s, transmittance3, 'g-', linewidth=2, label='T(t)')
    axes[2, 2].set_title('透射率 T(t) = exp(-∫σ(s)ds)')
    axes[2, 2].set_xlabel('距离 t')
    axes[2, 2].set_ylabel('透射概率')
    axes[2, 2].set_ylim(0, 1.1)
    axes[2, 2].legend()
    axes[2, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('transmittance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return {
        's': s,
        'case1': {'sigma': sigma1, 'integral': integral1, 'transmittance': transmittance1},
        'case2': {'sigma': sigma2, 'integral': integral2, 'transmittance': transmittance2},
        'case3': {'sigma': sigma3, 'integral': integral3, 'transmittance': transmittance3}
    }

def plot_comparison():
    """绘制三种情况的透射率对比"""
    data = plot_transmittance_analysis()
    
    plt.figure(figsize=(10, 6))
    plt.plot(data['s'], data['case1']['transmittance'], 'b-', linewidth=2, label='均匀密度')
    plt.plot(data['s'], data['case2']['transmittance'], 'r-', linewidth=2, label='高斯密度')
    plt.plot(data['s'], data['case3']['transmittance'], 'g-', linewidth=2, label='阶跃密度')
    
    plt.title('三种密度分布的透射率对比', fontsize=14, fontweight='bold')
    plt.xlabel('距离 t', fontsize=12)
    plt.ylabel('透射率 T(t)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.1)
    
    plt.savefig('transmittance_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("开始生成透射率积分的可视化分析...")
    data = plot_transmittance_analysis()
    plot_comparison()
    print("可视化完成！图像已保存为 transmittance_analysis.png 和 transmittance_comparison.png")
