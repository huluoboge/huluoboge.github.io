# Creating a visualization of a 2D scalar field, its level sets, and the gradient field (quiver).
# The resulting image will be saved to /mnt/data/levelset_plot.png and displayed inline.
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Grid
nx, ny = 200, 200
x = np.linspace(-2.0, 2.0, nx)
y = np.linspace(-2.0, 2.0, ny)
X, Y = np.meshgrid(x, y)

# Scalar field: a smooth bump (radial)
F = np.exp(-(X**2 + Y**2))

# Compute gradients (partial derivatives)
dx = x[1] - x[0]
dy = y[1] - y[0]
Fy_x, Fy_y = np.gradient(F, dx, dy, edge_order=2)  # returns derivatives along axis 0 and 1
# Note: np.gradient returns (dF/dy, dF/dx) for a 2D array with axes (y, x).
dFdx = Fy_y
dFdy = Fy_x

# Prepare quiver sampling (sparser for clarity)
step = 12
Xq = X[::step, ::step]
Yq = Y[::step, ::step]
dFdx_q = dFdx[::step, ::step]
dFdy_q = dFdy[::step, ::step]

# Normalize gradient vectors for visualization (only direction matters)
mag = np.sqrt(dFdx_q**2 + dFdy_q**2)
nonzero = mag > 1e-12
dFdx_q[nonzero] /= mag[nonzero]
dFdy_q[nonzero] /= mag[nonzero]

# Plotting
fig, ax = plt.subplots(figsize=(7,7))
# Filled contour for scalar field
cf = ax.contourf(X, Y, F, levels=30, alpha=0.9)
# Contour lines (level sets)
cs = ax.contour(X, Y, F, levels=np.linspace(F.min(), F.max(), 8), linewidths=1)
# Highlight a specific level set, e.g., f = 0.5
lvl = 0.5
cs2 = ax.contour(X, Y, F, levels=[lvl], linewidths=2)
# Quiver for gradient (points outward for this radial bump)
q = ax.quiver(Xq, Yq, dFdx_q, dFdy_q, scale=20, pivot='mid')

ax.set_aspect('equal', 'box')
ax.set_title('Scalar field $f(x,y)=e^{-(x^2+y^2)}$ — level sets and gradient directions')
ax.set_xlabel('x')
ax.set_ylabel('y')

# Save figure
out_path = Path('./levelset_plot.png')
plt.tight_layout()
plt.savefig(out_path, dpi=150)
plt.show()


