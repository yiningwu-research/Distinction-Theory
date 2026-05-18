#!/usr/bin/env python3
"""
Synthetic demonstrations for FDS-P4 v1.1:
Coarse-Grained Anti-Recurrence and Informational Hysteresis in Finite Memory Systems.

The script generates deterministic illustrative figures and CSV tables.
No empirical, proprietary, biological, human-subject, medical, device, or organizational data are used.
"""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
TAB = ROOT / "tables"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "figure.dpi": 150,
})


def savefig(name: str) -> None:
    for ext in ("pdf", "png"):
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight")
    plt.close()


def safe_entropy(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    def kl(a, b):
        mask = a > 0
        return float(np.sum(a[mask] * np.log2(a[mask] / b[mask])))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def fig1_preimage_recovery_bound() -> None:
    """Recovery bound: P_rec* = E_Z max_x p(x|Z), uniform fiber gives 2^-H."""
    n = 16
    retained = np.arange(0, n + 1)
    h_uniform = n - retained
    p_uniform = 2.0 ** (-h_uniform)
    # A non-uniform fiber model: one dominant preimage concentration increases with retained bits.
    concentration = 0.10 + 0.85 * (retained / n) ** 1.7
    p_nonuniform = np.maximum(p_uniform, concentration)
    df = pd.DataFrame({
        "retained_bits": retained,
        "uniform_preimage_entropy_bits": h_uniform,
        "uniform_exact_recovery_bound": p_uniform,
        "nonuniform_exact_recovery_bound": p_nonuniform,
    })
    df.to_csv(TAB / "fig1_preimage_recovery_bound.csv", index=False)

    plt.figure(figsize=(3.55, 2.55))
    plt.semilogy(retained, p_uniform, marker="o", label="uniform fiber $2^{-H(X|Z)}$")
    plt.semilogy(retained, p_nonuniform, marker="s", label=r"non-uniform Bayes bound")
    plt.xlabel("retained coarse bits $k$")
    plt.ylabel(r"best exact recovery probability $P^*_{rec}$")
    plt.title("Preimage recovery bound after truncation")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(loc="best")
    savefig("fig1_preimage_recovery_bound")


def fig2_capacity_hysteresis() -> None:
    n = 16
    t = np.arange(0, 120)
    C = np.full_like(t, 14, dtype=float)
    C[(t >= 35) & (t < 75)] = 6
    C[t >= 75] = 14
    overload = np.maximum(n - C, 0)
    H_no_log = np.maximum.accumulate(overload)
    H_partial = np.maximum.accumulate(np.maximum(overload - 4, 0))
    H_full = np.zeros_like(t, dtype=float)
    df = pd.DataFrame({
        "t": t,
        "capacity_bits": C,
        "overload_bits": overload,
        "H_no_log": H_no_log,
        "H_partial_log": H_partial,
        "H_full_log": H_full,
    })
    df.to_csv(TAB / "fig2_capacity_hysteresis.csv", index=False)

    plt.figure(figsize=(3.6, 2.65))
    plt.plot(t, C, label="capacity $C_t$")
    plt.plot(t, H_no_log, label="$H_{irr}$ no side record")
    plt.plot(t, H_partial, label="$H_{irr}$ partial side record")
    plt.plot(t, H_full, label="$H_{irr}$ full inverse record")
    plt.xlabel("time step")
    plt.ylabel("bits")
    plt.title("Capacity recovery is not distinction recovery")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    savefig("fig2_capacity_hysteresis")


def fig3_externalization_breakeven() -> None:
    D = 12.0  # erased inverse bits
    l_ext = np.linspace(0, D, 120)
    h_res = np.maximum(D - l_ext, 0.0)
    c_internal_recover = 0.55 * D**2 * np.ones_like(l_ext)  # cost of reconstructing internally by re-exploration
    c_write = 0.25 * l_ext
    c_sync = 0.055 * l_ext**2
    c_verify = 0.035 * l_ext**2
    c_retrieve = 0.15 * l_ext
    c_ext = c_write + c_sync + c_verify + c_retrieve
    pi_ext = c_internal_recover - c_ext
    total = h_res + 0.12 * c_ext
    idx = np.argmin(np.abs(pi_ext))
    df = pd.DataFrame({
        "external_inverse_bits": l_ext,
        "residual_inverse_uncertainty": h_res,
        "external_cost": c_ext,
        "internal_reconstruction_cost": c_internal_recover,
        "externalization_surplus": pi_ext,
        "record_equivalent_total_burden": total,
    })
    df.to_csv(TAB / "fig3_externalization_breakeven.csv", index=False)

    plt.figure(figsize=(3.6, 2.65))
    plt.plot(l_ext, c_ext, label="external ledger cost")
    plt.plot(l_ext, c_internal_recover, label="internal re-acquisition cost")
    plt.plot(l_ext, total, label="residual + weighted ledger")
    plt.axvline(l_ext[idx], linestyle="--", alpha=0.7, label="break-even region")
    plt.xlabel("side-record inverse information [bits]")
    plt.ylabel("cost / record-equivalent burden")
    plt.title("Externalization break-even audit")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    savefig("fig3_externalization_breakeven")


def fig4_mori_zwanzig_kernel() -> None:
    """Stylized memory-kernel burden from hidden eliminated degrees of freedom."""
    s = np.arange(0, 60)
    hidden_dims = np.array([1, 2, 4, 8])
    rows = []
    plt.figure(figsize=(3.6, 2.65))
    for d in hidden_dims:
        rho = 0.72 + 0.025 * np.log2(d)
        amp = 0.18 * d
        K = amp * rho ** s
        for si, ki in zip(s, K):
            rows.append({"lag": si, "hidden_dimensions": d, "kernel_norm": ki, "rho": rho})
        plt.plot(s, K, label=f"hidden dims={d}")
    pd.DataFrame(rows).to_csv(TAB / "fig4_mori_zwanzig_kernel.csv", index=False)
    plt.xlabel("lag $s$")
    plt.ylabel(r"memory-kernel norm proxy $\|K(s)\|$")
    plt.title("Projection leaves memory-kernel burden")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    savefig("fig4_mori_zwanzig_kernel")


def random_markov(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    A = rng.gamma(shape=1.1, scale=1.0, size=(n, n))
    # Add weak banded structure so coarse partitions matter.
    for i in range(n):
        A[i, i] += 4.0
        A[i, (i + 1) % n] += 2.0
        A[i, (i - 1) % n] += 1.0
    return A / A.sum(axis=1, keepdims=True)


def js_markov_closure_error(P: np.ndarray, labels: np.ndarray) -> float:
    unique = np.unique(labels)
    proj = np.zeros((len(labels), len(unique)))
    for j, lab in enumerate(unique):
        proj[:, j] = P[:, labels == lab].sum(axis=1)
    errs = []
    for lab in unique:
        rows = proj[labels == lab]
        if len(rows) > 1:
            m = rows.mean(axis=0)
            for r in rows:
                errs.append(js_divergence(r, m))
    return float(np.mean(errs)) if errs else 0.0


def fig5_js_markov_closure() -> None:
    n = 64
    P = random_markov(n, 11)
    m_values = np.array([2, 4, 8, 16, 32, 64])
    errors = []
    memory_burden = []
    for m in m_values:
        labels = np.arange(n) % m
        errors.append(js_markov_closure_error(P, labels))
        memory_burden.append(math.log2(m))
    df = pd.DataFrame({
        "coarse_classes": m_values,
        "coarse_memory_bits": memory_burden,
        "js_markov_closure_error_bits": errors,
    })
    df.to_csv(TAB / "fig5_js_markov_closure.csv", index=False)

    plt.figure(figsize=(3.55, 2.55))
    plt.plot(memory_burden, errors, marker="o")
    plt.xlabel(r"coarse memory capacity $\log_2 |Z|$")
    plt.ylabel(r"JS closure error $\mathcal{M}_{JS}(T)$ [bits]")
    plt.title("Non-lumpable projections carry hidden memory")
    plt.grid(True, alpha=0.3)
    savefig("fig5_js_markov_closure")


def fig6_benign_malignant_hysteresis() -> None:
    H = np.linspace(0, 12, 100)
    relevance = {
        "benign, low task relevance": 0.12,
        "mixed relevance": 0.45,
        "malignant, high task relevance": 0.85,
    }
    rows = []
    plt.figure(figsize=(3.6, 2.65))
    for label, r in relevance.items():
        loss = r * H
        for hi, li in zip(H, loss):
            rows.append({"residual_hysteresis_bits": hi, "task_relevance": r,
                         "task_loss": li, "regime": label})
        plt.plot(H, loss, label=label)
    pd.DataFrame(rows).to_csv(TAB / "fig6_benign_malignant_hysteresis.csv", index=False)
    plt.xlabel(r"residual hysteresis $H_{irr}$ [bits]")
    plt.ylabel("task loss proxy")
    plt.title("Benign versus malignant hysteresis")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    savefig("fig6_benign_malignant_hysteresis")


def fig7_phase_b_selection() -> None:
    rng = np.random.default_rng(14)
    n = 140
    predictive = rng.uniform(0.03, 1.0, n)
    update = rng.uniform(0.04, 1.25, n)
    maintenance = rng.uniform(0.04, 1.15, n)
    closure = rng.uniform(0.0, 0.95, n)
    lam = 1.0
    burden = update + maintenance + lam * closure
    score = predictive / (burden + 0.05)
    top = score >= np.quantile(score, 0.86)
    df = pd.DataFrame({"predictive_information": predictive, "update_cost": update,
                       "maintenance_cost": maintenance, "js_closure_error": closure,
                       "burden": burden, "survival_score": score,
                       "phase_b_candidate": top.astype(int)})
    df.to_csv(TAB / "fig7_phase_b_selection.csv", index=False)

    plt.figure(figsize=(3.55, 2.6))
    plt.scatter(burden, predictive, s=18, alpha=0.75, label="candidate variable")
    plt.scatter(burden[top], predictive[top], s=30, marker="x", label="Phase-B candidate")
    plt.xlabel("update + maintenance + closure burden")
    plt.ylabel(r"predictive persistence $I(\phi_t;\phi_{t+\tau})$")
    plt.title("Low-cost predictive survivors")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    savefig("fig7_phase_b_selection")


def fig8_p7_bridge() -> None:
    gamma = np.linspace(0, 1.0, 120)
    gamma_c = 0.62
    # Unprotected distinction progressively loses inverse recoverability under local perturbation.
    H_unprotected = 8.0 * (1 - np.exp(-3.0 * gamma))
    # Protected invariant remains recoverable until a transition closes protection.
    H_protected = np.where(gamma < gamma_c, 0.15 * gamma, 8.0 * (1 - np.exp(-7.0 * (gamma - gamma_c))))
    topo_marker = np.where(gamma < gamma_c, 1, 0)
    df = pd.DataFrame({"perturbation_strength": gamma,
                       "unprotected_residual_hysteresis": H_unprotected,
                       "protected_residual_hysteresis": H_protected,
                       "topological_protection_marker": topo_marker})
    df.to_csv(TAB / "fig8_p7_bridge.csv", index=False)

    plt.figure(figsize=(3.6, 2.65))
    plt.plot(gamma, H_unprotected, label="ordinary local encoding")
    plt.plot(gamma, H_protected, label="invariant/topological encoding")
    plt.axvline(gamma_c, linestyle="--", alpha=0.7, label="protection transition")
    plt.xlabel(r"local perturbation strength $\gamma$")
    plt.ylabel(r"residual hysteresis $H_{irr}$ [bits]")
    plt.title("P4-to-P7 bridge: protected distinctions")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    savefig("fig8_p7_bridge")


def main() -> None:
    fig1_preimage_recovery_bound()
    fig2_capacity_hysteresis()
    fig3_externalization_breakeven()
    fig4_mori_zwanzig_kernel()
    fig5_js_markov_closure()
    fig6_benign_malignant_hysteresis()
    fig7_phase_b_selection()
    fig8_p7_bridge()
    print(f"Generated figures in {FIG}")
    print(f"Generated CSV tables in {TAB}")


if __name__ == "__main__":
    main()
