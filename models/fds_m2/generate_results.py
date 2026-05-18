#!/usr/bin/env python3
"""
Deterministic synthetic normal-form illustrations for:
Value and Goal as Boundary-Relevance Ranking.

These simulations are illustrative only. They visualize definitions and failure modes;
they are not empirical evidence.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

rng = np.random.default_rng(20260518)


def savefig(name: str):
    for ext in ["pdf", "png"]:
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=220)
    plt.close()


def fig1_value_funnel():
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")
    stages = [
        ("candidate distinctions", "environment / memory / social signals"),
        ("M1 attention admission", "finite gate + verification path"),
        ("M2 FDS-value evaluation", "gross gain, net value, risk value"),
        ("M2 ranking", "boundary-relevance ordering"),
        ("M2 goal stabilization", "policy orientation over update windows"),
        ("M3 meaning interface", "actionable semantic quotient"),
    ]
    widths = np.linspace(0.88, 0.38, len(stages))
    ys = np.linspace(0.86, 0.18, len(stages))
    for i, ((title, subtitle), w, y) in enumerate(zip(stages, widths, ys)):
        x0, x1 = 0.5 - w/2, 0.5 + w/2
        h = 0.085
        poly = plt.Polygon([[x0, y+h/2], [x1, y+h/2], [x1-0.03, y-h/2], [x0+0.03, y-h/2]],
                           fill=False, lw=1.3, transform=ax.transAxes)
        ax.add_patch(poly)
        ax.text(0.5, y+0.013, title, ha="center", va="center", fontsize=10, weight="bold", transform=ax.transAxes)
        ax.text(0.5, y-0.022, subtitle, ha="center", va="center", fontsize=8, transform=ax.transAxes)
        if i < len(stages)-1:
            ax.annotate("", xy=(0.5, ys[i+1]+0.07), xytext=(0.5, y-0.07),
                        arrowprops=dict(arrowstyle="->", lw=1.1), xycoords=ax.transAxes)
    ax.text(0.5, 0.04, "Synthetic normal-form illustration: from environmental differences to stabilized goals and meaning interfaces.",
            ha="center", va="center", fontsize=9, transform=ax.transAxes)
    savefig("fig1_value_funnel")


def fig2_predictive_vs_causal():
    n = 280
    latent = rng.normal(0, 1, n)
    predictive = 0.65 * latent + rng.normal(0, 0.7, n)
    gross_gain = 0.45 * latent + rng.normal(0, 0.85, n)
    idx_hidden = rng.choice(n, 30, replace=False)
    predictive[idx_hidden] -= rng.uniform(0.8, 1.5, len(idx_hidden))
    gross_gain[idx_hidden] += rng.uniform(0.7, 1.4, len(idx_hidden))
    remain = np.setdiff1d(np.arange(n), idx_hidden)
    idx_predonly = rng.choice(remain, 32, replace=False)
    predictive[idx_predonly] += rng.uniform(0.8, 1.5, len(idx_predonly))
    gross_gain[idx_predonly] -= rng.uniform(0.7, 1.4, len(idx_predonly))
    cost = rng.uniform(0.05, 0.45, n)
    net_value = gross_gain - 0.65 * cost
    admitted = net_value > np.quantile(net_value, 0.74)
    df = pd.DataFrame({"predictive_relevance": predictive, "gross_causal_boundary_gain": gross_gain,
                       "cost": cost, "net_fds_value": net_value, "selected": admitted})
    df.to_csv(DATA / "predictive_vs_causal.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(predictive[~admitted], gross_gain[~admitted], s=18, alpha=0.55, label="evaluand")
    ax.scatter(predictive[admitted], gross_gain[admitted], s=35, marker="x", label="high net FDS-value")
    ax.axhline(0, lw=1, ls="--")
    ax.axvline(0, lw=1, ls="--")
    ax.text(1.05, 1.55, "predictive + causal", fontsize=8)
    ax.text(1.05, -1.65, "predictive-only\nwarning", fontsize=8)
    ax.text(-2.35, 1.35, "hidden causal\nlever", fontsize=8)
    ax.text(-2.25, -1.75, "irrelevant /\nnoise", fontsize=8)
    ax.set_xlabel("predictive relevance")
    ax.set_ylabel("gross causal boundary gain")
    ax.set_title("Synthetic normal-form illustration: predictive vs causal value")
    ax.legend(loc="lower right", fontsize=8)
    savefig("fig2_predictive_vs_causal")


def fig3_risk_weighted_ranking():
    alpha = np.linspace(0, 4.2, 140)
    loss_A, risk_A, cost_A = 1.05, 0.04, 0.12
    loss_B, risk_B, cost_B = 0.55, 0.27, 0.14
    V_A = loss_A + alpha * risk_A - cost_A
    V_B = loss_B + alpha * risk_B - cost_B
    # normal-form coupling between resource reserve and risk sensitivity
    phi_reserve = np.linspace(1.2, 0.1, 140)
    alpha_phi = 0.3 + 0.55 / (phi_reserve + 0.08)
    df = pd.DataFrame({"alpha": alpha, "value_A_avg_improver": V_A, "value_B_risk_reducer": V_B,
                       "resource_reserve_phi_minus_crit": phi_reserve, "alpha_from_resource_reserve": alpha_phi})
    df.to_csv(DATA / "risk_weighted_ranking.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.plot(alpha, V_A, label="A: average-loss improver")
    ax.plot(alpha, V_B, label="B: collapse-risk reducer")
    ix = np.argmin(np.abs(V_A - V_B))
    ax.axvline(alpha[ix], lw=1, ls="--")
    ax.text(alpha[ix]+0.08, max(V_A[ix], V_B[ix])+0.06, "ranking switch", fontsize=8)
    ax.set_xlabel("risk sensitivity $\\alpha_t$")
    ax.set_ylabel("risk-weighted net FDS-value")
    ax.set_title("Synthetic normal-form illustration: risk-weighted ranking near threshold")
    ax.legend(fontsize=8)
    savefig("fig3_risk_weighted_ranking")


def fig4_goal_stability():
    t = np.arange(0, 100)
    def dip(center, width, depth):
        return depth * np.exp(-0.5 * ((t-center)/width)**2)
    reflex = np.clip(0.35 + 0.08*np.sin(t/3.0) - dip(50, 10, 0.2), 0, 1)
    preference = np.clip(0.58 + 0.05*np.sin(t/9.0) - dip(50, 12, 0.18), 0, 1)
    goal = np.clip(0.82 - dip(50, 10, 0.18) + 0.02*np.sin(t/12), 0, 1)
    commitment = np.clip(0.94 - dip(50, 12, 0.08), 0, 1)
    df = pd.DataFrame({"time": t, "reflex": reflex, "preference": preference,
                       "goal": goal, "commitment": commitment})
    df.to_csv(DATA / "goal_stability.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.plot(t, reflex, label="reflex")
    ax.plot(t, preference, label="preference")
    ax.plot(t, goal, label="goal-like policy")
    ax.plot(t, commitment, label="commitment-like policy")
    ax.axvspan(42, 60, alpha=0.12, label="perturbation")
    ax.set_xlabel("time")
    ax.set_ylabel("goal-stability index")
    ax.set_ylim(0, 1.05)
    ax.set_title("Synthetic normal-form illustration: goal stability under perturbation")
    ax.legend(fontsize=8, loc="lower right")
    savefig("fig4_goal_stability")


def fig5_proxy_reward_hacking():
    n = 240
    proxy_delta = rng.normal(0, 1, n)
    loss_delta = -0.55 * proxy_delta + rng.normal(0, 0.75, n)
    idx = rng.choice(n, 40, replace=False)
    proxy_delta[idx] += rng.uniform(0.6, 1.5, len(idx))
    loss_delta[idx] += rng.uniform(0.8, 1.8, len(idx))
    hacked = (proxy_delta > 0) & (loss_delta > 0)
    df = pd.DataFrame({"delta_proxy_reward": proxy_delta, "delta_boundary_loss": loss_delta, "proxy_boundary_inversion": hacked})
    df.to_csv(DATA / "proxy_boundary_divergence.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(proxy_delta[~hacked], loss_delta[~hacked], s=20, alpha=0.55, label="candidate action")
    ax.scatter(proxy_delta[hacked], loss_delta[hacked], s=34, marker="x", label="proxy-positive / boundary-negative")
    ax.axhline(0, lw=1, ls="--")
    ax.axvline(0, lw=1, ls="--")
    ax.text(0.25, 1.85, "reward-hacking\nzone", fontsize=9)
    ax.set_xlabel("$\\Delta R_{\\rm proxy}$")
    ax.set_ylabel("$\\Delta \\ell_{\\rm host}$")
    ax.set_title("Synthetic normal-form illustration: proxy reward vs boundary value")
    ax.legend(fontsize=8, loc="lower left")
    savefig("fig5_proxy_boundary_divergence")


def fig6_evaluation_deficit():
    deficit = np.linspace(0, 1.5, 100)
    ranking_accuracy = 1 / (1 + np.exp(4*(deficit-0.75)))
    salience_substitution = 1 / (1 + np.exp(-5*(deficit-0.65)))
    proxy_dependence = 1 / (1 + np.exp(-4*(deficit-0.85)))
    coarse_preference = 1 / (1 + np.exp(-4*(deficit-0.55)))
    drift = 1 - ranking_accuracy
    df = pd.DataFrame({"evaluation_deficit": deficit, "ranking_accuracy": ranking_accuracy,
                       "salience_substitution": salience_substitution,
                       "proxy_dependence": proxy_dependence, "coarse_preference": coarse_preference,
                       "value_drift": drift})
    df.to_csv(DATA / "evaluation_deficit_value_drift.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.plot(deficit, ranking_accuracy, label="verified ranking accuracy")
    ax.plot(deficit, salience_substitution, label="salience substitution")
    ax.plot(deficit, proxy_dependence, label="proxy dependence")
    ax.plot(deficit, coarse_preference, label="coarse preference")
    ax.plot(deficit, drift, label="value drift")
    ax.axvline(0.75, lw=1, ls="--")
    ax.set_xlabel("evaluation capacity deficit $\\Delta_{eval}$")
    ax.set_ylabel("normalized level")
    ax.set_title("Synthetic normal-form illustration: second-order evaluation deficit")
    ax.legend(fontsize=8)
    savefig("fig6_evaluation_deficit")


def pareto_front(points):
    order = np.argsort(points[:, 0])
    pts = points[order]
    front = []
    max_y = -np.inf
    for x, y in pts[::-1]:
        if y > max_y:
            front.append((x, y))
            max_y = y
    return np.array(front[::-1])


def fig7_multi_goal_pareto():
    n = 220
    speed = rng.uniform(0, 1, n)
    safety = 1 - 0.85*speed + rng.normal(0, 0.13, n) + 0.25*np.sin(3*np.pi*speed)
    safety = np.clip(safety, 0, 1.05)
    points = np.column_stack([speed, safety])
    front = pareto_front(points)
    df = pd.DataFrame({"opportunity_value": speed, "safety_value": safety})
    df.to_csv(DATA / "multi_goal_pareto.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(speed, safety, s=18, alpha=0.5, label="feasible policy")
    if len(front) > 1:
        ax.plot(front[:, 0], front[:, 1], lw=2, label="Pareto frontier")
    xline = np.linspace(0, 1, 100)
    ax.plot(xline, 0.82 - 0.35*xline, ls="--", label="one scalarization")
    ax.set_xlabel("boundary dimension 1: opportunity / throughput")
    ax.set_ylabel("boundary dimension 2: safety / robustness")
    ax.set_title("Synthetic normal-form illustration: multi-goal conflict and Pareto front")
    ax.legend(fontsize=8)
    savefig("fig7_multi_goal_pareto")


def fig8_goal_hysteresis():
    t = np.arange(0, 130)
    threat = np.zeros_like(t, dtype=float)
    threat[25:70] = np.linspace(0, 1, 45)
    threat[70:88] = np.linspace(1, 0.15, 18)
    threat[88:] = 0.05
    h = np.zeros_like(t, dtype=float)
    alpha = np.zeros_like(t, dtype=float)
    diversity = np.zeros_like(t, dtype=float)
    for i in range(1, len(t)):
        increment = 0.08 if threat[i] > 0.55 else 0.0
        h[i] = 0.96*h[i-1] + increment
        target_alpha = 0.4 + 2.0*threat[i]
        alpha[i] = 0.92*alpha[i-1] + 0.08*(target_alpha + 0.9*h[i])
    diversity = np.clip(1.05 - 0.28*alpha + 0.02*np.sin(t/6), 0.05, 1)
    df = pd.DataFrame({"time": t, "threat_load": threat, "goal_hysteresis": h,
                       "risk_weight_alpha": alpha, "ranking_diversity": diversity})
    df.to_csv(DATA / "goal_hysteresis.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.plot(t, threat, label="threat / boundary load")
    ax.plot(t, alpha/np.max(alpha), label="risk-weighting / goal rigidity")
    ax.plot(t, diversity, label="ranking diversity")
    ax.axvspan(25, 88, alpha=0.10, label="crisis interval")
    ax.set_xlabel("time")
    ax.set_ylabel("normalized level")
    ax.set_title("Synthetic normal-form illustration: goal hysteresis and recovery lag")
    ax.legend(fontsize=8, loc="best")
    savefig("fig8_goal_hysteresis")


def main():
    fig1_value_funnel()
    fig2_predictive_vs_causal()
    fig3_risk_weighted_ranking()
    fig4_goal_stability()
    fig5_proxy_reward_hacking()
    fig6_evaluation_deficit()
    fig7_multi_goal_pareto()
    fig8_goal_hysteresis()
    print(f"Wrote figures to {FIG}")
    print(f"Wrote data to {DATA}")


if __name__ == "__main__":
    main()
