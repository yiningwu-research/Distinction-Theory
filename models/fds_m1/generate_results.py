"""Generate deterministic synthetic normal-form figures for
"Attention as Distinction Admission in Finite Systems" (v0.2).

The model is illustrative only. It visualizes FDS-M1 definitions:
capacity-limited distinction admission, salience-value dissociation,
verification burden, background scanning, nonlinear tunnel-vision gates,
attention hysteresis, failure modes, and collective attention saturation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
DATA_DIR = ROOT / "data"
FIG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

RNG = np.random.default_rng(20260517)


def savefig(name: str) -> None:
    for ext in ("pdf", "png"):
        plt.savefig(FIG_DIR / f"{name}.{ext}", bbox_inches="tight", dpi=220)
    plt.close()


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def make_candidates(n: int = 220) -> pd.DataFrame:
    """Synthetic distinction candidates.

    The variables are not empirical. They are deterministic random draws used
    to illustrate the formal distinction between raw salience, causal boundary
    value, verification burden, and exploratory information gain.
    """
    salience = RNG.beta(2.2, 2.0, n)
    novelty = RNG.beta(1.8, 3.0, n)
    threat = RNG.beta(1.6, 4.0, n)
    long_horizon_relevance = RNG.beta(2.0, 2.5, n)
    source_uncertainty = RNG.beta(1.7, 2.6, n)
    model_divergence = RNG.gamma(shape=1.25, scale=0.38, size=n)  # KL-like incompatibility
    crosscheck_cost = RNG.gamma(shape=1.4, scale=0.12, size=n)

    encoding_cost = 0.10 + RNG.gamma(shape=1.2, scale=0.12, size=n)
    maintenance_cost = 0.10 + RNG.gamma(shape=1.4, scale=0.16, size=n)
    verification_cost = (
        0.12
        + 0.22 * source_uncertainty
        + 0.34 * model_divergence
        + 0.55 * crosscheck_cost
        + RNG.gamma(shape=1.2, scale=0.08, size=n)
    )
    opportunity_cost = 0.04 + RNG.gamma(shape=1.2, scale=0.06, size=n)
    cost = encoding_cost + verification_cost + maintenance_cost + opportunity_cost

    # Boundary value is not identical to salience. Threat and long-horizon relevance matter.
    causal_value = (
        1.20 * long_horizon_relevance
        + 0.92 * threat
        + 0.22 * novelty
        + RNG.normal(0, 0.08, n)
        - 0.30 * verification_cost
    )
    collapse_risk_reduction = np.maximum(0, 0.90 * threat + 0.20 * novelty - 0.22 * verification_cost)
    information_gain = np.maximum(0, 0.72 * model_divergence + 0.40 * novelty - 0.28 * verification_cost)
    gate_score = causal_value + 0.55 * collapse_risk_reduction + 0.28 * information_gain
    value_density = gate_score / cost
    salience_priority = (salience + 0.10 * novelty) / cost

    df = pd.DataFrame(
        {
            "id": np.arange(n),
            "salience": salience,
            "novelty": novelty,
            "threat": threat,
            "long_horizon_relevance": long_horizon_relevance,
            "source_uncertainty": source_uncertainty,
            "model_divergence_kl_like": model_divergence,
            "crosscheck_cost": crosscheck_cost,
            "encoding_cost": encoding_cost,
            "verification_cost": verification_cost,
            "maintenance_cost": maintenance_cost,
            "opportunity_cost": opportunity_cost,
            "cost": cost,
            "causal_value": causal_value,
            "collapse_risk_reduction": collapse_risk_reduction,
            "information_gain": information_gain,
            "gate_score": gate_score,
            "value_density": value_density,
            "salience_priority": salience_priority,
        }
    )
    df.to_csv(DATA_DIR / "candidate_distinctions.csv", index=False)
    return df


def greedy_admission(df: pd.DataFrame, capacity: float, score_col: str = "value_density") -> pd.DataFrame:
    sorted_df = df.sort_values(score_col, ascending=False).copy()
    admitted = []
    total = 0.0
    for _, row in sorted_df.iterrows():
        if total + row["cost"] <= capacity:
            admitted.append(True)
            total += row["cost"]
        else:
            admitted.append(False)
    sorted_df["admitted"] = admitted
    return sorted_df.sort_index()


def fig1_flow() -> None:
    plt.figure(figsize=(9.0, 3.9))
    ax = plt.gca()
    ax.axis("off")
    nodes = [
        ("Candidate\ndistinctions", 0.06, 0.58),
        ("Admission\ngate", 0.25, 0.58),
        ("Verification\npath/status", 0.44, 0.58),
        ("Maintained\nrecord", 0.63, 0.58),
        ("Update / action\npolicy", 0.82, 0.58),
    ]
    for text, x, y in nodes:
        box = FancyBboxPatch(
            (x - 0.075, y - 0.125),
            0.15,
            0.25,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            linewidth=1.4,
            facecolor="white",
            edgecolor="black",
        )
        ax.add_patch(box)
        ax.text(x, y, text, ha="center", va="center", fontsize=9.5)
    for i in range(len(nodes) - 1):
        x1, y1 = nodes[i][1] + 0.075, nodes[i][2]
        x2, y2 = nodes[i + 1][1] - 0.075, nodes[i + 1][2]
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->", mutation_scale=14, lw=1.4))
    ax.text(0.18, 0.17, r"capacity: $\sum a_t(d)c_t(d) \leq C_{att}$", ha="center", fontsize=9)
    ax.text(0.52, 0.09, "trusted / for-verification / rejected-unverified", ha="center", fontsize=9)
    ax.add_patch(FancyArrowPatch((0.82, 0.43), (0.25, 0.43), connectionstyle="arc3,rad=-0.25", arrowstyle="->", mutation_scale=14, lw=1.2, linestyle="--"))
    ax.text(0.55, 0.02, "boundary-loss feedback changes future admission priorities", ha="center", fontsize=9)
    ax.set_title("Synthetic normal-form illustration: attention as distinction admission")
    savefig("fig1_attention_flow")


def fig2_salience_value(df: pd.DataFrame) -> None:
    capacity = df["cost"].sum() * 0.24
    admitted_by_value = greedy_admission(df, capacity)
    out = df.copy()
    out["admitted_value"] = admitted_by_value["admitted"]
    out.to_csv(DATA_DIR / "salience_value_admission.csv", index=False)
    plt.figure(figsize=(7.8, 5.3))
    sx = df["salience"]
    vy = df["causal_value"]
    xmid = float(np.quantile(sx, 0.62))
    ymid = float(np.quantile(vy, 0.62))
    plt.scatter(sx, vy, s=25, alpha=0.50, label="candidate")
    adm = out[out["admitted_value"]]
    plt.scatter(adm["salience"], adm["causal_value"], s=45, marker="x", label="admitted by FDS value")
    plt.axvline(xmid, linestyle="--", lw=1.0, color="gray", alpha=0.5)
    plt.axhline(ymid, linestyle="--", lw=1.0, color="gray", alpha=0.5)
    plt.fill_between([plt.xlim()[0], xmid], ymid, plt.ylim()[1], alpha=0.04, color="darkblue")
    plt.fill_between([xmid, plt.xlim()[1]], ymid, plt.ylim()[1], alpha=0.04, color="darkblue")
    plt.fill_between([plt.xlim()[0], xmid], plt.ylim()[0], ymid, alpha=0.04, color="darkred")
    plt.fill_between([xmid, plt.xlim()[1]], plt.ylim()[0], ymid, alpha=0.04, color="darkred")
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(alpha=0.12, color="darkblue", label="high value"),
        Patch(alpha=0.12, color="darkred", label="low value"),
    ]
    plt.text(xmid + 0.02, ymid + 0.35, "urgent relevant signal", fontsize=7.5, fontstyle="italic")
    plt.text(xmid + 0.02, ymid - 0.42, "salience trap", fontsize=7.5, fontstyle="italic")
    plt.text(xmid - 0.43, ymid + 0.35, "hidden critical signal", fontsize=7.5, fontstyle="italic")
    plt.text(xmid - 0.38, ymid - 0.42, "background noise", fontsize=7.5, fontstyle="italic")
    plt.xlabel("raw salience")
    plt.ylabel("causal boundary-gradient value")
    plt.title("Synthetic normal-form illustration: salience-value dissociation")
    plt.legend(frameon=False)
    plt.grid(alpha=0.25)
    savefig("fig2_salience_value_dissociation")


def fig3_capacity_sweep(df: pd.DataFrame) -> None:
    total_cost = df["cost"].sum()
    caps = np.linspace(0.05 * total_cost, 0.72 * total_cost, 55)
    rows = []
    for c in caps:
        exploit_capacity = 0.88 * c
        scan_capacity = 0.12 * c
        admitted_exploit = greedy_admission(df, exploit_capacity, "value_density")
        rest = df.loc[~admitted_exploit["admitted"]].copy()
        # Background scanning samples uncertain/high-info-gain candidates not selected by exploitation.
        scan = greedy_admission(rest, scan_capacity, "information_gain")
        admitted_ids = set(admitted_exploit[admitted_exploit["admitted"]]["id"]).union(
            set(scan[scan["admitted"]]["id"])
        )
        subset = df[df["id"].isin(admitted_ids)]
        rows.append(
            {
                "capacity": c,
                "fraction_capacity": c / total_cost,
                "num_admitted": len(subset),
                "value_retained": subset["causal_value"].clip(lower=0).sum(),
                "mean_information_gain": subset["information_gain"].mean() if len(subset) else 0,
                "scan_count": len(set(scan[scan["admitted"]]["id"])),
            }
        )
    sweep = pd.DataFrame(rows)
    sweep.to_csv(DATA_DIR / "capacity_sweep.csv", index=False)
    plt.figure(figsize=(7.6, 5.0))
    plt.plot(sweep["fraction_capacity"], sweep["num_admitted"], marker="o", ms=3, label="admitted distinctions")
    plt.plot(sweep["fraction_capacity"], sweep["value_retained"] / sweep["value_retained"].max() * sweep["num_admitted"].max(), lw=2, label="retained value (scaled)")
    plt.plot(sweep["fraction_capacity"], sweep["scan_count"], lw=2, label="background scan count")
    plt.xlabel("attention capacity as fraction of full candidate cost")
    plt.ylabel("admitted count / scaled retained value")
    plt.title("Synthetic normal-form illustration: capacity-limited admission with scanning")
    plt.legend(frameon=False)
    plt.grid(alpha=0.25)
    savefig("fig3_capacity_limited_admission")


def fig4_verification_burden(df: pd.DataFrame) -> None:
    threshold = float(np.quantile(df["verification_cost"], 0.74))
    d2 = df.copy()
    d2["gross_priority"] = 0.70 * d2["salience"] + 0.80 * d2["causal_value"].clip(lower=0) + 0.35 * d2["information_gain"]
    d2["net_priority"] = d2["gross_priority"] - 0.95 * d2["verification_cost"]
    d2["rejected_by_verification"] = (d2["gross_priority"] > np.quantile(d2["gross_priority"], 0.62)) & (d2["verification_cost"] > threshold)
    d2.to_csv(DATA_DIR / "verification_burden.csv", index=False)
    plt.figure(figsize=(7.6, 5.2))
    plt.scatter(d2["gross_priority"], d2["verification_cost"], s=28, alpha=0.55, label="candidate")
    rej = d2[d2["rejected_by_verification"]]
    plt.scatter(rej["gross_priority"], rej["verification_cost"], s=48, marker="x", label="rejected despite priority")
    plt.axhline(threshold, linestyle="--", lw=1.3, label=r"$c^{verify}=C^{avail}_{verify}$ threshold")
    plt.xlabel("gross salience/value/curiosity priority")
    plt.ylabel("verification cost")
    plt.title("Synthetic normal-form illustration: verification-limited attention")
    plt.legend(frameon=False)
    plt.grid(alpha=0.25)
    savefig("fig4_verification_limited_attention")


def fig5_tunnel_vision() -> None:
    x = np.linspace(-3, 3, 240)
    deficits = [0.0, 0.45, 0.9]
    rows = []
    plt.figure(figsize=(7.6, 5.0))
    for d in deficits:
        beta = 1.0 + 3.6 * max(d, 0)
        y = sigmoid(beta * x)
        rows.extend({"score": xi, "deficit": d, "admission_probability": yi, "beta": beta} for xi, yi in zip(x, y))
        plt.plot(x, y, lw=2, label=fr"$\Delta_{{att}}$={d:.2f}")
    pd.DataFrame(rows).to_csv(DATA_DIR / "tunnel_vision_gate.csv", index=False)
    plt.xlabel("standardized value-threat-cost score")
    plt.ylabel("admission probability")
    plt.title("Synthetic normal-form illustration: nonlinear gate steepening")
    plt.legend(frameon=False)
    plt.grid(alpha=0.25)
    savefig("fig5_tunnel_vision_gate")


def fig6_failure_modes() -> None:
    modes = ["overload", "distraction", "salience\ncapture", "suppression", "critical\nexclusion", "false\nadmission", "verification\nsaturation", "recovery\nlag"]
    admission_error = np.array([0.78, 0.55, 0.64, 0.45, 0.82, 0.58, 0.74, 0.62])
    maintenance_error = np.array([0.62, 0.40, 0.50, 0.35, 0.68, 0.70, 0.81, 0.73])
    df = pd.DataFrame({"mode": modes, "admission_error": admission_error, "maintenance_error": maintenance_error})
    df.to_csv(DATA_DIR / "failure_modes.csv", index=False)
    x = np.arange(len(modes))
    width = 0.36
    plt.figure(figsize=(8.6, 4.8))
    plt.bar(x - width/2, admission_error, width, label="admission error")
    plt.bar(x + width/2, maintenance_error, width, label="maintenance/verification error")
    plt.xticks(x, modes)
    plt.ylim(0, 1.0)
    plt.ylabel("normalized failure intensity")
    plt.title("Synthetic normal-form illustration: attention failure modes")
    plt.legend(frameon=False)
    plt.grid(axis="y", alpha=0.25)
    savefig("fig6_attention_failure_modes")


def fig7_recovery_hysteresis() -> None:
    t = np.arange(120)
    shock = sigmoid((t - 22) / 4) - sigmoid((t - 58) / 5)
    background_load = 0.12 + 0.04 * np.sin(t / 9)
    deficit = np.clip(0.15 + 0.78 * shock + background_load, 0, None)
    # Target beta follows deficit, but actual beta relaxes slowly and locks in after crisis.
    beta_target = 1.0 + 4.0 * deficit
    beta = np.zeros_like(beta_target)
    beta[0] = beta_target[0]
    lock = 0.0
    for i in range(1, len(t)):
        if deficit[i] > 0.55:
            lock += 0.035
        else:
            lock *= 0.965
        beta[i] = beta[i-1] + 0.11 * (beta_target[i] + lock - beta[i-1])
    admission_diversity = 1.18 / (1.0 + 0.62 * beta)
    df = pd.DataFrame({"time": t, "semantic_deficit": deficit, "beta_target": beta_target, "beta_actual_hysteretic": beta, "admission_diversity": admission_diversity})
    df.to_csv(DATA_DIR / "attention_recovery.csv", index=False)
    plt.figure(figsize=(7.7, 5.0))
    plt.plot(t, deficit, lw=2, label="semantic/attention deficit")
    plt.plot(t, beta / beta.max(), lw=2, label="gate steepness beta (scaled)")
    plt.plot(t, admission_diversity / admission_diversity.max(), lw=2, label="admission diversity (scaled)")
    plt.axvspan(22, 58, alpha=0.12, label="crisis load")
    plt.xlabel("time")
    plt.ylabel("normalized level")
    plt.title("Synthetic normal-form illustration: attention hysteresis and recovery delay")
    plt.legend(frameon=False)
    plt.grid(alpha=0.25)
    savefig("fig7_attention_recovery")


def fig8_collective_pollution() -> None:
    t = np.arange(100)
    verification_demand = 0.55 + 0.030 * t + 0.25 * np.sin(t / 8)
    capacity = 1.65 + 0.006 * t
    saturation = verification_demand / capacity
    false_admission = sigmoid(3.0 * (saturation - 1.0))
    agenda_capture = sigmoid(2.5 * (saturation - 1.25))
    gate_narrowing = sigmoid(3.2 * (saturation - 1.10))
    df = pd.DataFrame({"time": t, "verification_demand": verification_demand, "verification_capacity": capacity, "saturation": saturation, "false_admission_risk": false_admission, "agenda_capture_risk": agenda_capture, "collective_gate_narrowing": gate_narrowing})
    df.to_csv(DATA_DIR / "collective_attention_pollution.csv", index=False)
    plt.figure(figsize=(7.7, 5.0))
    plt.plot(t, saturation, lw=2, label="verification saturation $Z_{att/poll}$")
    plt.plot(t, false_admission, lw=2, label="false admission risk")
    plt.plot(t, agenda_capture, lw=2, label="agenda capture risk")
    plt.plot(t, gate_narrowing, lw=2, label="collective tunnel vision")
    plt.axhline(1.0, linestyle="--", lw=1.2, label="capacity threshold")
    plt.xlabel("time")
    plt.ylabel("normalized level")
    plt.title("Synthetic normal-form illustration: collective attention and epistemic pollution")
    plt.legend(frameon=False)
    plt.grid(alpha=0.25)
    savefig("fig8_collective_attention_pollution")


def main() -> None:
    df = make_candidates()
    fig1_flow()
    fig2_salience_value(df)
    fig3_capacity_sweep(df)
    fig4_verification_burden(df)
    fig5_tunnel_vision()
    fig6_failure_modes()
    fig7_recovery_hysteresis()
    fig8_collective_pollution()


if __name__ == "__main__":
    main()
