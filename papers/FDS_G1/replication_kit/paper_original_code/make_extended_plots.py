#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, json, os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from run_extended_mcmc import EXT_PARAM_NAMES, EXT_BOUNDS, EXT_STARTS, map_to_g1de2, derived_quantities
from stage2d_exact_likelihood import load_config, make_likelihood_from_config


def corner_plot(model: str, chains: list[np.ndarray], names: list[str], outdir: Path):
    try:
        import corner
        all_chain = np.vstack(chains)
        fig = corner.corner(all_chain, labels=names, show_titles=True,
                            quantiles=[0.16, 0.5, 0.84],
                            title_fmt=".4f")
        fig.savefig(outdir / "figures" / f"{model}_corner.png", dpi=180, bbox_inches="tight")
        plt.close(fig)
        print(f"  corner -> figures/{model}_corner.png")
    except Exception as e:
        (outdir / "figures" / f"{model}_corner_warning.txt").write_text(str(e))
        print(f"  corner skipped: {e}")


def trace_plot(model: str, paths: list[str], chains: list[np.ndarray], names: list[str], outdir: Path):
    ndim = len(names)
    ncols = min(ndim, 3)
    nrows = int(np.ceil(ndim / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 3 * nrows), squeeze=False)
    colors = plt.cm.tab10(np.linspace(0, 1, len(chains)))
    for j in range(ndim):
        ax = axes[j // ncols][j % ncols]
        for i, (path, ch) in enumerate(zip(paths, chains)):
            seed = Path(path).name.split("_seed")[-1].split("_")[0]
            ax.plot(ch[:, j], alpha=0.15, color=colors[i], lw=0.3, label=f"seed {seed}")
        ax.set_ylabel(names[j])
        ax.set_xlabel("post-burn step")
    for ax in axes.flat[ndim:]:
        ax.set_visible(False)
    fig.suptitle(f"{model} trace diagnostics", fontsize=13)
    fig.tight_layout()
    fig.savefig(outdir / "figures" / f"{model}_traces.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  traces -> figures/{model}_traces.png")


def locked_scatter(model: str, chains: list[np.ndarray], names: list[str], outdir: Path):
    if "s" not in names:
        return
    all_chain = np.vstack(chains)
    si = names.index("s")
    # Compute Sigma0 from the model
    drow = [derived_quantities(model, th) for th in all_chain]
    Sigma0 = np.array([d.get("Sigma0", np.nan) for d in drow])
    s_vals = all_chain[:, si]
    ok = np.isfinite(Sigma0) & np.isfinite(s_vals)
    s_vals = s_vals[ok]
    Sigma0 = Sigma0[ok]

    fig, ax = plt.subplots(figsize=(6, 5))
    # Hexbin
    hb = ax.hexbin(s_vals, Sigma0, gridsize=40, cmap="Blues", mincnt=1)
    plt.colorbar(hb, ax=ax, label="samples")

    # kappa = 3/4 line
    s_grid = np.linspace(2.3, 2.9, 100)
    ax.plot(s_grid, -0.75 * (3 - s_grid), "r--", lw=2, label=r"$\Sigma_0 = -3/4\,(3-s)$")
    ax.plot(s_grid, -(3 - s_grid), "k:", lw=1, label=r"$\kappa=1$")

    # Pilot reference
    med_s = np.median(s_vals)
    med_S = np.median(Sigma0)
    ax.plot(med_s, med_S, "r*", ms=12, label=f"median (s={med_s:.3f}, Σ₀={med_S:.3f})")

    ax.set_xlabel("s")
    ax.set_ylabel("Σ₀")
    ax.set_title(f"{model}: projection-locking check")
    ax.legend(fontsize=9)
    ax.axhline(0, color="gray", ls=":", alpha=0.5)
    ax.axvline(3, color="gray", ls=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(outdir / "figures" / f"{model}_s_Sigma0_locked.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  locked scatter -> figures/{model}_s_Sigma0_locked.png")


def response_plot(model: str, best: np.ndarray, config_path: str, outdir: Path):
    config = load_config(config_path)
    like = make_likelihood_from_config(config)
    base = map_to_g1de2(model, best)
    sol = like.growth_solution("g1de2", base)
    if sol is None:
        print("  response plot skipped (no growth solution)")
        return
    a_grid, D, f = sol
    z_grid = 1.0 / a_grid - 1.0

    pars = {"Omega_m": float(base[0]), "s": float(base[1]), "q_BAO": float(base[2]),
            "sigma8_0": float(base[3]), "mu0": float(base[4]), "Sigma0": float(base[5])}
    X = like.Xhat_a(a_grid, pars["Omega_m"], pars["s"])
    mu = 1.0 + pars["mu0"] * X
    Sigma = 1.0 + pars["Sigma0"] * X

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(z_grid[z_grid < 3], mu[z_grid < 3], "C0", lw=2)
    ax1.axhline(1, color="gray", ls="--")
    ax1.set_xlabel("z")
    ax1.set_ylabel(r"$\mu(z)$")
    ax1.set_title(f"Growth response (μ₀={pars['mu0']:.3f})")
    ax1.set_xlim(0, 2.5)

    ax2.plot(z_grid[z_grid < 3], Sigma[z_grid < 3], "C2", lw=2)
    ax2.axhline(1, color="gray", ls="--")
    ax2.set_xlabel("z")
    ax2.set_ylabel(r"$\Sigma(z)$")
    ax2.set_title(f"Weyl response (Σ₀={pars['Sigma0']:.3f})")
    ax2.set_xlim(0, 2.5)

    fig.suptitle(f"{model} response functions (posterior median)", fontsize=12)
    fig.tight_layout()
    fig.savefig(outdir / "figures" / f"{model}_response.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  response -> figures/{model}_response.png")


def model_comparison_chart(outdir: Path):
    rows = []
    for path in glob.glob(str(Path(outdir) / "tables" / "*_seed*_summary.json")):
        with open(path) as f:
            s = json.load(f)
        model = s.get("model", "")
        if not model:
            continue
        k = len(s.get("parameter_names", []))
        chi2 = float(s.get("chi2_total", np.nan))
        if not np.isfinite(chi2):
            continue
        rows.append({"model": model, "seed": s["seed"], "k": k, "chi2": chi2,
                     "acceptance": s.get("acceptance_fraction_mean", np.nan)})

    if not rows:
        print("  comparison chart: no summary files found")
        return

    df = pd.DataFrame(rows)
    best = df.sort_values("chi2").groupby("model", as_index=False).first()
    best["AIC"] = best["chi2"] + 2 * best["k"]
    best = best.sort_values("AIC")
    best["Delta_AIC"] = best["AIC"] - best["AIC"].min()
    best["Delta_chi2"] = best["chi2"] - best["chi2"].min()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    colors = plt.cm.Set2(np.linspace(0, 1, len(best)))
    chi2_min = best["chi2"].min()
    bars = ax1.bar(range(len(best)), best["Delta_chi2"], color=colors, edgecolor="gray", linewidth=0.5)
    ax1.set_xticks(range(len(best)))
    ax1.set_xticklabels(best["model"], rotation=30, ha="right", fontsize=8)
    ax1.set_ylabel(r"$\Delta\chi^2$  (base = " + f"{chi2_min:.1f}" + ")")
    ax1.set_title(r"$\Delta\chi^2$ by model (best seed)")
    for i, (dchi, k) in enumerate(zip(best["Delta_chi2"], best["k"])):
        ax1.text(i, dchi + 0.01, f"k={k}", ha="center", fontsize=8, color="gray")

    bars2 = ax2.bar(range(len(best)), best["Delta_AIC"], color=colors, edgecolor="gray", linewidth=0.5)
    ax2.set_xticks(range(len(best)))
    ax2.set_xticklabels(best["model"], rotation=30, ha="right", fontsize=8)
    ax2.set_ylabel(r"$\Delta$AIC")
    ax2.set_title(r"$\Delta$AIC (lower = better)")
    ax2.axhline(2, color="gray", ls="--", alpha=0.5)
    ax2.axhline(6, color="gray", ls=":", alpha=0.5)

    fig.suptitle("Extended model comparison (200-step smoke / 3-seed pilot)", fontsize=13)
    fig.tight_layout()
    fig.savefig(outdir / "figures" / "model_comparison_extended.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  comparison -> figures/model_comparison_extended.png")


def eg_fit_plot(model: str, best: np.ndarray, config_path: str, outdir: Path):
    config = load_config(config_path)
    like = make_likelihood_from_config(config)
    base = map_to_g1de2(model, best)
    pred = like.eg_pred("g1de2", base)
    if pred is None:
        print("  EG fit skipped (no prediction)")
        return
    z = like.z_eg
    val = like.val_eg
    err = np.sqrt(np.diag(like.Ceg))
    z_fine = np.linspace(z.min() - 0.05, z.max() + 0.2, 80)
    ae_fine = 1.0 / (1.0 + z_fine)
    pars = like.theta_to_pars("g1de2", base)
    sol = like.growth_solution("g1de2", base)
    if sol is None:
        print("  EG fit skipped (no growth)")
        return
    a_grid, D, f = sol
    f_fine = np.interp(ae_fine, a_grid, f)
    Sigma_fine = like.Sigma_response("g1de2", ae_fine, pars)
    curve = pars["Omega_m"] * Sigma_fine / f_fine

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.errorbar(z, val, yerr=err, fmt="ko", capsize=4, label=r"$E_G$ data")
    ax.plot(z_fine, curve, "C2-", lw=2, label=model)
    ax.set_xlabel("z")
    ax.set_ylabel(r"$E_G$")
    ax.set_title(f"{model}  $E_G$ fit (posterior median)")
    ax.legend()
    ax.set_xlim(-0.02, z.max() + 0.25)
    fig.tight_layout()
    fig.savefig(outdir / "figures" / f"{model}_EG_fit.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  EG fit -> figures/{model}_EG_fit.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage2d_exact_config.json")
    ap.add_argument("--model", choices=list(EXT_PARAM_NAMES))
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--chains-dir", default="outputs/chains")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    (outdir / "figures").mkdir(parents=True, exist_ok=True)

    if args.compare:
        model_comparison_chart(outdir)
        return

    if not args.model:
        ap.error("--model required unless --compare")

    model = args.model
    names = EXT_PARAM_NAMES[model]
    paths = sorted(glob.glob(os.path.join(args.chains_dir, f"{model}_seed*_chain_flat.npy")))
    if not paths:
        raise FileNotFoundError(f"No flat chains found for model={model}")

    chains = [np.load(p) for p in paths]
    all_chain = np.vstack(chains)

    q = np.quantile(all_chain, 0.5, axis=0)

    corner_plot(model, chains, names, outdir)
    trace_plot(model, paths, chains, names, outdir)
    locked_scatter(model, chains, names, outdir)

    if model in ("g1dew", "g1dem34", "g1demk", "g1dem1"):
        best_theta = map_to_g1de2(model, q)
        eg_fit_plot(model, q, args.config, outdir)
        response_plot(model, q, args.config, outdir)
    else:
        eg_fit_plot(model, q, args.config, outdir)
        response_plot(model, q, args.config, outdir)


if __name__ == "__main__":
    main()
