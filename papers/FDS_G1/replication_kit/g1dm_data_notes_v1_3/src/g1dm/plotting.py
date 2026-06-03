"""Plotting helpers for G1DM data-note prototypes."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def savefig(path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_gaussian_1d(mean, sigma, out, xlabel, markers=None, title=None):
    x = np.linspace(mean - 5*sigma, mean + 5*sigma, 500)
    y = np.exp(-0.5*((x-mean)/sigma)**2)/(sigma*np.sqrt(2*np.pi))
    plt.figure(figsize=(6,4))
    plt.plot(x, y)
    if markers:
        for val, label in markers:
            plt.axvline(val, linestyle="--", linewidth=1)
            plt.text(val, y.max()*0.9, label, rotation=90, va="top", ha="right")
    plt.xlabel(xlabel)
    plt.ylabel("Gaussian density")
    if title:
        plt.title(title)
    savefig(out)
