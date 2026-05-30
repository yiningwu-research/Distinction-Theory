#!/usr/bin/env python3
"""Reproduce paper Figure 6: Δχ² bar chart for KiDS shear-only."""
import argparse, csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def load_confusion(path):
    with open(path) as f:
        d = json.load(f)
    return d.get("results", {})

def plot_delta_chi2(results, outpath):
    models = ["LCDM", "M3/4", "Mkappa", "const-Sigma", "binned-Sigma"]
    colors = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b2"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(models))
    ref = next((r for m, r in results.items() if "m34" in m.lower()), None)
    if ref is None:
        ref = results.get(list(results.keys())[0], {})
    chi2_ref = ref.get("chi2_min", 0)
    deltas = []
    labels = []
    for m in models:
        key = m.lower().replace("-", "_").replace(" ", "_")
        r = results.get(key, {})
        d = r.get("chi2_min", 0) - chi2_ref
        deltas.append(d)
        labels.append(m)
    bars = ax.bar(x, deltas, color=colors, width=0.6, edgecolor="black", linewidth=0.5)
    for bar, d in zip(bars, deltas):
        va = "bottom" if d >= 0 else "top"
        offset = 0.5 if d >= 0 else -0.5
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + offset * np.sign(d) if d != 0 else offset,
                f"{d:.1f}", ha="center", va=va, fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel(r"$\Delta\chi^2$ (relative to M$_{3/4}$)", fontsize=11)
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.set_title("KiDS-1000 shear-only: M$_{3/4}$ vs controls\n"
                 "(m$_i$+$\Delta$z$_i$+A$_{\\rm IA}$ profiled)", fontsize=11)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)
    print(f"Saved {outpath}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confusion", default="outputs/phase2b4_confusion_deterministic.json")
    ap.add_argument("--outdir", default="figures")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    results = load_confusion(args.confusion)
    plot_delta_chi2(results, outdir / "kids_delta_chi2.png")
    plot_delta_chi2(results, outdir / "kids_delta_chi2.pdf")

if __name__ == "__main__":
    main()
