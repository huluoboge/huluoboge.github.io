"""
RANSAC停止准则演示代码
基于论文"Fixing the RANSAC Stopping Criterion"的实现

这个脚本演示了传统近似停止准则与新的精确停止准则之间的差异
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
import platform
import matplotlib.font_manager as fm

# 设置中文字体支持
def setup_chinese_font():
    """设置 matplotlib 使用中文字体"""
    system = platform.system()
    
    # 根据操作系统选择字体
    if system == 'Windows':
        # Windows 系统常用中文字体
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
    elif system == 'Darwin':  # macOS
        # macOS 系统常用中文字体
        chinese_fonts = ['Arial Unicode MS', 'Heiti SC', 'Hiragino Sans GB', 'PingFang SC']
    else:  # Linux
        # Linux 系统常用中文字体
        chinese_fonts = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
    
    # 查找可用的中文字体
    available_fonts = []
    for font_name in chinese_fonts:
        try:
            font_path = fm.findfont(fm.FontProperties(family=font_name))
            if font_path and 'DejaVu' not in font_path:  # 排除回退字体
                available_fonts.append(font_name)
        except:
            continue
    
    # 设置字体
    if available_fonts:
        plt.rcParams['font.sans-serif'] = available_fonts + ['DejaVu Sans', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
        print(f"已设置中文字体: {available_fonts[0]}")
        return True
    else:
        print("警告: 未找到中文字体，将使用默认字体（可能无法显示中文）")
        print("建议安装中文字体包: sudo apt install fonts-wqy-microhei")
        return False

# 初始化字体设置
chinese_font_available = setup_chinese_font()

# 如果找不到中文字体，将图表标题改为英文
def get_chart_title(chinese_title, english_title):
    """根据字体可用性返回适当的标题"""
    return english_title if not chinese_font_available else chinese_title

def get_axis_label(chinese_label, english_label):
    """根据字体可用性返回适当的轴标签"""
    return english_label if not chinese_font_available else chinese_label

def approximate_all_inlier_probability(p: float, k: int) -> float:
    """
    传统的近似全内点采样概率计算
    Pₐ = pᵏ
    
    参数:
        p: 内点比例 (0 <= p <= 1)
        k: 最小样本大小
    
    返回:
        近似的全内点采样概率
    """
    return p ** k

def exact_all_inlier_probability(n: int, p: float, k: int) -> float:
    """
    精确的全内点采样概率计算
    Pₑ = ∏(pn-i)/(n-i) for i=0 to k-1
    
    参数:
        n: 总测量数
        p: 内点比例 (0 <= p <= 1)
        k: 最小样本大小
    
    返回:
        精确的全内点采样概率
    """
    pn = int(p * n)  # 内点总数
    
    # 如果内点数少于样本大小，概率为0
    if pn < k:
        return 0.0
    
    # 计算精确概率
    probability = 1.0
    for i in range(k):
        probability *= (pn - i) / (n - i)
    
    return probability

def compute_ransac_iterations(s: float, P: float) -> int:
    """
    计算RANSAC所需的迭代次数
    N ≥ log(1-s) / log(1-P)
    
    参数:
        s: 目标成功概率 (0 < s < 1)
        P: 全内点采样概率
    
    返回:
        所需的迭代次数
    """
    if P >= 1.0:
        return 1
    if P <= 0.0:
        return float('inf')  # 理论上需要无限次迭代
    
    return math.ceil(math.log(1 - s) / math.log(1 - P))

def compare_stopping_criteria(n: int, p: float, k: int, s: float = 0.99) -> Tuple[int, int, float]:
    """
    比较近似和精确停止准则
    
    参数:
        n: 总测量数
        p: 内点比例
        k: 最小样本大小
        s: 目标成功概率
    
    返回:
        (近似迭代次数, 精确迭代次数, 相对误差)
    """
    # 计算近似概率和迭代次数
    P_approx = approximate_all_inlier_probability(p, k)
    N_approx = compute_ransac_iterations(s, P_approx)
    
    # 计算精确概率和迭代次数
    P_exact = exact_all_inlier_probability(n, p, k)
    N_exact = compute_ransac_iterations(s, P_exact)
    
    # 计算相对误差
    relative_error = (P_approx - P_exact) / P_approx if P_approx > 0 else 0.0
    
    return N_approx, N_exact, relative_error

def demo_basic_comparison():
    """基础比较演示"""
    print("=" * 60)
    print("RANSAC停止准则比较演示")
    print("=" * 60)
    
    # 测试用例1：挑战性场景（少量测量，低内点比例）
    print("\n1. 挑战性场景 (n=50, p=0.2, k=5):")
    n1, p1, k1 = 50, 0.2, 5
    N_approx1, N_exact1, error1 = compare_stopping_criteria(n1, p1, k1)
    print(f"   近似方法: {N_approx1} 次迭代")
    print(f"   精确方法: {N_exact1} 次迭代")
    print(f"   相对误差: {error1:.2%}")
    print(f"   迭代次数增加: {(N_exact1 - N_approx1) / N_approx1:.1%}")
    
    # 测试用例2：中等场景
    print("\n2. 中等场景 (n=100, p=0.5, k=5):")
    n2, p2, k2 = 100, 0.5, 5
    N_approx2, N_exact2, error2 = compare_stopping_criteria(n2, p2, k2)
    print(f"   近似方法: {N_approx2} 次迭代")
    print(f"   精确方法: {N_exact2} 次迭代")
    print(f"   相对误差: {error2:.2%}")
    print(f"   迭代次数增加: {(N_exact2 - N_approx2) / N_approx2:.1%}")
    
    # 测试用例3：简单场景（大量测量，高内点比例）
    print("\n3. 简单场景 (n=500, p=0.8, k=5):")
    n3, p3, k3 = 500, 0.8, 5
    N_approx3, N_exact3, error3 = compare_stopping_criteria(n3, p3, k3)
    print(f"   近似方法: {N_approx3} 次迭代")
    print(f"   精确方法: {N_exact3} 次迭代")
    print(f"   相对误差: {error3:.2%}")
    print(f"   迭代次数增加: {(N_exact3 - N_approx3) / N_approx3:.1%}")

def plot_probability_comparison():
    """绘制概率比较图"""
    n_values = [20, 50, 100, 200, 500]
    p = 0.3
    k = 5
    
    approx_probs = []
    exact_probs = []
    
    for n in n_values:
        P_approx = approximate_all_inlier_probability(p, k)
        P_exact = exact_all_inlier_probability(n, p, k)
        approx_probs.append(P_approx)
        exact_probs.append(P_exact)
    
    plt.figure(figsize=(10, 6))
    plt.plot(n_values, approx_probs, 'r-', label='Approximate Pₐ = pᵏ', linewidth=2)
    plt.plot(n_values, exact_probs, 'b-', label='Exact Pₑ', linewidth=2)
    plt.xlabel(get_axis_label('总测量数 (n)', 'Total Measurements (n)'))
    plt.ylabel(get_axis_label('全内点采样概率', 'All-inlier Sampling Probability'))
    plt.title(get_chart_title(f'近似vs精确概率比较 (p={p}, k={k})', 
                             f'Approximate vs Exact Probability Comparison (p={p}, k={k})'))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('probability_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_iteration_comparison():
    """绘制迭代次数比较图"""
    p_values = np.linspace(0.1, 0.9, 9)
    n = 50
    k = 5
    s = 0.99
    
    approx_iters = []
    exact_iters = []
    
    for p in p_values:
        N_approx = compute_ransac_iterations(s, approximate_all_inlier_probability(p, k))
        N_exact = compute_ransac_iterations(s, exact_all_inlier_probability(n, p, k))
        approx_iters.append(N_approx)
        exact_iters.append(N_exact)
    
    plt.figure(figsize=(10, 6))
    plt.plot(p_values, approx_iters, 'r-', label='Approximate Method', linewidth=2)
    plt.plot(p_values, exact_iters, 'b-', label='Exact Method', linewidth=2)
    plt.xlabel(get_axis_label('内点比例 (p)', 'Inlier Ratio (p)'))
    plt.ylabel(get_axis_label('所需迭代次数', 'Required Iterations'))
    plt.title(get_chart_title(f'迭代次数比较 (n={n}, k={k}, s={s})', 
                             f'Iteration Comparison (n={n}, k={k}, s={s})'))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('iteration_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_error_impact():
    """分析误差影响"""
    print("\n" + "=" * 60)
    print("误差影响分析")
    print("=" * 60)
    
    # 分析不同参数组合下的误差
    n_values = [20, 50, 100, 200]
    p_values = [0.1, 0.3, 0.5, 0.7]
    k_values = [2, 5, 8]
    
    print("\n不同参数组合下的相对误差:")
    print("n\tp\tk\t近似P\t精确P\t相对误差")
    print("-" * 50)
    
    for n in n_values:
        for p in p_values:
            for k in k_values:
                P_approx = approximate_all_inlier_probability(p, k)
                P_exact = exact_all_inlier_probability(n, p, k)
                if P_approx > 0:
                    error = (P_approx - P_exact) / P_approx
                    print(f"{n}\t{p}\t{k}\t{P_approx:.4f}\t{P_exact:.4f}\t{error:.2%}")

def practical_ransac_simulation():
    """实际的RANSAC模拟"""
    print("\n" + "=" * 60)
    print("RANSAC模拟实验")
    print("=" * 60)
    
    # 模拟参数
    n_total = 100  # 总测量数
    true_inlier_ratio = 0.3  # 真实内点比例
    k = 5  # 最小样本大小
    s = 0.99  # 目标成功概率
    
    # 计算两种方法的迭代次数
    N_approx = compute_ransac_iterations(s, approximate_all_inlier_probability(true_inlier_ratio, k))
    N_exact = compute_ransac_iterations(s, exact_all_inlier_probability(n_total, true_inlier_ratio, k))
    
    print(f"模拟参数: n={n_total}, p={true_inlier_ratio}, k={k}, s={s}")
    print(f"近似方法迭代次数: {N_approx}")
    print(f"精确方法迭代次数: {N_exact}")
    print(f"迭代次数差异: {N_exact - N_approx} (+{(N_exact - N_approx)/N_approx:.1%})")
    
    # 模拟实际成功率
    num_simulations = 1000
    approx_success = 0
    exact_success = 0
    
    for _ in range(num_simulations):
        # 模拟近似方法的成功率
        success_prob_approx = 1 - (1 - exact_all_inlier_probability(n_total, true_inlier_ratio, k)) ** N_approx
        if np.random.random() < success_prob_approx:
            approx_success += 1
        
        # 模拟精确方法的成功率
        success_prob_exact = 1 - (1 - exact_all_inlier_probability(n_total, true_inlier_ratio, k)) ** N_exact
        if np.random.random() < success_prob_exact:
            exact_success += 1
    
    print(f"\n模拟结果 ({num_simulations} 次实验):")
    print(f"近似方法实际成功率: {approx_success/num_simulations:.1%}")
    print(f"精确方法实际成功率: {exact_success/num_simulations:.1%}")
    print(f"目标成功率: {s:.1%}")

if __name__ == "__main__":
    # 运行演示
    demo_basic_comparison()
    
    # 分析误差影响
    analyze_error_impact()
    
    # 运行模拟实验
    practical_ransac_simulation()
    
    print("\n" + "=" * 60)
    print("关键发现总结")
    print("=" * 60)
    print("1. 传统近似方法总是高估全内点采样概率")
    print("2. 在挑战性场景中（n小，p低，k大），近似误差显著")
    print("3. 精确方法确保达到目标成功概率，但可能增加运行时间")
    print("4. 在简单场景中，两种方法差异很小")
    print("5. 精确方法的实现非常简单，只需几行代码")
    
    # 注释掉绘图部分，避免在没有图形界面的环境中出错
    print("\n生成比较图表...")
    try:
        plot_probability_comparison()
        plot_iteration_comparison()
        print("图表已保存为 probability_comparison.png 和 iteration_comparison.png")
    except Exception as e:
        print(f"图表生成失败: {e}")
        print("请确保已安装 matplotlib 库")
