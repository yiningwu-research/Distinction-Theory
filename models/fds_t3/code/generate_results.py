"""Generate deterministic synthetic simulations for FDS-T3 v0.2.

The simulations support the paper:
Capacity Overflow, Effective Stochasticity, and Phase-B Invariants.
They are illustrative deterministic model demonstrations, not fits to
physical, biological, quantum, AI-benchmark, or human-subject data.
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
FIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)


def entropy(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    total = p.sum()
    if total <= 0:
        return 0.0
    p = p / total
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def smooth_derivative(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    dy = np.gradient(y, x)
    # very light smoothing without scipy dependency
    kernel = np.ones(5) / 5
    return np.convolve(dy, kernel, mode="same")


def savefig(name: str) -> None:
    for ext in ["pdf", "png"]:
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=220)
    plt.close()


# -----------------------------------------------------------------------------
# Fig. 1: deterministic hidden dynamics -> stochastic accessible kernels
# -----------------------------------------------------------------------------

def simulation_projection_stochasticity() -> None:
    K = 8   # visible records
    M = 64  # hidden residues per visible record
    states = [(z, h) for z in range(K) for h in range(M)]

    def step(z: int, h: int) -> tuple[int, int]:
        # Deterministic hidden update; visible successor depends on unresolved h.
        h2 = (5 * h + 3 * z + 7) % M
        z2 = (z + (h % K) + 1) % K
        return z2, h2

    rows = []
    for hidden_bits in range(0, 7):
        divisor = 2 ** max(0, 6 - hidden_bits)
        groups: dict[tuple[int, int], list[tuple[int, int]]] = {}
        for z, h in states:
            retained_h = h // divisor if hidden_bits > 0 else 0
            groups.setdefault((z, retained_h), []).append((z, h))
        entropies, loss, predictability = [], [], []
        for obs_state, xs in groups.items():
            targets = [step(z, h)[0] for z, h in xs]
            counts = np.bincount(targets, minlength=K)
            H = entropy(counts)
            entropies.append(H)
            loss.append(math.log2(len(xs)))
            predictability.append(1.0 - H / math.log2(K))
        rows.append({
            "hidden_bits_retained": hidden_bits,
            "capacity_bits": math.log2(K) + hidden_bits,
            "mean_transition_entropy_bits": float(np.mean(entropies)),
            "mean_projection_loss_bits": float(np.mean(loss)),
            "mean_predictability": float(np.mean(predictability)),
        })
    df = pd.DataFrame(rows)
    df.to_csv(DATA / "projection_stochasticity.csv", index=False)

    plt.figure(figsize=(6.4, 3.7))
    plt.plot(df.hidden_bits_retained, df.mean_transition_entropy_bits, marker="o", label="effective transition entropy")
    plt.plot(df.hidden_bits_retained, df.mean_projection_loss_bits, marker="s", label="projection loss H(hidden|record)")
    plt.plot(df.hidden_bits_retained, df.mean_predictability * math.log2(K), marker="^", label="predictability proxy (scaled)")
    plt.xlabel("hidden bits retained by observer")
    plt.ylabel("bits")
    plt.title("Projection-induced stochasticity falls as hidden distinctions are retained")
    plt.legend(fontsize=8)
    savefig("fig1_projection_stochasticity")


# -----------------------------------------------------------------------------
# Fig. 2: critical deficit and predictive susceptibility
# -----------------------------------------------------------------------------

def simulation_critical_deficit() -> None:
    u = np.linspace(0, 100, 220)
    capacity = 44 + 3.5 * np.sin(u / 13.0)
    demand = 18 + 0.54 * u + 0.0011 * u**2
    deficit = demand - capacity
    positive = np.maximum(deficit, 0)
    # Rapid but finite transition near deficit 0.
    transition_entropy = 0.12 + 2.85 * (1.0 / (1.0 + np.exp(-(deficit - 1.5) / 4.8)))
    error_floor = 0.015 + 0.60 * (1.0 / (1.0 + np.exp(-(deficit - 3.0) / 6.5)))
    chi_p = np.abs(smooth_derivative(error_floor, deficit))
    chi_h = np.abs(smooth_derivative(transition_entropy, deficit))

    df = pd.DataFrame({
        "load": u,
        "demand_bits": demand,
        "capacity_bits": capacity,
        "deficit_bits": deficit,
        "transition_entropy_bits": transition_entropy,
        "error_floor": error_floor,
        "predictive_susceptibility": chi_p,
        "entropy_susceptibility": chi_h,
    })
    df.to_csv(DATA / "critical_deficit_susceptibility.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(6.4, 3.8))
    ax1.plot(u, demand, label="task distinction demand")
    ax1.plot(u, capacity, label="accessible capacity")
    ax1.fill_between(u, capacity, demand, where=demand > capacity, alpha=0.14, label="overflow region")
    ax1.set_xlabel("load / environmental complexity")
    ax1.set_ylabel("bits")
    ax2 = ax1.twinx()
    ax2.plot(u, transition_entropy, linestyle="--", label="effective stochasticity")
    ax2.plot(u, chi_p / (chi_p.max() + 1e-9) * 2.0, linestyle=":", label="predictive susceptibility (scaled)")
    ax2.set_ylabel("entropy / susceptibility proxy")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, fontsize=8, loc="upper left")
    plt.title("Critical capacity deficit produces a susceptibility peak")
    savefig("fig2_critical_deficit")


# -----------------------------------------------------------------------------
# Fig. 3: Markov closure and Phase-B invariant selection
# -----------------------------------------------------------------------------

def simulation_markov_closure_selection() -> None:
    cycles = np.arange(0, 80)
    candidates = {
        "microstate detail": {"I0": 7.0, "tau": 18, "cost": 6.5, "markov": 1.2},
        "local coarse feature": {"I0": 4.0, "tau": 32, "cost": 2.5, "markov": 0.55},
        "Phase-B invariant": {"I0": 2.6, "tau": 180, "cost": 0.9, "markov": 0.08},
        "wrong invariant": {"I0": 2.0, "tau": 80, "cost": 0.55, "markov": 0.75},
    }
    rows = []
    for name, p in candidates.items():
        info = p["I0"] * np.exp(-cycles / p["tau"])
        closure_error = p["markov"] * (0.6 + 0.4 * np.exp(-cycles / 45.0))
        update_cost = p["cost"] * (0.8 + 0.2 * np.sin(cycles / 18.0) ** 2)
        survival_score = info / (update_cost + 1.6 * closure_error + 0.15)
        for c, I, m, cost, score in zip(cycles, info, closure_error, update_cost, survival_score):
            rows.append({
                "cycle": int(c),
                "candidate": name,
                "retained_information_bits": float(I),
                "markov_closure_error_bits": float(m),
                "update_cost_units": float(cost),
                "survival_score": float(score),
            })
    df = pd.DataFrame(rows)
    df.to_csv(DATA / "markov_closure_selection.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(6.4, 3.8))
    for name in candidates:
        sub = df[df.candidate == name]
        if name == "Phase-B invariant":
            ax1.plot(sub.cycle, sub.survival_score, linewidth=2.5, label=name)
        else:
            ax1.plot(sub.cycle, sub.survival_score, label=name)
    ax1.set_xlabel("projection / update cycle")
    ax1.set_ylabel("survival score")
    ax2 = ax1.twinx()
    sub_inv = df[df.candidate == "Phase-B invariant"]
    sub_micro = df[df.candidate == "microstate detail"]
    ax2.plot(sub_inv.cycle, sub_inv.markov_closure_error_bits, linestyle="--", label="invariant Markov error")
    ax2.plot(sub_micro.cycle, sub_micro.markov_closure_error_bits, linestyle=":", label="microstate Markov error")
    ax2.set_ylabel("Markov closure error")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, fontsize=7, loc="upper right")
    plt.title("Phase-B invariants minimize update cost and Markov closure error")
    savefig("fig3_markov_closure_selection")


# -----------------------------------------------------------------------------
# Fig. 4: informational hysteresis after capacity recovery
# -----------------------------------------------------------------------------

def simulation_hysteresis() -> None:
    t = np.linspace(0, 140, 240)
    demand = 43 + 19 * np.exp(-((t - 58) / 19) ** 2)
    capacity = 51 - 17 * np.exp(-((t - 58) / 24) ** 2)
    deficit = np.maximum(demand - capacity, 0)
    recovered_margin = np.maximum(capacity - demand, 0)
    loss_no_log = np.zeros_like(t)
    loss_with_log = np.zeros_like(t)
    pruned_state_fraction = np.zeros_like(t)
    for i in range(1, len(t)):
        dt = t[i] - t[i - 1]
        loss_no_log[i] = loss_no_log[i - 1] + 0.075 * deficit[i] * dt - 0.0025 * recovered_margin[i] * dt
        loss_no_log[i] = max(loss_no_log[i], 0)
        loss_with_log[i] = loss_with_log[i - 1] + 0.030 * deficit[i] * dt - 0.028 * recovered_margin[i] * dt
        loss_with_log[i] = max(loss_with_log[i], 0)
        pruned_state_fraction[i] = 1 - np.exp(-loss_no_log[i] / 30.0)
    df = pd.DataFrame({
        "time": t,
        "demand_bits": demand,
        "capacity_bits": capacity,
        "deficit_bits": deficit,
        "irrecoverable_loss_no_external_log": loss_no_log,
        "loss_with_external_log": loss_with_log,
        "pruned_state_fraction": pruned_state_fraction,
    })
    df.to_csv(DATA / "informational_hysteresis.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(6.4, 3.8))
    ax1.plot(t, demand, label="demand")
    ax1.plot(t, capacity, label="capacity")
    ax1.fill_between(t, capacity, demand, where=demand > capacity, alpha=0.13, label="overflow")
    ax1.set_xlabel("time")
    ax1.set_ylabel("bits")
    ax2 = ax1.twinx()
    ax2.plot(t, loss_no_log, linestyle="--", label="irrecoverable loss, no log")
    ax2.plot(t, loss_with_log, linestyle=":", label="loss with external log")
    ax2.plot(t, pruned_state_fraction * max(loss_no_log.max(), 1), linestyle="-.", label="pruned state fraction (scaled)")
    ax2.set_ylabel("lost distinctions / scaled pruning")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, fontsize=7, loc="upper right")
    plt.title("Capacity recovery restores storage, not discarded distinctions")
    savefig("fig4_informational_hysteresis")


# -----------------------------------------------------------------------------
# Fig. 5: observer hierarchy and capacity-relative stochasticity
# -----------------------------------------------------------------------------

def simulation_observer_hierarchy() -> None:
    hidden_bits = np.arange(0, 9)
    kernel_entropy = 2.9 * np.exp(-hidden_bits / 3.0) + 0.08
    projection_loss = np.maximum(8 - hidden_bits, 0)
    deterministic_fraction = 1 - kernel_entropy / kernel_entropy[0]
    instrument_generation = hidden_bits / hidden_bits.max()
    df = pd.DataFrame({
        "retained_hidden_bits": hidden_bits,
        "transition_entropy_bits": kernel_entropy,
        "projection_loss_bits": projection_loss,
        "deterministic_fraction_proxy": deterministic_fraction,
        "instrument_generation_proxy": instrument_generation,
    })
    df.to_csv(DATA / "observer_hierarchy.csv", index=False)

    plt.figure(figsize=(6.4, 3.7))
    plt.plot(hidden_bits, kernel_entropy, marker="o", label="apparent stochasticity")
    plt.plot(hidden_bits, projection_loss, marker="s", label="projection loss")
    plt.plot(hidden_bits, deterministic_fraction * projection_loss.max(), marker="^", label="deterministic structure recovered (scaled)")
    plt.xlabel("hidden distinctions retained by observer")
    plt.ylabel("bits / scaled proxy")
    plt.title("Randomness can shrink as observer capacity increases")
    plt.legend(fontsize=8)
    savefig("fig5_observer_hierarchy")


# -----------------------------------------------------------------------------
# Fig. 6: Phase-A/B transition with invariant and susceptibility
# -----------------------------------------------------------------------------

def simulation_phase_transition() -> None:
    u = np.linspace(0, 1, 220)
    capacity = 0.74 - 0.30 * u + 0.035 * np.sin(5 * np.pi * u)
    demand = 0.24 + 0.66 * u
    deficit = demand - capacity
    phase_b = 1 / (1 + np.exp(-34 * deficit))
    micro_error = 0.035 + 0.78 * phase_b
    invariant_error = 0.04 + 0.10 * phase_b
    stochasticity = 0.10 + 1.85 * phase_b
    chi = np.abs(smooth_derivative(stochasticity, deficit))
    df = pd.DataFrame({
        "control_parameter": u,
        "capacity": capacity,
        "demand": demand,
        "deficit": deficit,
        "phaseB_index": phase_b,
        "microstate_error": micro_error,
        "invariant_error": invariant_error,
        "effective_stochasticity": stochasticity,
        "critical_susceptibility": chi,
    })
    df.to_csv(DATA / "phase_transition.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(6.4, 3.8))
    ax1.plot(u, demand, label="distinction demand")
    ax1.plot(u, capacity, label="accessible capacity")
    ax1.plot(u, phase_b, label="Phase-B index")
    ax1.set_xlabel("control parameter")
    ax1.set_ylabel("normalized demand / capacity / phase")
    ax2 = ax1.twinx()
    ax2.plot(u, micro_error, linestyle="--", label="microstate error")
    ax2.plot(u, invariant_error, linestyle=":", label="invariant error")
    ax2.plot(u, chi / (chi.max() + 1e-9), linestyle="-.", label="critical susceptibility")
    ax2.set_ylabel("error / susceptibility proxy")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, fontsize=7, loc="upper left")
    plt.title("Phase-A to Phase-B transition under capacity overflow")
    savefig("fig6_phase_transition")


# -----------------------------------------------------------------------------
# Fig. 7: semantic drift / wrong invariant completion under context overflow
# -----------------------------------------------------------------------------

def simulation_semantic_drift() -> None:
    tokens = np.linspace(0, 80000, 220)
    window = 20000
    task_history = 0.75 * tokens + 2500 * np.log1p(tokens / 9000)
    overflow = np.maximum(task_history - window, 0)
    exact_context = np.minimum(task_history, window)
    retrieved_external = 0.55 * overflow * (1 - np.exp(-overflow / 22000))
    lost_without_rag = overflow
    lost_with_rag = np.maximum(overflow - retrieved_external, 0)
    semantic_drift = 1 - np.exp(-lost_without_rag / 26000)
    wrong_invariant_completion = 1 - np.exp(-lost_without_rag / 38000)
    rag_drift = 1 - np.exp(-lost_with_rag / 26000)
    df = pd.DataFrame({
        "tokens_processed": tokens,
        "task_history_demand": task_history,
        "exact_context_capacity": np.full_like(tokens, window),
        "exact_context_retained": exact_context,
        "lost_order_without_external_memory": lost_without_rag,
        "lost_order_with_external_memory": lost_with_rag,
        "semantic_drift_proxy": semantic_drift,
        "wrong_invariant_completion_proxy": wrong_invariant_completion,
        "rag_drift_proxy": rag_drift,
    })
    df.to_csv(DATA / "semantic_drift_context_overflow.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(6.4, 3.8))
    ax1.plot(tokens, task_history, label="task history demand")
    ax1.plot(tokens, np.full_like(tokens, window), label="exact context capacity")
    ax1.plot(tokens, lost_without_rag, linestyle="--", label="lost preimage distinctions")
    ax1.plot(tokens, lost_with_rag, linestyle=":", label="loss after external retrieval")
    ax1.set_xlabel("tokens / updates processed")
    ax1.set_ylabel("bits or tokens proxy")
    ax2 = ax1.twinx()
    ax2.plot(tokens, semantic_drift, linestyle="-.", label="semantic drift proxy")
    ax2.plot(tokens, wrong_invariant_completion, linestyle=(0, (3, 1, 1, 1)), label="wrong invariant completion")
    ax2.plot(tokens, rag_drift, linestyle=(0, (5, 2)), label="drift with external memory")
    ax2.set_ylabel("dimensionless proxy")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, fontsize=7, loc="upper left")
    plt.title("Context overflow can create semantic drift and wrong invariant completion")
    savefig("fig7_semantic_drift")


def main() -> None:
    simulation_projection_stochasticity()
    simulation_critical_deficit()
    simulation_markov_closure_selection()
    simulation_hysteresis()
    simulation_observer_hierarchy()
    simulation_phase_transition()
    simulation_semantic_drift()
    print(f"Wrote figures to {FIG}")
    print(f"Wrote data to {DATA}")


if __name__ == "__main__":
    main()
