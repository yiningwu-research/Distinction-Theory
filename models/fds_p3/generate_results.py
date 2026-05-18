#!/usr/bin/env python3
"""Deterministic normal-form demonstrations for FDS-P3.

The figures are synthetic audits of finite-bath memory, Markovianization,
accessible environmental readout, bath saturation, environmental ledgers, and
P3/P4/P7 regime logic. They are not fitted experimental data.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]
FIG = BASE / "figures"
DATA = BASE / "data"
FIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)


def savefig(name: str) -> None:
    for ext in ("pdf", "png"):
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=220)
    plt.close()


def binary_entropy(p: np.ndarray | float) -> np.ndarray | float:
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def main() -> None:
    # Core parameters
    t = np.linspace(0, 120, 600)
    params = {
        "t_max": 120,
        "n_time_points": len(t),
        "bath_sizes": [16, 64, 256],
        "mixing_rates": [0.018, 0.035, 0.06],
        "record_export_rate": 5.0,
        "finite_bath_capacity": 260.0,
        "task_alphabet_size": 8,
        "residual_entropy_tolerance_h_tol_bits": 0.65,
        "markov_threshold_eta": 0.05,
        "resource_units": "normalized audit units",
        "figures_are": "deterministic normal-form demonstrations, not empirical fits",
    }
    (DATA / "simulation_parameters.json").write_text(json.dumps(params, indent=2))

    # ------------------------------------------------------------------
    # Figure 1: finite bath memory decay and recurrence/backflow
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    fig1 = pd.DataFrame({"time": t})
    for N, lam in zip(params["bath_sizes"], params["mixing_rates"]):
        # Larger baths: more rapid operational dilution but weaker recurrence.
        recurrence_amp = 0.28 * np.sqrt(16 / N)
        omega = 0.15 / np.sqrt(N / 16)
        floor = 0.015 * np.sqrt(16 / N)
        I = np.exp(-lam * t) * (1 + recurrence_amp * np.cos(omega * t) ** 2) + floor
        I = np.clip(I / I[0], 0, 1.05)
        ax.plot(t, I, label=f"N_B={N}, mixing={lam:.3f}")
        fig1[f"I_acc_N{N}"] = I
    ax.set_xlabel("time / update windows")
    ax.set_ylabel(r"accessible inverse information $I_{acc}(t)$ [normalized]")
    ax.set_title("Finite-bath memory decay with finite recurrence")
    ax.axhline(0.2, linestyle="--", linewidth=1, label="recovery threshold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.25)
    fig1.to_csv(DATA / "fig1_finite_bath_memory_decay.csv", index=False)
    savefig("fig1_finite_bath_memory_decay")

    # ------------------------------------------------------------------
    # Figure 2: Markov closure error and history advantage
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    fig2 = pd.DataFrame({"time": t})
    cases = [
        ("fast mixing", 0.08, 0.04, 0.20),
        ("slow mixing", 0.025, 0.08, 0.11),
        ("finite recurrence", 0.018, 0.18, 0.18),
    ]
    for label, lam, amp, omega in cases:
        M = 0.55 * np.exp(-lam * t) + amp * np.exp(-0.008 * t) * (np.sin(omega * t) ** 2)
        M = np.clip(M, 0, None)
        ax.plot(t, M, label=label)
        fig2[label.replace(" ", "_")] = M
    ax.axhline(params["markov_threshold_eta"], linestyle="--", linewidth=1, label=r"operational Markov threshold $\eta$")
    ax.set_xlabel("time / update windows")
    ax.set_ylabel(r"Markov closure error $\mathcal{M}_{env}$ [JS proxy]")
    ax.set_title("Markovianization as loss of accessible bath memory")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.25)
    fig2.to_csv(DATA / "fig2_markov_closure_error.csv", index=False)
    savefig("fig2_markov_closure_error")

    # ------------------------------------------------------------------
    # Figure 3: memory kernels and tail burden
    # ------------------------------------------------------------------
    s = np.linspace(0, 80, 500)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    fig.subplots_adjust(wspace=0.35)
    fig3 = pd.DataFrame({"lag": s})
    for tauB, amp, omega in [(6, 1.0, 0.38), (18, 0.8, 0.22), (40, 0.65, 0.14)]:
        K = amp * np.exp(-s / tauB) * np.cos(omega * s)
        tail = np.array([np.trapz(np.abs(K[i:]), s[i:]) for i in range(len(s))])
        axes[0].plot(s, K, label=fr"$\tau_B={tauB}$")
        axes[1].plot(s, tail, label=fr"$\tau_B={tauB}$")
        fig3[f"K_tau{tauB}"] = K
        fig3[f"tail_tau{tauB}"] = tail
    axes[0].set_title("Finite-bath memory kernels")
    axes[0].set_xlabel("lag")
    axes[0].set_ylabel(r"kernel $K(s)$ [arb.]")
    axes[1].set_title("Unresolved memory tail burden")
    axes[1].set_xlabel("Markov cutoff time")
    axes[1].set_ylabel(r"$\int_T^\infty |K(s)|ds$ [arb.]")
    for a in axes:
        a.grid(True, alpha=0.25)
        a.legend(fontsize=8)
    fig3.to_csv(DATA / "fig3_memory_kernel_burden.csv", index=False)
    savefig("fig3_memory_kernel_burden")

    # ------------------------------------------------------------------
    # Figure 4: side-record recovery probability and conditional entropy
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    fig.subplots_adjust(wspace=0.35)
    readout_strength = np.linspace(0, 1, 300)
    V = params["task_alphabet_size"]
    # Bayes-like recovery model: alpha controls how concentrated the posterior becomes.
    for alpha in [0.8, 1.6, 3.0]:
        p_rec = 1 / V + (1 - 1 / V) * (1 - np.exp(-alpha * readout_strength))
        # Fano-style proxy entropy upper bound from error p_e = 1-p_rec.
        pe = 1 - p_rec
        H_bound = binary_entropy(pe) + pe * np.log2(V - 1)
        axes[0].plot(readout_strength, p_rec, label=fr"readout gain $\alpha={alpha}$")
        axes[1].plot(readout_strength, H_bound, label=fr"$\alpha={alpha}$")
    axes[0].axhline(0.85, linestyle="--", linewidth=1, label="task recovery target")
    axes[0].set_xlabel("accessible readout strength")
    axes[0].set_ylabel(r"Bayes recovery probability $P^E_{rec}$")
    axes[0].set_title("Side-record recovery probability\nimproves with accessible readouts", fontsize=11)
    axes[1].set_xlabel("accessible readout strength")
    axes[1].set_ylabel(r"residual task entropy bound [bits]")
    axes[1].set_title("Residual uncertainty falls\nonly for accessible readouts", fontsize=11)
    for a in axes:
        a.grid(True, alpha=0.25)
        a.legend(fontsize=8)
    pd.DataFrame({"readout_strength": readout_strength}).assign(
        recovery_alpha_08=1/V+(1-1/V)*(1-np.exp(-0.8*readout_strength)),
        recovery_alpha_16=1/V+(1-1/V)*(1-np.exp(-1.6*readout_strength)),
        recovery_alpha_30=1/V+(1-1/V)*(1-np.exp(-3.0*readout_strength)),
    ).to_csv(DATA / "fig4_side_record_recovery.csv", index=False)
    savefig("fig4_side_record_recovery")

    # ------------------------------------------------------------------
    # Figure 5: finite bath saturation and record collisions
    # ------------------------------------------------------------------
    t2 = np.linspace(0, 100, 400)
    C_B = params["finite_bath_capacity"]
    rates = [2.0, 5.0, 9.0]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    fig.subplots_adjust(wspace=0.35)
    fig5 = pd.DataFrame({"time": t2})
    for r in rates:
        ratio = r * t2 / C_B
        collision = np.maximum(0, ratio - 1) ** 1.5
        recovery = np.exp(-0.22 * collision) / (1 + 0.02 * ratio)
        axes[0].plot(t2, ratio, label=fr"export rate $r={r}$")
        axes[1].plot(t2, recovery, label=fr"$r={r}$")
        fig5[f"load_ratio_r{r}"] = ratio
        fig5[f"recovery_r{r}"] = recovery
    axes[0].axhline(1, linestyle="--", linewidth=1, label="capacity threshold")
    axes[0].set_xlabel("time")
    axes[0].set_ylabel(r"exported records / bath capacity")
    axes[0].set_title("Finite-bath record saturation")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("record recovery proxy")
    axes[1].set_title("Collisions and overwrite reduce recoverability")
    for a in axes:
        a.grid(True, alpha=0.25)
        a.legend(fontsize=8)
    fig5.to_csv(DATA / "fig5_finite_bath_saturation.csv", index=False)
    savefig("fig5_finite_bath_saturation")

    # ------------------------------------------------------------------
    # Figure 6: Markovianization window/regime map
    # ------------------------------------------------------------------
    mix = np.linspace(0.0, 1.0, 250)
    access = np.linspace(0.0, 1.0, 250)
    M, A = np.meshgrid(mix, access)
    # Regions: 0 hidden memory, 1 non-Markovian, 2 operational Markovian, 3 recurrence-prone, 4 inaccessible hidden memory.
    score = np.zeros_like(M)
    score[(M < 0.25) & (A > 0.45)] = 1  # accessible history matters: non-Markovian
    score[(M >= 0.25) & (A > 0.35)] = 2  # operational Markovianization
    score[(M < 0.18) & (A < 0.35)] = 3  # small slow bath: recurrence/backflow
    score[(M >= 0.35) & (A < 0.35)] = 4  # hidden/inaccessible memory
    fig, ax = plt.subplots(figsize=(5.6, 4.3))
    im = ax.imshow(score, origin="lower", extent=[0, 1, 0, 1], aspect="auto")
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2, 3, 4])
    cbar.ax.set_yticklabels(["transition", "non-Markov", "Markovianized", "recurrence", "hidden"])
    ax.set_xlabel("bath mixing / dilution strength")
    ax.set_ylabel("accessible readout strength")
    ax.set_title("Operational Markovianization regimes")
    ax.text(0.08, 0.75, "history\nmatters", color="white", fontsize=8)
    ax.text(0.62, 0.70, "operational\nMarkovian", color="white", fontsize=8)
    ax.text(0.08, 0.12, "finite-bath\nrecurrence", color="white", fontsize=8)
    ax.text(0.58, 0.14, "hidden\nrecords", color="white", fontsize=8)
    pd.DataFrame({"mixing": M.ravel(), "readout_strength": A.ravel(), "regime": score.ravel()}).to_csv(DATA / "fig6_markovianization_regimes.csv", index=False)
    savefig("fig6_markovianization_regimes")

    # ------------------------------------------------------------------
    # Figure 7: environmental forgetting ledger
    # ------------------------------------------------------------------
    t3 = np.linspace(0, 80, 260)
    write = 1.8 + 0.04 * t3
    mix_cost = 0.5 + 0.016 * t3 ** 1.25
    monitor = 1.0 + 0.6 * np.exp(-t3 / 28)
    retrieve = 0.8 + 0.018 * t3
    verify = 0.5 + 0.0028 * t3 ** 1.55
    total = write + mix_cost + monitor + retrieve + verify
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    ax.stackplot(t3, write, mix_cost, monitor, retrieve, verify,
                 labels=["write", "mix/isolate", "monitor", "retrieve", "verify"])
    ax.plot(t3, total, linestyle="--", linewidth=1.2, label="coupled environmental ledger")
    ax.set_xlabel("time / update windows")
    ax.set_ylabel("resource / readout ledger [arb.]")
    ax.set_title("Environmental side readouts require a coupled ledger")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.25)
    pd.DataFrame({"time": t3, "write": write, "mix_isolate": mix_cost, "monitor": monitor, "retrieve": retrieve, "verify": verify, "total": total}).to_csv(DATA / "fig7_environmental_ledger.csv", index=False)
    savefig("fig7_environmental_ledger")

    # ------------------------------------------------------------------
    # Figure 8: P3/P4/P7 regime diagram
    # ------------------------------------------------------------------
    env_access = np.linspace(0, 1, 250)
    inv_prot = np.linspace(0, 1, 250)
    EA, IP = np.meshgrid(env_access, inv_prot)
    # 0 P4 internal loss only, 1 P3 env forgetting, 2 environment recovers, 3 P7 invariant protection, 4 overload/collapse
    reg = np.zeros_like(EA)
    reg[(EA < 0.25) & (IP < 0.25)] = 1
    reg[(EA >= 0.45) & (IP < 0.45)] = 2
    reg[(IP >= 0.55)] = 3
    reg[(EA < 0.18) & (IP < 0.18)] = 4
    fig, ax = plt.subplots(figsize=(5.6, 4.3))
    im = ax.imshow(reg, origin="lower", extent=[0, 1, 0, 1], aspect="auto")
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2, 3, 4])
    cbar.ax.set_yticklabels(["P4 loss", "P3 forgetting", "env recovers", "P7 protected", "collapse"])
    ax.set_xlabel("accessible environmental readout strength")
    ax.set_ylabel("invariant / topological protection")
    ax.set_title("P3 between P4 loss and P7 protection")
    ax.text(0.07, 0.08, "collapse /\nrelax", color="white", fontsize=8)
    ax.text(0.05, 0.35, "P3 env\nforgetting", color="white", fontsize=8)
    ax.text(0.60, 0.25, "environment\nrecovers", color="white", fontsize=8)
    ax.text(0.52, 0.75, "P7 invariant\nprotection", color="white", fontsize=8)
    pd.DataFrame({"env_access": EA.ravel(), "invariant_protection": IP.ravel(), "regime": reg.ravel()}).to_csv(DATA / "fig8_p3_p4_p7_regimes.csv", index=False)
    savefig("fig8_p3_p4_p7_regimes")


if __name__ == "__main__":
    main()
