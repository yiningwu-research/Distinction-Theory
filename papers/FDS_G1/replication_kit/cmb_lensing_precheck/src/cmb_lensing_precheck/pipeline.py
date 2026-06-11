from __future__ import annotations

import json
from pathlib import Path
import shutil
import numpy as np
import matplotlib.pyplot as plt

from .background import make_background
from .growth import solve_growth
from .lensing import compute_lensing, LensingResult
from .likelihood import evaluate_act_dr6, evaluate_generic_npz, LikelihoodResult
from .power import make_power


def _prepare_output(cfg: dict) -> Path:
    out = Path(cfg["run"]["output_dir"])
    if out.exists() and cfg["run"].get("overwrite", False):
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    return out


def _range_summary(ell: np.ndarray, ratio: np.ndarray, lo: int, hi: int) -> dict:
    mask = (ell >= lo) & (ell <= hi) & np.isfinite(ratio)
    if not np.any(mask):
        return {"ell_min": lo, "ell_max": hi, "n": 0}
    r = ratio[mask]
    return {
        "ell_min": lo,
        "ell_max": hi,
        "n": int(r.size),
        "mean_ratio": float(np.mean(r)),
        "median_ratio": float(np.median(r)),
        "min_ratio": float(np.min(r)),
        "max_ratio": float(np.max(r)),
    }


def _evaluate_likelihood(cfg: dict, result: LensingResult) -> LikelihoodResult | None:
    lcfg = cfg["likelihood"]
    if lcfg["backend"] == "none":
        return None
    if lcfg["backend"] == "generic_npz":
        if not lcfg.get("path"):
            raise ValueError("likelihood.path is required for generic_npz backend.")
        return evaluate_generic_npz(
            lcfg["path"], result.ell, result.clpp_model, result.clkk_model,
            result.clpp_lcdm, result.clkk_lcdm,
        )
    if lcfg["backend"] == "act_dr6":
        return evaluate_act_dr6(cfg, result.ell, result.clpp_model, result.clpp_lcdm)
    raise ValueError(f"Unknown likelihood backend {lcfg['backend']!r}.")


def _save_tables(out: Path, result: LensingResult) -> None:
    np.savetxt(
        out / "clpp.csv",
        np.column_stack([
            result.ell, result.clpp_lcdm, result.clpp_model,
            result.clkk_lcdm, result.clkk_model, result.ratio,
        ]),
        delimiter=",",
        header="ell,clpp_lcdm,clpp_model,clkk_lcdm,clkk_model,ratio_model_over_lcdm",
        comments="",
    )
    np.savetxt(
        out / "background_growth.csv",
        np.column_stack([
            result.z_grid, result.sigma_pivot, result.growth_ratio,
            result.kernel_weight_lcdm,
        ]),
        delimiter=",",
        header="z,Sigma_at_L200,growth_delta_model_over_lcdm,lcdm_kernel_weight_unnormalized",
        comments="",
    )


def _save_plots(out: Path, result: LensingResult) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(result.ell, result.ratio)
    ax.axhline(1.0, linewidth=1.0)
    ax.set_xscale("log")
    ax.set_xlabel(r"$L$")
    ax.set_ylabel(r"$C_L^{\phi\phi,\,model}/C_L^{\phi\phi,\,LCDM}$")
    ax.set_title("CMB-lensing precheck ratio")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "clpp_ratio.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(result.z_grid, result.sigma_pivot)
    ax.axhline(1.0, linewidth=1.0)
    ax.set_xscale("log")
    ax.set_xlim(max(result.z_grid.min(), 1e-3), min(20.0, result.z_grid.max()))
    ax.set_xlabel("z")
    ax.set_ylabel(r"$\Sigma(z,k_{L=200})$")
    ax.set_title("Registered Weyl response")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "sigma_of_z.png", dpi=180)
    plt.close(fig)

    kernel = result.kernel_weight_lcdm
    kernel_norm = kernel / np.trapz(kernel, result.z_grid)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(result.z_grid, kernel_norm, label="LCDM geometry kernel")
    ax.plot(result.z_grid, result.growth_ratio, label="growth ratio")
    ax.set_xscale("log")
    ax.set_xlim(max(result.z_grid.min(), 1e-3), min(30.0, result.z_grid.max()))
    ax.set_xlabel("z")
    ax.set_title("Kernel and growth diagnostics")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "kernel_diagnostics.png", dpi=180)
    plt.close(fig)


def run_precheck(cfg: dict, write_artifacts: bool = True, return_result: bool = False):
    out = _prepare_output(cfg) if write_artifacts else None
    model_bg_name = "lcdm" if cfg["model"]["name"] == "lcdm" else "g1de"
    bg_model = make_background(cfg, model_bg_name)
    bg_lcdm = make_background(cfg, "lcdm")
    growth_model = solve_growth(bg_model, float(cfg["integration"]["a_ini"]))
    growth_lcdm = solve_growth(bg_lcdm, float(cfg["integration"]["a_ini"]))
    power = make_power(cfg)
    try:
        result = compute_lensing(cfg, bg_model, bg_lcdm, growth_model, growth_lcdm, power)
        like = _evaluate_likelihood(cfg, result)
        if write_artifacts:
            assert out is not None
            _save_tables(out, result)
            _save_plots(out, result)
        summary = {
            "status": "pre-production",
            "config_path": cfg.get("_config_path"),
            "run_name": cfg["run"]["name"],
            "model": cfg["model"],
            "amplitude": cfg["amplitude"],
            "power_backend": cfg["power"]["backend"],
            "power_sigma8_baseline": float(power.sigma8),
            "growth_delta_today_ratio_model_over_lcdm": float(growth_model.delta_today / growth_lcdm.delta_today),
            "clpp_ratio_ranges": [
                _range_summary(result.ell, result.ratio, 8, 40),
                _range_summary(result.ell, result.ratio, 40, 400),
                _range_summary(result.ell, result.ratio, 400, 1000),
                _range_summary(result.ell, result.ratio, 1000, int(result.ell.max())),
            ],
            "likelihood": None if like is None else {
                "backend": like.backend,
                "chi2_model": like.chi2_model,
                "chi2_lcdm": like.chi2_lcdm,
                "delta_chi2": like.delta_chi2,
                "metadata": like.metadata,
            },
            "claim_boundary": (
                "Linear-Limber precheck with unchanged early transfer function; not a full D11 "
                "Boltzmann or primary-CMB likelihood result."
            ),
        }
        if write_artifacts:
            assert out is not None
            with (out / "summary.json").open("w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
        return (summary, result) if return_result else summary
    finally:
        close = getattr(power, "close", None)
        if callable(close):
            close()
