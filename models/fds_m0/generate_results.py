#!/usr/bin/env python3
"""
Generate deterministic synthetic normal-form illustrations for FDS-M0 v0.2.
These figures are not empirical evidence. They visualize definitions and
failure modes introduced in the paper.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures")
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
RNG = np.random.default_rng(20260517)


def savefig(name):
    for ext in ("png", "pdf"):
        plt.savefig(os.path.join(FIG_DIR, f"{name}.{ext}"), bbox_inches="tight", dpi=190)
    plt.close()


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def fig1_constraint_pyramid():
    layers = [
        ("Culture", "shared externalized\nverification"),
        ("Agency", "closed-loop\nupdate control"),
        ("Meaning", "actionable semantic\nquotient"),
        ("Goal", "stable policy\norientation"),
        ("Value", "boundary-gradient\nranking"),
        ("Attention", "capacity-limited\nadmission"),
        ("Record", "maintained\ndistinction"),
        ("Distinction", "separate\nalternatives"),
    ]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axis("off")
    base_y = 0.05
    height = 0.095
    for i, (name, desc) in enumerate(reversed(layers)):
        y = base_y + i * height
        width = 0.94 - i * 0.075
        x0 = 0.5 - width / 2
        ax.add_patch(plt.Rectangle((x0, y), width, height * 0.82, fill=False, lw=1.2))
        ax.text(0.5, y + height * 0.55, name, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(0.5, y + height * 0.23, desc, ha="center", va="center", fontsize=8)
    ax.text(0.5, 0.94, "Agency-semantics constraint pyramid", ha="center", fontsize=14, fontweight="bold")
    ax.text(0.5, 0.90, "Higher layers require stronger memory, verification, stability, and resource budgets.", ha="center", fontsize=9)
    ax.annotate("increasing budget demand", xy=(1.0, 0.80), xytext=(1.0, 0.20),
                arrowprops=dict(arrowstyle="->", lw=1.1), rotation=90, va="center", ha="center")
    savefig("fig1_constraint_pyramid")


def simulate_distinctions(n=180):
    novelty = RNG.gamma(2.0, 0.65, n)
    threat = RNG.beta(2.0, 4.8, n)
    affordance = RNG.beta(2.3, 2.1, n)
    verification = RNG.gamma(1.7, 0.38, n) + 0.06
    maintenance = RNG.gamma(1.4, 0.32, n) + 0.04
    salience_noise = RNG.beta(1.8, 2.2, n)
    cost = verification + maintenance
    # boundary-gradient value: expected maintenance loss reduction + collapse-risk reduction - cost
    risk_reduction = 1.7 * threat**2 + 0.35 * threat * novelty
    average_loss_reduction = 0.8 * affordance + 0.6 * threat + 0.25 * novelty
    value_causal = average_loss_reduction + 0.55 * risk_reduction - 0.52 * cost
    salience = 0.65 * novelty + 0.25 * salience_noise + 0.1 * threat
    df = pd.DataFrame({
        "id": np.arange(n),
        "novelty": novelty,
        "threat": threat,
        "affordance": affordance,
        "verification_cost": verification,
        "maintenance_cost": maintenance,
        "cost": cost,
        "risk_reduction": risk_reduction,
        "avg_loss_reduction": average_loss_reduction,
        "causal_value": value_causal,
        "salience": salience,
        "value_density": value_causal / (cost + 1e-9),
    })
    return df


def fig2_attention_gate():
    df = simulate_distinctions()
    df.to_csv(os.path.join(DATA_DIR, "distinction_stream.csv"), index=False)
    deficits = [0.0, 0.45, 0.9]
    rows = []
    for Delta in deficits:
        beta = 3.0 + 7.0 * Delta
        score = df["causal_value"].values + 0.55 * df["novelty"].values * Delta - 0.7 * df["cost"].values
        p = sigmoid(beta * (score - np.quantile(score, 0.68)))
        admitted = p > 0.55
        for i, pr, adm in zip(df["id"], p, admitted):
            rows.append({"id": i, "semantic_deficit": Delta, "admission_probability": pr, "admitted": int(adm)})
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(DATA_DIR, "attention_gate_nonlinear.csv"), index=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    x_fine = np.linspace(-3, 3, 200)
    colors = ["#2ecc71", "#f39c12", "#e74c3c"]
    labels = ["low deficit (broad admission)", "medium deficit (sharper gate)", "high deficit (tunnel vision)"]
    for Delta, color, label in zip(deficits, colors, labels):
        beta_eff = 3.0 + 7.0 * Delta
        p_curve = sigmoid(beta_eff * x_fine)
        ax.plot(x_fine, p_curve, color=color, lw=2.5, label=label)
    ax.set_xlabel("composite value-novelty-cost score (standardized)")
    ax.set_ylabel("admission probability $P(\\operatorname{admit}(d))$")
    ax.set_title("Synthetic normal-form illustration: sigmoid admission curves and tunnel vision")
    ax.legend(frameon=False, fontsize=9)
    savefig("fig2_attention_gate")


def fig3_boundary_gradient_value():
    df = simulate_distinctions()
    df = df.sort_values("value_density", ascending=False).reset_index(drop=True)
    capacity = 26.0
    cum_cost = df["cost"].cumsum()
    df["admitted_by_budget"] = (cum_cost <= capacity) & (df["causal_value"] > 0)
    df.to_csv(os.path.join(DATA_DIR, "boundary_gradient_value.csv"), index=False)
    fig, ax1 = plt.subplots(figsize=(9, 5))
    x = np.arange(len(df))
    ax1.plot(x, df["causal_value"], label="causal boundary value")
    ax1.plot(x, df["risk_reduction"], linestyle="--", label="collapse-risk reduction")
    ax1.set_xlabel("candidate distinctions sorted by value density")
    ax1.set_ylabel("value terms")
    ax2 = ax1.twinx()
    ax2.plot(x, cum_cost, linestyle=":", label="cumulative admission cost")
    ax2.axhline(capacity, lw=1.1, linestyle="-.", label="attention budget")
    ax2.set_ylabel("cumulative cost")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, frameon=False, loc="upper right")
    ax1.set_title("Synthetic normal-form illustration: value as boundary-gradient ranking")
    savefig("fig3_boundary_value")


def fig4_semantic_capacity():
    demand = np.linspace(20, 140, 121)
    caps = [45, 70, 95]
    rows = []
    for c in caps:
        deficit = np.maximum(demand - c, 0)
        meaning_retained = 1.0 - 0.78 * sigmoid((deficit - 18) / 6.5)
        tunnel = sigmoid((deficit - 12) / 5.5)
        false_compression = sigmoid((deficit - 24) / 6.0)
        for d, de, mr, tv, fc in zip(demand, deficit, meaning_retained, tunnel, false_compression):
            rows.append({"semantic_demand": d, "capacity": c, "deficit": de,
                         "meaning_retained": mr, "tunnel_vision": tv, "false_compression": fc})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "semantic_capacity_collapse.csv"), index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    for c in caps:
        sub = df[df["capacity"] == c]
        ax.plot(sub["semantic_demand"], sub["meaning_retained"], label=f"C_sem={c}")
    ax.set_xlabel("semantic task demand")
    ax.set_ylabel("actionable meaning retained")
    ax.set_title("Synthetic normal-form illustration: semantic capacity deficit and collapse")
    ax.legend(frameon=False)
    savefig("fig4_semantic_capacity")


def fig5_quotient_compression():
    q = np.linspace(0, 1, 151)
    maintenance = 1.1 - 0.9 * q + 0.1 * q**2
    # policy loss remains small while quotient is task-sufficient, then jumps at over-compression.
    policy_loss = 0.06 + 0.05 * q + 1.6 * sigmoid((q - 0.67) / 0.045)
    context_robustness = 1.0 - 0.1 * q - 0.82 * sigmoid((q - 0.76) / 0.055)
    total = maintenance + 0.85 * policy_loss + 0.35 * (1 - context_robustness)
    q_star = q[np.argmin(total)]
    df = pd.DataFrame({"quotient_strength": q, "maintenance_cost": maintenance,
                       "policy_loss": policy_loss, "context_robustness": context_robustness,
                       "total_objective": total})
    df.to_csv(os.path.join(DATA_DIR, "semantic_quotient_tradeoff.csv"), index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(q, maintenance, label="maintenance cost")
    ax.plot(q, policy_loss, label="policy error")
    ax.plot(q, total, label="total objective")
    ax.axvline(q_star, linestyle="--", lw=1.2, label=f"q*={q_star:.2f}")
    ax.axvspan(0.70, 1.0, alpha=0.12, label="over-compression")
    ax.set_xlabel("semantic quotient strength")
    ax.set_ylabel("normalized cost")
    ax.set_title("Synthetic normal-form illustration: policy-preserving semantic quotient")
    ax.legend(frameon=False)
    savefig("fig5_semantic_quotient")


def fig6_goal_stability():
    T = 100
    t = np.arange(T)
    perturb = np.zeros(T)
    perturb[35:55] = 1.0
    # goal-like policy recovers; reflex policy changes immediately with perturbation.
    stable = 0.82 - 0.18 * sigmoid((t - 35) / 2.0) + 0.15 * sigmoid((t - 55) / 3.0)
    stable += 0.03 * np.sin(t / 9)
    reflex = 0.82 - 0.62 * perturb + 0.04 * RNG.normal(size=T)
    commitment = 0.9 - 0.08 * sigmoid((t - 36) / 4) + 0.05 * sigmoid((t - 60) / 5)
    df = pd.DataFrame({"time": t, "perturbation": perturb, "goal_like_GSI": stable,
                       "reflex_GSI": reflex, "commitment_GSI": commitment})
    df.to_csv(os.path.join(DATA_DIR, "goal_stability_index.csv"), index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(t, stable, label="goal-like policy")
    ax.plot(t, reflex, label="reflexive response")
    ax.plot(t, commitment, label="commitment-like policy")
    ax.fill_between(t, 0, perturb, alpha=0.08, label="perturbation window")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("time")
    ax.set_ylabel("Goal-stability index")
    ax.set_title("Synthetic normal-form illustration: goal stability under perturbation")
    ax.legend(frameon=False)
    savefig("fig6_goal_stability")


def fig7_agency_boundary_verification():
    T = 90
    t = np.arange(T)
    disturbance = 0.5 + 0.22 * np.sin(t / 8) + RNG.normal(0, 0.035, T)
    disturbance = np.maximum(disturbance, 0.05)

    def rollout(mode):
        loss = np.zeros(T); verify = np.zeros(T); resource = np.zeros(T)
        loss[0] = 0.6; resource[0] = 1.0; verify[0] = 0.2
        for k in range(1, T):
            if mode == "self_verifying_agent":
                action = 0.75 * loss[k-1] + 0.20 * disturbance[k]
                verify[k] = 0.55 * verify[k-1] + 0.25 * abs(loss[k-1] - loss[k-2] if k > 1 else 0.0)
                external = 0.0
            elif mode == "coupled_agent_host_verifies":
                action = 0.68 * loss[k-1] + 0.18 * disturbance[k]
                verify[k] = 0.08
                external = 0.18
            elif mode == "bare_mapper":
                action = 0.22 * disturbance[k]
                verify[k] = 0.02
                external = 0.0
            else:
                action = 0.0; external = 0.0
            v_cost = 0.06 * verify[k] + external
            resource[k] = np.clip(resource[k-1] + 0.025 - 0.045 * action**2 - v_cost, 0, 1.2)
            loss[k] = np.clip(0.70 * loss[k-1] + disturbance[k] - 0.82 * action + 0.09 * (1 - resource[k]), 0, 1.8)
        return pd.DataFrame({"time": t, "mode": mode, "boundary_loss": loss, "verification_load": verify, "resource": resource})

    df = pd.concat([rollout(m) for m in ["self_verifying_agent", "coupled_agent_host_verifies", "bare_mapper"]])
    df.to_csv(os.path.join(DATA_DIR, "agency_boundary_verification.csv"), index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    for mode in df["mode"].unique():
        sub = df[df["mode"] == mode]
        ax.plot(sub["time"], sub["boundary_loss"], label=mode.replace("_", " "))
    ax.set_xlabel("time")
    ax.set_ylabel("boundary-maintenance loss")
    ax.set_title("Synthetic normal-form illustration: agency boundary sensitivity and verification load")
    ax.legend(frameon=False)
    savefig("fig7_agency_verification")


def fig8_misalignment_pollution():
    actions = np.arange(8)
    base = 0
    host_effect = np.array([0, -0.35, -0.25, 0.15, 0.42, -0.10, 0.30, 0.05])
    delegate_aligned = np.array([0, -0.28, -0.20, 0.12, 0.31, -0.08, 0.24, 0.04])
    delegate_misaligned = np.array([0, 0.25, 0.20, -0.08, -0.33, 0.06, -0.22, -0.03])

    def align(a, b):
        aa = a[1:] - a[base]
        bb = b[1:] - b[base]
        return float(np.dot(aa, bb) / (np.linalg.norm(aa) * np.linalg.norm(bb)))

    A_aligned = align(host_effect, delegate_aligned)
    A_mis = align(host_effect, delegate_misaligned)
    df = pd.DataFrame({"action": actions, "host_effect": host_effect,
                       "delegate_aligned_effect": delegate_aligned,
                       "delegate_misaligned_effect": delegate_misaligned})
    df.to_csv(os.path.join(DATA_DIR, "misalignment_finite_difference.csv"), index=False)

    t = np.arange(80)
    pollution = 0.1 + 0.015 * t + 0.002 * np.maximum(t - 40, 0)**2
    verify_cap = 1.2 + 0.12 * np.sin(t / 9)
    saturation = pollution / verify_cap
    false_compression = sigmoid((saturation - 1.05) / 0.08)
    ep = pd.DataFrame({"time": t, "verification_demand": pollution,
                       "verification_capacity": verify_cap, "saturation_ratio": saturation,
                       "false_compression": false_compression})
    ep.to_csv(os.path.join(DATA_DIR, "epistemic_pollution_saturation.csv"), index=False)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(actions, host_effect, marker="o", label="host loss effect")
    axes[0].plot(actions, delegate_aligned, marker="s", label=f"aligned delegate A={A_aligned:.2f}")
    axes[0].plot(actions, delegate_misaligned, marker="^", label=f"misaligned delegate A={A_mis:.2f}")
    axes[0].axhline(0, lw=1, linestyle="--")
    axes[0].set_xlabel("discrete action")
    axes[0].set_ylabel("finite-difference effect on loss")
    axes[0].set_title("Normalized action-effect alignment")
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].plot(t, saturation, label="verification saturation")
    axes[1].plot(t, false_compression, label="false compression risk")
    axes[1].axhline(1, lw=1, linestyle="--", label="capacity threshold")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("normalized level")
    axes[1].set_title("Epistemic pollution as verification bandwidth saturation")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("Synthetic normal-form illustration: misalignment and epistemic pollution", y=1.03)
    savefig("fig8_misalignment_pollution")


def main():
    fig1_constraint_pyramid()
    fig2_attention_gate()
    fig3_boundary_gradient_value()
    fig4_semantic_capacity()
    fig5_quotient_compression()
    fig6_goal_stability()
    fig7_agency_boundary_verification()
    fig8_misalignment_pollution()
    print(f"Generated figures in {FIG_DIR} and data in {DATA_DIR}")


if __name__ == "__main__":
    main()
