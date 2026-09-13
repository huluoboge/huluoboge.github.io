#!/usr/bin/env python3
"""Generate a conceptual time-domain/PSD figure for the IMU noise article."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "blog/articles/imu-noise-allan-variance/psd-frequency-distribution.png"


def periodogram(signal, sample_rate):
    signal = signal - np.mean(signal)
    window = np.hanning(len(signal))
    spectrum = np.fft.rfft(signal * window)
    frequency = np.fft.rfftfreq(len(signal), 1.0 / sample_rate)
    power = np.abs(spectrum) ** 2
    power /= np.sum(window**2) * sample_rate
    return frequency[1:], power[1:]


def main():
    rng = np.random.default_rng(20260914)
    sample_rate = 200.0
    duration = 4.0
    time = np.arange(0.0, duration, 1.0 / sample_rate)

    low_signal = (
        0.95 * np.sin(2.0 * np.pi * 1.2 * time)
        + 0.18 * np.sin(2.0 * np.pi * 2.6 * time + 0.4)
        + 0.05 * rng.normal(size=len(time))
    )
    high_signal = (
        0.45 * np.sin(2.0 * np.pi * 34.0 * time)
        + 0.28 * np.sin(2.0 * np.pi * 62.0 * time + 0.7)
        + 0.16 * rng.normal(size=len(time))
    )
    low_frequency, low_power = periodogram(low_signal, sample_rate)
    high_frequency, high_power = periodogram(high_signal, sample_rate)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.edgecolor": "#8a919b",
            "axes.labelcolor": "#222222",
            "xtick.color": "#4d5560",
            "ytick.color": "#4d5560",
        }
    )
    figure, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    figure.patch.set_facecolor("white")

    axes[0, 0].plot(time, low_signal, color="#246b8f", linewidth=1.6)
    axes[0, 0].set_title("Slowly varying signal", loc="left", fontweight="bold")
    axes[0, 0].set_ylabel("Amplitude")
    axes[0, 0].set_xlim(0, duration)
    axes[0, 0].set_ylim(-1.35, 1.35)

    axes[0, 1].plot(low_frequency, low_power, color="#246b8f", linewidth=1.5)
    axes[0, 1].fill_between(low_frequency, low_power, color="#246b8f", alpha=0.14)
    axes[0, 1].set_title("PSD: energy concentrated at low frequency", loc="left", fontweight="bold")
    axes[0, 1].set_xlim(0, 100)
    axes[0, 1].set_ylim(bottom=0)

    axes[1, 0].plot(time, high_signal, color="#b45b48", linewidth=1.15)
    axes[1, 0].set_title("Rapidly varying signal", loc="left", fontweight="bold")
    axes[1, 0].set_xlabel("Time (s)")
    axes[1, 0].set_ylabel("Amplitude")
    axes[1, 0].set_xlim(0, duration)
    axes[1, 0].set_ylim(-1.05, 1.05)

    axes[1, 1].plot(high_frequency, high_power, color="#b45b48", linewidth=1.5)
    axes[1, 1].fill_between(high_frequency, high_power, color="#b45b48", alpha=0.14)
    axes[1, 1].set_title("PSD: energy shifted to higher frequency", loc="left", fontweight="bold")
    axes[1, 1].set_xlabel("Frequency (Hz)")
    axes[1, 1].set_xlim(0, 100)
    axes[1, 1].set_ylim(bottom=0)

    for axis in axes.flat:
        axis.grid(True, color="#dfe3e8", linewidth=0.65)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    figure.suptitle("The same signal can be viewed in time and frequency", fontsize=14, fontweight="bold")
    figure.text(
        0.5,
        0.005,
        "Conceptual illustration: PSD describes how signal power is distributed over frequency.",
        ha="center",
        color="#5c6470",
        fontsize=9,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=180, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()
