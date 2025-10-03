import matplotlib.pyplot as plt
import numpy as np

def plot_epipolar_error():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 假设图像坐标系大小
    img_w, img_h = 400, 300
    
    # 原始匹配点 (x, y)
    x = np.array([200, 150])
    x_prime = np.array([220, 120])

    # 假设的基础矩阵 F （简单模拟）
    F = np.array([[0, -0.001, 0.1],
                  [0.001, 0, -0.05],
                  [-0.1, 0.05, 1]])

    # 扩展为齐次坐标
    X = np.array([x[0], x[1], 1])
    Xp = np.array([x_prime[0], x_prime[1], 1])

    # 对极线 l' = F x
    l_prime = F @ X  
    # 对极线 l = F^T x'
    l = F.T @ Xp  

    def line_points(l, w=img_w):
        # l = (a, b, c)
        a, b, c = l
        if abs(b) > 1e-6:
            xs = np.array([0, w])
            ys = -(a*xs + c)/b
        else:
            xs = -c/a * np.ones(2)
            ys = np.array([0, img_h])
        return xs, ys

    # --------- 图1: 代数误差 ---------
    ax = axes[0]
    xs, ys = line_points(l_prime)
    ax.plot(xs, ys, 'r-', label="Epipolar line (l')")
    ax.plot(x_prime[0], x_prime[1], 'bo', label="Point x'")
    ax.set_xlim(0, img_w)
    ax.set_ylim(img_h, 0)
    ax.set_title("Algebraic Error\n(x'^T F x ≠ 0)")
    ax.legend()

    # --------- 图2: 几何误差 (点到对极线的距离) ---------
    ax = axes[1]
    xs, ys = line_points(l_prime)
    ax.plot(xs, ys, 'r-', label="Epipolar line (l')")
    ax.plot(x_prime[0], x_prime[1], 'bo', label="Point x'")

    # 点到直线的垂足
    a, b, c = l_prime
    d = (a*x_prime[0] + b*x_prime[1] + c)/(a**2+b**2)
    foot = np.array([x_prime[0] - a*d, x_prime[1] - b*d])

    ax.plot([x_prime[0], foot[0]], [x_prime[1], foot[1]], 'g--', label="Geometric error")
    ax.plot(foot[0], foot[1], 'go')
    ax.set_xlim(0, img_w)
    ax.set_ylim(img_h, 0)
    ax.set_title("Geometric Error\n(distance to epipolar line)")
    ax.legend()

    # --------- 图3: Sampson误差近似 ---------
    ax = axes[2]
    xs, ys = line_points(l_prime)
    ax.plot(xs, ys, 'r-', label="Epipolar line (l')")
    ax.plot(x_prime[0], x_prime[1], 'bo', label="Point x'")

    # 画出几何误差和说明
    ax.plot([x_prime[0], foot[0]], [x_prime[1], foot[1]], 'g--')
    ax.plot(foot[0], foot[1], 'go')

    ax.text(50, 50, "Sampson error ≈\n(algebraic error)^2 / gradient norm", fontsize=10, bbox=dict(facecolor="white", alpha=0.6))

    ax.set_xlim(0, img_w)
    ax.set_ylim(img_h, 0)
    ax.set_title("Sampson Error\n(second-order approx.)")
    ax.legend()

    plt.tight_layout()
    return fig

fig = plot_epipolar_error()
plt.show()
