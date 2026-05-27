#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stage2d_exact_likelihood import PARAM_NAMES, load_config, make_likelihood_from_config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage2d_exact_config.json")
    ap.add_argument("--model", required=True, choices=list(PARAM_NAMES))
    ap.add_argument("--chains-dir", default="outputs/chains")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    (outdir / "figures").mkdir(parents=True, exist_ok=True)

    paths = sorted(glob.glob(os.path.join(args.chains_dir, f"{args.model}_seed*_chain_flat.npy")))
    if not paths:
        raise FileNotFoundError(f"No flat chains found for model={args.model}")

    chains = [np.load(p) for p in paths]
    all_chain = np.vstack(chains)
    names = PARAM_NAMES[args.model]

    try:
        import corner
        fig = corner.corner(all_chain, labels=names, show_titles=True, quantiles=[0.16, 0.5, 0.84])
        fig.savefig(outdir / "figures" / f"{args.model}_corner.png", dpi=180, bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        (outdir / "figures" / f"{args.model}_corner_warning.txt").write_text(str(e))

    # Pair plots for G1DE-2 key projections.
    def scatter(xname: str, yname: str, filename: str):
        if xname not in names or yname not in names:
            return
        xi, yi = names.index(xname), names.index(yname)
        plt.figure(figsize=(5, 4))
        for path, ch in zip(paths, chains):
            seed = Path(path).name.split("_seed")[-1].split("_")[0]
            plt.scatter(ch[:, xi], ch[:, yi], s=2.5, alpha=0.18, label=seed)
        if xname == "s":
            plt.axvline(3.0, color="red", ls="--", lw=1)
        if yname in ("mu0", "Sigma0"):
            plt.axhline(0.0, color="red", ls="--", lw=1)
        if xname in ("mu0", "Sigma0"):
            plt.axvline(0.0, color="red", ls="--", lw=1)
        plt.xlabel(xname)
        plt.ylabel(yname)
        plt.legend(fontsize=7, title="seed")
        plt.tight_layout()
        plt.savefig(outdir / "figures" / filename, dpi=180, bbox_inches="tight")
        plt.close()

    scatter("s", "mu0", f"{args.model}_s_mu0.png")
    scatter("s", "Sigma0", f"{args.model}_s_Sigma0.png")
    scatter("mu0", "Sigma0", f"{args.model}_mu0_Sigma0.png")
    scatter("sigma8_0", "Sigma0", f"{args.model}_sigma8_Sigma0.png")

    # Trace plots from unflattened chains.
    un_paths = sorted(glob.glob(os.path.join(args.chains_dir, f"{args.model}_seed*_chain_unflattened.npy")))
    if un_paths:
        fig, axes = plt.subplots(len(names)+1, 1, figsize=(9, 1.9*(len(names)+1)), sharex=True)
        for j, name in enumerate(names):
            for p in un_paths:
                ch = np.load(p)
                axes[j].plot(ch[:, :, j], lw=0.35, alpha=0.12)
            axes[j].set_ylabel(name)
        for p in un_paths:
            lp_path = p.replace("_chain_unflattened.npy", "_logp_unflattened.npy")
            if os.path.exists(lp_path):
                axes[-1].plot(np.load(lp_path), lw=0.35, alpha=0.12)
        axes[-1].set_ylabel("logp")
        axes[-1].set_xlabel("step")
        fig.tight_layout()
        fig.savefig(outdir / "figures" / f"{args.model}_traces.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    # Response functions and E_G fit for G1DE-2.
    if args.model == "g1de2":
        like = make_likelihood_from_config(load_config(args.config))
        med = np.median(all_chain, axis=0)
        pars = like.theta_to_pars("g1de2", med)
        z = np.linspace(0, 2, 300)
        a = 1/(1+z)
        X = like.Xhat_a(a, pars["Omega_m"], pars["s"])
        plt.figure(figsize=(7,4.2))
        plt.plot(z, 1 + pars["mu0"]*X, label=f"mu(z), mu0={pars['mu0']:.3f}")
        plt.plot(z, 1 + pars["Sigma0"]*X, label=f"Sigma(z), Sigma0={pars['Sigma0']:.3f}")
        plt.axhline(1, color="k", lw=1)
        plt.xlabel("z")
        plt.ylabel("response")
        plt.legend()
        plt.tight_layout()
        plt.savefig(outdir / "figures" / "g1de2_mu_Sigma_response.png", dpi=180)
        plt.close()

        zplot = np.linspace(0.05, 0.8, 220)
        # Build E_G curve by temporarily evaluating at arbitrary z using a copy of the interpolation logic.
        sol = like.growth_solution("g1de2", med)
        if sol is not None:
            ag, D, f = sol
            ae = 1/(1+zplot)
            fz = np.interp(ae, ag, f)
            Sig = like.Sigma_response("g1de2", ae, pars)
            EG = pars["Omega_m"]*Sig/fz
            plt.figure(figsize=(7,4.6))
            plt.errorbar(like.z_eg, like.val_eg, yerr=like.eg["sigma"].to_numpy(float), fmt="o", capsize=3, label="E_G data")
            plt.plot(zplot, EG, label="G1DE-2 posterior median")
            plt.xlabel("z")
            plt.ylabel(r"$E_G(z)$")
            plt.legend()
            plt.tight_layout()
            plt.savefig(outdir / "figures" / "g1de2_EG_fit.png", dpi=180)
            plt.close()


if __name__ == "__main__":
    main()
