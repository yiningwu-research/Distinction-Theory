"""Generate figures and synthetic numerical results for FDS-E1 v0.2.

This script is intentionally deterministic. It produces the figures, CSV files,
and LaTeX table snippets used in the paper:
Finite-Capacity Prospect Theory: State-Dependent Risk Preferences under Resource,
Attention, and Boundary-Risk Constraints.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
TABLES = ROOT / "tables"
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
TABLES.mkdir(exist_ok=True)

EPS = 1e-8
rng = np.random.default_rng(20260516)


def risk_potential(d: np.ndarray, kappa: float = 1.0, eps: float = 0.08, nu: float = 1.15) -> np.ndarray:
    """Boundary-risk potential. d is perceived distance from the boundary."""
    d = np.maximum(d, EPS)
    return kappa * (d + eps) ** (-nu)


def local_lambda(d: np.ndarray, delta: float = 0.03, eps: float = 0.08, nu: float = 1.15) -> np.ndarray:
    """Local loss-aversion coefficient from asymmetric boundary-risk changes."""
    d = np.asarray(d)
    d0 = np.maximum(d, delta + 1e-5)
    loss_cost = risk_potential(d0 - delta, eps=eps, nu=nu) - risk_potential(d0, eps=eps, nu=nu)
    gain_relief = risk_potential(d0, eps=eps, nu=nu) - risk_potential(d0 + delta, eps=eps, nu=nu)
    return loss_cost / np.maximum(gain_relief, EPS)


def ces_effective_buffer(F: np.ndarray, weights: np.ndarray, eta: float) -> np.ndarray:
    """CES aggregator for resource vector F, row-wise."""
    F = np.maximum(F, 1e-6)
    weights = weights / weights.sum()
    if eta == 0:
        return np.exp(np.sum(weights * np.log(F), axis=1))
    return np.power(np.sum(weights * np.power(F, eta), axis=1), 1.0 / eta)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def weighting_function(p: np.ndarray, gamma: float) -> np.ndarray:
    """Tversky-Kahneman one-parameter inverse-S curve."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    num = np.power(p, gamma)
    den = np.power(p, gamma) + np.power(1 - p, gamma)
    return num / den


def figure_loss_aversion_fungibility() -> None:
    x = np.linspace(0.08, 1.0, 250)
    # Resource vector: monetary, sleep/time, attention. Vary only the second resource.
    F_sleep_depletion = np.column_stack([np.ones_like(x) * 0.85, x, np.ones_like(x) * 0.80])
    F_money_depletion = np.column_stack([x, np.ones_like(x) * 0.85, np.ones_like(x) * 0.80])
    weights = np.array([0.4, 0.35, 0.25])
    eta_fungible = 0.75
    eta_nonfungible = -5.0
    # d = F_eff - Fcrit; normalize by setting Fcrit=0.05 in these units.
    d_sleep_fungible = ces_effective_buffer(F_sleep_depletion, weights, eta_fungible) - 0.05
    d_sleep_nonfungible = ces_effective_buffer(F_sleep_depletion, weights, eta_nonfungible) - 0.05
    d_money_fungible = ces_effective_buffer(F_money_depletion, weights, eta_fungible) - 0.05
    d_money_nonfungible = ces_effective_buffer(F_money_depletion, weights, eta_nonfungible) - 0.05
    lam_sleep_fungible = local_lambda(d_sleep_fungible)
    lam_sleep_nonfungible = local_lambda(d_sleep_nonfungible)
    lam_money_fungible = local_lambda(d_money_fungible)
    lam_money_nonfungible = local_lambda(d_money_nonfungible)
    df = pd.DataFrame({
        "resource_level": x,
        "lambda_sleep_fungible": lam_sleep_fungible,
        "lambda_sleep_nonfungible": lam_sleep_nonfungible,
        "lambda_money_fungible": lam_money_fungible,
        "lambda_money_nonfungible": lam_money_nonfungible,
    })
    df.to_csv(DATA / "loss_aversion_fungibility.csv", index=False)
    plt.figure(figsize=(7, 4.5))
    plt.plot(x, lam_sleep_fungible, label="sleep/time depletion, fungible")
    plt.plot(x, lam_sleep_nonfungible, label="sleep/time depletion, non-fungible")
    plt.plot(x, lam_money_fungible, label="money depletion, fungible", linestyle="--")
    plt.plot(x, lam_money_nonfungible, label="money depletion, non-fungible", linestyle="--")
    plt.xlabel("resource dimension level")
    plt.ylabel("local loss-aversion coefficient")
    plt.title("Loss aversion rises nonlinearly when non-fungible resources deplete")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "fig1_loss_aversion_fungibility.pdf")
    plt.savefig(FIG / "fig1_loss_aversion_fungibility.png", dpi=220)
    plt.close()


def figure_perceived_distance() -> None:
    d_true = np.linspace(0.08, 2.0, 300)
    thetas = [1.25, 1.0, 0.65, 0.35]
    data = {"true_boundary_distance": d_true}
    plt.figure(figsize=(7, 4.5))
    for theta in thetas:
        d_hat = theta * d_true
        lam = local_lambda(d_hat)
        data[f"lambda_theta_{theta}"] = lam
        plt.plot(d_true, lam, label=f"perception factor theta={theta}")
    pd.DataFrame(data).to_csv(DATA / "perceived_boundary_mapping.csv", index=False)
    plt.xlabel("true resource-buffer distance")
    plt.ylabel("local loss-aversion coefficient")
    plt.title("Perceived boundary distance shifts loss aversion")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "fig2_perceived_distance.pdf")
    plt.savefig(FIG / "fig2_perceived_distance.png", dpi=220)
    plt.close()


def figure_reference_adaptation() -> None:
    T = 80
    t = np.arange(T)
    # Outcome stream: baseline 0, then sustained positive shock, then negative shock.
    x = np.zeros(T)
    x[15:45] = 1.0
    x[45:65] = -0.6
    x[65:] = 0.4
    # High buffer: faster adaptation and pruning of obsolete baseline.
    alpha_high = 0.24
    alpha_low = 0.07
    kappa_high = 0.02
    kappa_low = 0.005
    ref_high = np.zeros(T)
    ref_low = np.zeros(T)
    for i in range(1, T):
        pe_h = x[i-1] - ref_high[i-1]
        pe_l = x[i-1] - ref_low[i-1]
        ref_high[i] = ref_high[i-1] + alpha_high * pe_h - kappa_high * np.sign(ref_high[i-1]) * abs(ref_high[i-1])
        ref_low[i] = ref_low[i-1] + alpha_low * pe_l - kappa_low * np.sign(ref_low[i-1]) * abs(ref_low[i-1])
    df = pd.DataFrame({"time": t, "outcome": x, "reference_high_buffer": ref_high, "reference_low_buffer": ref_low})
    df.to_csv(DATA / "reference_adaptation.csv", index=False)
    plt.figure(figsize=(7, 4.5))
    plt.plot(t, x, label="outcome stream", linestyle="--")
    plt.plot(t, ref_high, label="reference, high buffer")
    plt.plot(t, ref_low, label="reference, depleted buffer")
    plt.xlabel("decision period")
    plt.ylabel("reference level")
    plt.title("Reference baselines adapt more slowly under resource depletion")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "fig3_reference_adaptation.pdf")
    plt.savefig(FIG / "fig3_reference_adaptation.png", dpi=220)
    plt.close()


def figure_probability_weighting() -> None:
    p = np.linspace(0.001, 0.999, 500)
    scenarios = [
        ("neutral event, high capacity", 0.92),
        ("neutral event, low capacity", 0.70),
        ("boundary-risk event, high capacity", 0.68),
        ("boundary-risk event, low capacity", 0.47),
    ]
    out = {"p": p}
    plt.figure(figsize=(7, 4.5))
    plt.plot(p, p, label="objective p", linestyle=":")
    for name, gamma in scenarios:
        w = weighting_function(p, gamma)
        out[name.replace(" ", "_").replace(",", "")] = w
        plt.plot(p, w, label=f"{name}, gamma={gamma}")
    pd.DataFrame(out).to_csv(DATA / "probability_weighting_by_capacity_event.csv", index=False)
    plt.xlabel("objective probability")
    plt.ylabel("decision weight")
    plt.title("Finite precision and boundary relevance amplify inverse-S weighting")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "fig4_probability_weighting.pdf")
    plt.savefig(FIG / "fig4_probability_weighting.png", dpi=220)
    plt.close()

    # Tail over-representation ratio for small p.
    small_p = np.array([0.005, 0.01, 0.02, 0.05, 0.10])
    rows = []
    for name, gamma in scenarios:
        w = weighting_function(small_p, gamma)
        for pp, ww in zip(small_p, w):
            rows.append({"scenario": name, "p": pp, "w_p": ww, "overrepresentation_ratio": ww/pp})
    pd.DataFrame(rows).to_csv(DATA / "tail_overrepresentation.csv", index=False)


def figure_nudge_bandwidth() -> None:
    N = 2000
    # Synthetic population with resource buffers and attention capacity.
    F_eff = rng.beta(2.0, 2.3, N) * 1.8 + 0.05
    C_available = 1.2 * np.log1p(3.0 * F_eff) + rng.normal(0, 0.08, N)
    C_available = np.maximum(C_available, 0.02)
    # Nudge complexity levels.
    complexity = np.array([0.35, 0.65, 0.95, 1.25])
    rows = []
    for c_req in complexity:
        margin = C_available - c_req
        # Positive when bandwidth sufficient; negative administrative-load backfire when not.
        effect = 0.18 * np.tanh(2.4 * margin) - 0.04 * (margin < -0.25)
        # Add small idiosyncratic noise for a plausible policy-outcome distribution.
        effect_noisy = effect + rng.normal(0, 0.025, N)
        quartile = pd.qcut(F_eff, 4, labels=["Q1 lowest buffer", "Q2", "Q3", "Q4 highest buffer"])
        tmp = pd.DataFrame({"F_eff": F_eff, "C_available": C_available, "nudge_complexity": c_req,
                            "nudge_effect": effect_noisy, "buffer_quartile": quartile.astype(str)})
        rows.append(tmp)
    df = pd.concat(rows, ignore_index=True)
    df.to_csv(DATA / "nudge_bandwidth_population.csv", index=False)
    summary = df.groupby(["buffer_quartile", "nudge_complexity"], as_index=False)["nudge_effect"].mean()
    summary.to_csv(DATA / "nudge_bandwidth_summary.csv", index=False)
    plt.figure(figsize=(7, 4.5))
    for q in ["Q1 lowest buffer", "Q2", "Q3", "Q4 highest buffer"]:
        s = summary[summary["buffer_quartile"] == q]
        plt.plot(s["nudge_complexity"], s["nudge_effect"], marker="o", label=q)
    plt.axhline(0, linestyle=":")
    plt.xlabel("nudge bandwidth requirement")
    plt.ylabel("mean treatment effect")
    plt.title("Complex nudges can fail or backfire when decision bandwidth is depleted")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "fig5_nudge_bandwidth.pdf")
    plt.savefig(FIG / "fig5_nudge_bandwidth.png", dpi=220)
    plt.close()


def synthetic_parameter_horse_race() -> None:
    N = 1200
    F_money = rng.lognormal(mean=-0.10, sigma=0.55, size=N)
    F_sleep = rng.beta(2.1, 2.4, size=N) * 1.6 + 0.05
    F_attention = rng.beta(2.5, 2.0, size=N) * 1.3 + 0.05
    weights = np.array([0.45, 0.30, 0.25])
    F = np.column_stack([F_money / np.percentile(F_money, 85), F_sleep, F_attention])
    F_eff = ces_effective_buffer(F, weights, eta=-2.5)
    theta = rng.lognormal(mean=-0.10, sigma=0.35, size=N)
    d_hat = np.maximum(theta * (F_eff - 0.08), 0.04)
    # True state-dependent parameters.
    lam_true = 1.05 + 0.19 * np.power(d_hat + 0.06, -0.82)
    lam_true = np.clip(lam_true, 1.05, 5.5)
    gamma_true = 0.38 + 0.54 * sigmoid(2.2 * (np.log(d_hat + 0.08) + 0.4))
    alpha_true = 0.04 + 0.30 * sigmoid(2.0 * (np.log(d_hat + 0.15) + 0.2))
    # Observed parameter estimates with measurement noise.
    lam_obs = lam_true + rng.normal(0, 0.18, N)
    gamma_obs = gamma_true + rng.normal(0, 0.035, N)
    alpha_obs = alpha_true + rng.normal(0, 0.025, N)
    df = pd.DataFrame({
        "F_money": F_money, "F_sleep": F_sleep, "F_attention": F_attention,
        "F_eff": F_eff, "theta": theta, "d_hat": d_hat,
        "lambda_obs": lam_obs, "gamma_obs": gamma_obs, "alpha_obs": alpha_obs,
        "lambda_true": lam_true, "gamma_true": gamma_true, "alpha_true": alpha_true
    })
    df.to_csv(DATA / "synthetic_subject_parameters.csv", index=False)

    def fit_constant(y: np.ndarray):
        yhat = np.full_like(y, np.mean(y))
        k = 1
        rss = np.sum((y - yhat) ** 2)
        rmse = np.sqrt(np.mean((y - yhat) ** 2))
        aic = N * np.log(rss / N) + 2 * k
        return yhat, rmse, aic, k

    def fit_state(y: np.ndarray):
        X = np.column_stack([np.ones(N), np.log(d_hat + 0.08), F_sleep, F_attention, np.log1p(F_money)])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        yhat = X @ beta
        k = X.shape[1]
        rss = np.sum((y - yhat) ** 2)
        rmse = np.sqrt(np.mean((y - yhat) ** 2))
        aic = N * np.log(rss / N) + 2 * k
        return yhat, rmse, aic, k, beta

    rows = []
    predictions = {}
    for name, y in [("lambda", lam_obs), ("gamma", gamma_obs), ("alpha", alpha_obs)]:
        yhat0, rmse0, aic0, k0 = fit_constant(y)
        yhat1, rmse1, aic1, k1, beta = fit_state(y)
        predictions[f"{name}_static"] = yhat0
        predictions[f"{name}_state"] = yhat1
        rows.append({"parameter": name, "model": "static Prospect parameter", "rmse": rmse0, "aic": aic0, "k": k0})
        rows.append({"parameter": name, "model": "finite-capacity state-dependent", "rmse": rmse1, "aic": aic1, "k": k1})
        # Save coefficient table.
        coef = pd.DataFrame({"term": ["intercept", "log(d_hat+0.08)", "F_sleep", "F_attention", "log(1+F_money)"], "coefficient": beta})
        coef.to_csv(DATA / f"state_model_coefficients_{name}.csv", index=False)
    comp = pd.DataFrame(rows)
    comp["delta_aic_vs_static"] = comp.groupby("parameter")["aic"].transform(lambda x: x - x.iloc[0])
    comp.to_csv(DATA / "model_comparison.csv", index=False)
    # LaTeX table snippet.
    with open(TABLES / "model_comparison_table.tex", "w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{llrrr}\n")
        f.write("\\toprule\n")
        f.write("Parameter & Model & RMSE & AIC & $\\Delta$AIC \\\\\n")
        f.write("\\midrule\n")
        for _, r in comp.iterrows():
            f.write(f"{r['parameter']} & {r['model']} & {r['rmse']:.3f} & {r['aic']:.1f} & {r['delta_aic_vs_static']:.1f} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")

    # Plot RMSE comparison.
    plt.figure(figsize=(7, 4.5))
    params = ["lambda", "gamma", "alpha"]
    xloc = np.arange(len(params))
    width = 0.35
    static_rmse = [comp[(comp.parameter == p) & (comp.model == "static Prospect parameter")]["rmse"].iloc[0] for p in params]
    state_rmse = [comp[(comp.parameter == p) & (comp.model == "finite-capacity state-dependent")]["rmse"].iloc[0] for p in params]
    plt.bar(xloc - width/2, static_rmse, width, label="static")
    plt.bar(xloc + width/2, state_rmse, width, label="state-dependent")
    plt.xticks(xloc, ["loss aversion", "weighting", "reference rate"])
    plt.ylabel("RMSE in synthetic parameter recovery")
    plt.title("State-dependent parameters improve synthetic recovery")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "fig6_model_comparison.pdf")
    plt.savefig(FIG / "fig6_model_comparison.png", dpi=220)
    plt.close()


def main() -> None:
    figure_loss_aversion_fungibility()
    figure_perceived_distance()
    figure_reference_adaptation()
    figure_probability_weighting()
    figure_nudge_bandwidth()
    synthetic_parameter_horse_race()
    print(f"Wrote results to {ROOT}")


if __name__ == "__main__":
    main()
