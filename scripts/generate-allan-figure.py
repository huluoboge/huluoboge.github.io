#!/usr/bin/env python3
"""Generate a finite-sample Allan deviation figure for the IMU article."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "blog/articles/imu-noise-allan-variance/allan-deviation.png"


def allan_deviation(data, sample_rate, taus):
    """Compute non-overlapping Allan deviation for a scalar sequence."""
    data = np.asarray(data, dtype=float)
    result_taus = []
    result_adev = []
    for tau in taus:
        cluster_size = max(1, int(round(tau * sample_rate)))
        cluster_count = len(data) // cluster_size
        if cluster_count < 3:
            continue
        clusters = data[: cluster_count * cluster_size].reshape(
            cluster_count, cluster_size
        )
        means = clusters.mean(axis=1)
        result_taus.append(cluster_size / sample_rate)
        result_adev.append(np.sqrt(0.5 * np.mean(np.diff(means) ** 2)))
    return np.asarray(result_taus), np.asarray(result_adev)


def simulate_channel(rng, sample_rate, duration, noise_density, bias_std, bias_tau, rw):
    """Create a stationary sensor channel with finite-sample imperfections."""
    count = int(sample_rate * duration)
    dt = 1.0 / sample_rate

    white = rng.normal(0.0, noise_density / np.sqrt(dt), count)
    bias = np.zeros(count)
    # A slowly varying OU component gives a finite bias-stability region.
    alpha = np.exp(-dt / bias_tau)
    ou_noise = bias_std * np.sqrt(1.0 - alpha * alpha)
    # A random-walk component produces the long-time +1/2 branch.
    rw_steps = rng.normal(0.0, rw * np.sqrt(dt), count)
    for index in range(1, count):
        bias[index] = alpha * bias[index - 1] + ou_noise * rng.normal()
    bias += np.cumsum(rw_steps)
    return white + bias


def add_reference_slopes(ax, tau, adev, noise_density, label):
    """Add local slope guides without implying they are fitted measurements."""
    left = tau[len(tau) // 7]
    right = tau[-len(tau) // 5]
    left_y = noise_density / np.sqrt(left) * 1.05
    right_y = adev[-len(adev) // 5] * 0.7
    ax.loglog(
        [left, left * 8],
        [left_y, left_y / np.sqrt(8)],
        "--",
        color="#315f9b",
        linewidth=1.2,
    )
    ax.text(left * 1.4, left_y * 0.8, "-1/2", color="#315f9b", fontsize=9)
    ax.loglog(
        [right / 4, right],
        [right_y / 2, right_y],
        "--",
        color="#b4574d",
        linewidth=1.2,
    )
    ax.text(right / 2.2, right_y * 0.78, "+1/2", color="#b4574d", fontsize=9)
    ax.text(
        0.03,
        0.04,
        label,
        transform=ax.transAxes,
        fontsize=9,
        color="#555555",
    )


def main():
    rng = np.random.default_rng(20260914)
    sample_rate = 200.0
    duration = 4096.0
    taus = np.logspace(np.log10(1.0 / sample_rate), np.log10(1000.0), 70)

    gyro = simulate_channel(
        rng,
        sample_rate,
        duration,
        noise_density=0.008,
        bias_std=0.0008,
        bias_tau=35.0,
        rw=0.00022,
    )
    accel = simulate_channel(
        rng,
        sample_rate,
        duration,
        noise_density=0.08,
        bias_std=0.008,
        bias_tau=35.0,
        rw=0.0018,
    )
    gyro_tau, gyro_adev = allan_deviation(gyro, sample_rate, taus)
    accel_tau, accel_adev = allan_deviation(accel, sample_rate, taus)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#777777",
            "axes.labelcolor": "#222222",
            "xtick.color": "#444444",
            "ytick.color": "#444444",
            "font.size": 10,
        }
    )
    figure, axes = plt.subplots(1, 2, figsize=(14, 5.6), constrained_layout=True)
    figure.patch.set_facecolor("white")

    panels = [
        (axes[0], gyro_tau, gyro_adev, 0.008, "Gyroscope", "rad/s"),
        (axes[1], accel_tau, accel_adev, 0.08, "Accelerometer", "m/s²"),
    ]
    for ax, tau, adev, density, name, unit in panels:
        ax.loglog(
            tau,
            adev,
            color="#202b3c",
            marker="o",
            markersize=3.4,
            linewidth=1.1,
            alpha=0.9,
            label="finite-sample simulation",
        )
        ax.set_title(name, loc="left", fontweight="bold", pad=10)
        ax.set_xlabel("Cluster time $\\tau$ (s)")
        ax.set_ylabel(f"Allan deviation ({unit})")
        ax.grid(True, which="both", color="#d9dde3", linewidth=0.65, alpha=0.8)
        ax.set_xlim(0.004, 1000)
        ax.legend(loc="upper right", frameon=False, fontsize=8)
        add_reference_slopes(ax, tau, adev, density, "synthetic stationary data")

    figure.suptitle(
        "Allan deviation from finite-length stationary IMU simulations",
        fontsize=14,
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.01,
        "The two -1/2 branches are sensor-specific white-noise regions; their unit conversions give ARW and VRW.",
        ha="center",
        color="#555555",
        fontsize=9,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=180, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()
