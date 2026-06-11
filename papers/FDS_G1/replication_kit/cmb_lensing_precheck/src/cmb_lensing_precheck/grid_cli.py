from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from .config import load_config
from .pipeline import run_precheck


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan (s,kappa) for the FDS-G1 CMB-lensing precheck.")
    parser.add_argument("config")
    args = parser.parse_args()
    cfg0 = load_config(args.config)
    grid = cfg0.get("grid")
    if not grid:
        raise ValueError("Grid configuration is missing.")
    root = Path(cfg0["run"]["output_dir"])
    root.mkdir(parents=True, exist_ok=True)
    s_values = np.linspace(float(grid["s_min"]), float(grid["s_max"]), int(grid["n_s"]))
    k_values = np.linspace(float(grid["kappa_min"]), float(grid["kappa_max"]), int(grid["n_kappa"]))
    mean_ratio = np.empty((s_values.size, k_values.size))
    delta_chi2 = np.full_like(mean_ratio, np.nan)
    lo, hi = int(grid["summary_ell_min"]), int(grid["summary_ell_max"])

    rows = []
    for i, s in enumerate(s_values):
        for j, kappa in enumerate(k_values):
            cfg = deepcopy(cfg0)
            cfg["model"]["name"] = "g1de_mkappa"
            cfg["model"]["s"] = float(s)
            cfg["model"]["kappa"] = float(kappa)
            cfg["run"]["name"] = f"s{s:.5f}_k{kappa:.5f}"
            summary, result = run_precheck(cfg, write_artifacts=False, return_result=True)
            mask = (result.ell >= lo) & (result.ell <= hi)
            mr = float(np.mean(result.ratio[mask]))
            mean_ratio[i, j] = mr
            dchi = np.nan
            if summary["likelihood"] is not None:
                dchi = float(summary["likelihood"]["delta_chi2"])
                delta_chi2[i, j] = dchi
            rows.append((s, kappa, mr, dchi))

    np.savetxt(root / "grid_summary.csv", np.asarray(rows), delimiter=",", header="s,kappa,mean_clpp_ratio,delta_chi2", comments="")
    with (root / "grid_metadata.json").open("w", encoding="utf-8") as f:
        json.dump({"s_values": s_values.tolist(), "kappa_values": k_values.tolist(), "ell_range": [lo, hi]}, f, indent=2)

    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    mesh = ax.pcolormesh(k_values, s_values, mean_ratio, shading="auto")
    fig.colorbar(mesh, ax=ax, label=rf"mean $C_L^{{\phi\phi}}$ ratio, $L={lo}$–${hi}$")
    ax.scatter([0.75], [2.555], marker="x", s=70, label=r"reference $M_{3/4}$")
    ax.set_xlabel(r"$\kappa$")
    ax.set_ylabel(r"$s$")
    ax.legend()
    fig.tight_layout()
    fig.savefig(root / "grid_mean_ratio.png", dpi=180)
    plt.close(fig)

    if np.any(np.isfinite(delta_chi2)):
        fig, ax = plt.subplots(figsize=(7.2, 5.2))
        mesh = ax.pcolormesh(k_values, s_values, delta_chi2, shading="auto")
        fig.colorbar(mesh, ax=ax, label=r"$\Delta\chi^2$ relative to LCDM")
        ax.set_xlabel(r"$\kappa$")
        ax.set_ylabel(r"$s$")
        fig.tight_layout()
        fig.savefig(root / "grid_delta_chi2.png", dpi=180)
        plt.close(fig)


if __name__ == "__main__":
    main()
