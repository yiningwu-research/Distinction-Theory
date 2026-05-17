#!/usr/bin/env python3
"""Generate deterministic synthetic simulations for FDS-O3.

The figures are illustrative normal-form demonstrations, not fits to physical devices
or biological data. Running this script regenerates all figures and CSV files.
"""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)


def savefig(name: str) -> None:
    plt.tight_layout()
    for ext in ("pdf", "png"):
        plt.savefig(FIG / f"{name}.{ext}", dpi=220 if ext == "png" else None, bbox_inches="tight")
    plt.close()


def fig1_memory_reuse() -> None:
    t = np.arange(0, 180)
    C_mem = np.full_like(t, 100, dtype=float)
    incoming = 1.05 + 0.006 * t
    protected = 12 + 0.08 * t  # invariant/context records not immediately reusable
    record_load = np.cumsum(incoming) * 0.72 + protected
    record_load = np.minimum(record_load, 150)
    rho = record_load / C_mem
    reuse_pressure = np.maximum(record_load - C_mem, 0)
    df = pd.DataFrame({"step": t, "record_load": record_load, "C_mem": C_mem, "rho_M": rho, "reuse_pressure": reuse_pressure})
    df.to_csv(DATA / "figure1_memory_reuse.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.plot(t, record_load, label="record load $B_R(t)$")
    plt.plot(t, C_mem, "--", label="finite memory $C_{mem}$")
    plt.fill_between(t, C_mem, record_load, where=record_load >= C_mem, alpha=0.25, label="reuse pressure")
    plt.xlabel("update step")
    plt.ylabel("record units")
    plt.title("Finite memory creates record-reuse pressure")
    plt.legend(fontsize=8)
    savefig("fig1_memory_reuse")


def fig2_residual_irreversibility() -> None:
    t = np.arange(0, 160)
    # Reversible logging stores side records; low residual but memory grows.
    rev_res = np.zeros_like(t, dtype=float) + 2
    rev_memory = 20 + 0.72 * t
    # Bounded cleanup: sawtooth residual spikes at cleanup events.
    cleanup_period = 36
    phase = t % cleanup_period
    bounded_res = 3 + 0.22 * phase
    clean_spikes = (phase == cleanup_period - 1).astype(float) * 18
    bounded_entropy = 0.45 * bounded_res + clean_spikes
    # Lossy overwrite: high residual but low memory.
    overwrite_res = 4 + 0.17 * t
    overwrite_entropy = 2.5 + 0.18 * overwrite_res
    df = pd.DataFrame({
        "step": t,
        "rev_residual": rev_res,
        "rev_memory": rev_memory,
        "bounded_residual": bounded_res,
        "bounded_entropy": bounded_entropy,
        "overwrite_residual": overwrite_res,
        "overwrite_entropy": overwrite_entropy,
    })
    df.to_csv(DATA / "figure2_residual_irreversibility.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.plot(t, rev_memory / 5, label="reversible logging: memory/5")
    plt.plot(t, bounded_entropy, label="bounded cleanup: entropy proxy")
    plt.plot(t, overwrite_entropy, label="lossy overwrite: entropy proxy")
    plt.plot(t, overwrite_res, "--", label="residual irreversibility")
    plt.xlabel("update step")
    plt.ylabel("proxy units")
    plt.title("Residual irreversibility and record-turnover cost")
    plt.legend(fontsize=8)
    savefig("fig2_residual_irreversibility")


def fig3_entropy_ledger() -> None:
    t = np.arange(0, 170)
    stress = 1 / (1 + np.exp(-(t - 80) / 18))
    erase = 2 + 0.05 * t + 8 * stress
    refresh = 9 + 0.035 * t + 4 * stress
    repair = 1.5 + 10 * np.exp(-0.5 * ((t - 115) / 22) ** 2)
    sync = 3 + 0.08 * t
    ext = 1 + 16 * stress**2
    recovery = 0.4 + 9 * np.exp(-0.5 * ((t - 135) / 16) ** 2)
    total = erase + refresh + repair + sync + ext + recovery
    df = pd.DataFrame({"step": t, "erase": erase, "refresh": refresh, "repair": repair, "sync": sync, "externalization": ext, "recovery": recovery, "audit_total": total})
    df.to_csv(DATA / "figure3_entropy_ledger.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.stackplot(t, erase, refresh, repair, sync, ext, recovery, labels=["erase", "refresh", "repair", "sync", "external", "recovery"])
    plt.plot(t, total, linewidth=2.0, label="audit total")
    plt.xlabel("update step")
    plt.ylabel("unique-channel entropy proxy")
    plt.title("O3 coupled entropy ledger")
    plt.legend(fontsize=7, loc="upper left")
    savefig("fig3_entropy_ledger")


def fig4_externalization_audit() -> None:
    x = np.linspace(0, 1, 160)
    local = 105 * (1 - 0.75 * x) + 6 * x**2
    write_verify_retrieve = 12 + 45 * x + 80 * x**2
    latency = 6 + 32 * x**3
    coupled = local + write_verify_retrieve + latency
    df = pd.DataFrame({"externalized_fraction": x, "local": local, "external_overhead": write_verify_retrieve, "latency_sync": latency, "coupled": coupled})
    df.to_csv(DATA / "figure4_externalization_audit.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.plot(x, local, label="local ledger")
    plt.plot(x, write_verify_retrieve, label="write/verify/retrieve")
    plt.plot(x, latency, label="latency/sync")
    plt.plot(x, coupled, linewidth=2.0, label="coupled ledger")
    plt.axhline(local[0], linestyle=":", linewidth=1, label="initial local")
    plt.xlabel("fraction of records externalized")
    plt.ylabel("cost proxy")
    plt.title("Externalization shifts the operational Second-Law channel")
    plt.legend(fontsize=8)
    savefig("fig4_externalization_audit")


def fig5_pruning_roi() -> None:
    t = np.arange(0, 190)
    no_prune = 18 + 0.0027 * t**2
    event = 65
    task_pres = 18 + 0.0012 * t**2 + 45 * np.exp(-0.5 * ((t - event) / 5) ** 2)
    task_pres[t > event] = 30 + 0.001 * (t[t > event] - event) ** 2 + 40 * np.exp(-0.5 * ((t[t > event] - event) / 5) ** 2)
    over = 19 + 0.0009 * t**2 + 70 * np.exp(-0.5 * ((t - event) / 4) ** 2)
    over[t > event] = 10 + 0.0006 * (t[t > event] - event) ** 2 + 70 * np.exp(-0.5 * ((t[t > event] - event) / 4) ** 2)
    task_loss = np.zeros_like(t, dtype=float)
    task_loss[t > event] = 22 + 0.002 * (t[t > event] - event) ** 2
    over_total = over + task_loss
    savings = np.maximum(no_prune - task_pres, 0)
    df = pd.DataFrame({"time": t, "no_prune": no_prune, "task_preserving_prune": task_pres, "over_prune_total": over_total, "savings": savings})
    df.to_csv(DATA / "figure5_pruning_roi.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.plot(t, no_prune, label="no pruning")
    plt.plot(t, task_pres, label="task-preserving pruning")
    plt.plot(t, over_total, label="over-pruning task loss")
    plt.fill_between(t, task_pres, no_prune, where=no_prune > task_pres, alpha=0.22, label="future saving")
    plt.axvline(event, linestyle="--", linewidth=1, label="pruning event")
    plt.xlabel("time horizon")
    plt.ylabel("entropy-production or loss proxy")
    plt.title("Pruning and invariant compression as entropy relief")
    plt.legend(fontsize=8)
    savefig("fig5_pruning_roi")


def fig6_invariant_compression() -> None:
    compression = np.linspace(0, 1, 160)
    # Maintenance burden falls with compression; task loss rises after critical loss of distinctions.
    maintenance = 92 * np.exp(-2.25 * compression) + 12
    verification = 16 - 5 * compression + 2 * compression**2
    task_penalty = 4 + 135 * np.maximum(compression - 0.70, 0) ** 2
    total = maintenance + verification + task_penalty
    critical = 0.70
    optimum_idx = int(np.argmin(total))
    optimum = compression[optimum_idx]
    df = pd.DataFrame({
        "compression_strength": compression,
        "maintenance": maintenance,
        "verification": verification,
        "task_penalty": task_penalty,
        "total_objective": total,
        "critical_complexity": np.full_like(compression, critical),
        "optimum": np.full_like(compression, optimum),
    })
    df.to_csv(DATA / "figure6_invariant_compression.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.plot(compression, maintenance, label="maintenance ledger")
    plt.plot(compression, task_penalty, label="task-loss penalty")
    plt.plot(compression, total, linewidth=2.0, label="$J(q)$ total")
    plt.axvline(critical, linestyle="--", linewidth=1, label="critical compression")
    plt.axvline(optimum, linestyle=":", linewidth=1.5, label="optimal quotient $q^*$")
    plt.fill_between(compression, 0, total, where=compression > critical, alpha=0.15, label="over-compression region")
    plt.xlabel("compression strength / quotient coarseness")
    plt.ylabel("ledger or loss proxy")
    plt.title("Invariant compression has an optimum")
    plt.legend(fontsize=8)
    savefig("fig6_invariant_compression")

def fig7_hysteresis() -> None:
    d = np.linspace(0, 90, 160)
    increasing = 20 + 0.55 * d + 0.018 * d**2
    decreasing = 24 + 0.7 * d + 0.02 * d**2 + 14 * (1 - np.exp(-d / 35))
    gap = decreasing - increasing
    df = pd.DataFrame({"positive_deficit": d, "increasing": increasing, "decreasing_after_overload": decreasing, "gap": gap})
    df.to_csv(DATA / "figure7_hysteresis.csv", index=False)
    plt.figure(figsize=(6, 4))
    plt.plot(d, increasing, label="deficit increasing")
    plt.plot(d, decreasing, label="decreasing after overload")
    plt.fill_between(d, increasing, decreasing, where=decreasing >= increasing, alpha=0.2, label="record/invariant gap")
    plt.xlabel("positive deficit / residual irreversibility")
    plt.ylabel("ledger proxy")
    plt.title("Finite-memory hysteresis after overload")
    plt.legend(fontsize=8)
    savefig("fig7_hysteresis")


def fig8_regime_diagram() -> None:
    r = np.linspace(0, 90, 120)
    fin = np.linspace(20, 170, 120)
    R, F = np.meshgrid(r, fin)
    demand = 30 + 0.9 * R + 0.018 * R**2
    relief = 0.28 * F
    score = demand - relief
    # 0 stable, 1 high-diss, 2 prune/ext, 3 invariant, 4 collapse
    regime = np.zeros_like(score)
    regime[score > 15] = 1
    regime[score > 45] = 2
    regime[(score > 25) & (R < 35) & (F > 85)] = 3
    regime[score > 75] = 4
    pd.DataFrame({"r_res": R.ravel(), "resource_input": F.ravel(), "regime": regime.ravel()}).to_csv(DATA / "figure8_regime_diagram.csv", index=False)
    plt.figure(figsize=(6, 4))
    cs = plt.contourf(R, F, regime, levels=[-0.5,0.5,1.5,2.5,3.5,4.5])
    cbar = plt.colorbar(cs, ticks=[0,1,2,3,4])
    cbar.ax.set_yticklabels(["stable", "high-diss", "prune/ext", "invariant", "collapse"])
    plt.xlabel("residual irreversibility rate")
    plt.ylabel("resource input $\dot F_{in}$")
    plt.title("O3 regimes under finite memory")
    savefig("fig8_regime_diagram")


def main() -> None:
    fig1_memory_reuse()
    fig2_residual_irreversibility()
    fig3_entropy_ledger()
    fig4_externalization_audit()
    fig5_pruning_roi()
    fig6_invariant_compression()
    fig7_hysteresis()
    fig8_regime_diagram()


if __name__ == "__main__":
    main()
