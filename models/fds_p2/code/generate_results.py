#!/usr/bin/env python3
"""
Generate deterministic synthetic figures and CSV tables for FDS-P2 v0.2.
No empirical data are used. The figures illustrate model mechanisms:
correlated garbage entropy rate, memory-fill pressure, uncomputation versus cleanup,
cleanup scheduling, externalization latency, lossy compression/active forgetting,
regime phase diagram, and syndrome-style record turnover.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIG / f"{name}.pdf")
    plt.savefig(FIG / f"{name}.png", dpi=220)
    plt.close()


def fig1_entropy_rate_and_fill_pressure() -> None:
    # Correlated garbage: entropy-rate load grows more slowly than naive per-step sum.
    t = np.arange(0, 201)
    b_step = 0.75  # naive independent bits/update
    corr_len = 40.0
    entropy_load = b_step * (t - corr_len * (1 - np.exp(-t / corr_len)))  # correlated increments
    naive_load = b_step * t
    m0 = 15.0
    mmax = 110.0
    rho = (m0 + entropy_load) / mmax
    rho_clip = np.clip(rho, 0, 0.995)
    alloc_pressure = -8.0 * np.log(1 - rho_clip + 1e-3)  # nonlinear allocation/fragmentation pressure
    total_pressure = entropy_load + alloc_pressure
    df = pd.DataFrame({
        "t": t,
        "naive_sum_bits": naive_load,
        "entropy_rate_load_bits": entropy_load,
        "fill_ratio": rho,
        "allocation_pressure_proxy": alloc_pressure,
        "total_pressure_proxy": total_pressure,
    })
    df.to_csv(DATA / "fig1_entropy_rate_fill_pressure.csv", index=False)
    plt.figure(figsize=(6.4, 3.9))
    plt.plot(t, naive_load, label="naive sum of step losses")
    plt.plot(t, entropy_load, label="correlated garbage entropy load")
    plt.plot(t, total_pressure, label="load + allocation pressure")
    plt.axhline(mmax - m0, linestyle="--", label="available memory")
    plt.xlabel("update step")
    plt.ylabel("bits or equivalent pressure")
    plt.title("Correlated garbage and nonlinear memory-fill pressure")
    plt.legend(fontsize=8)
    savefig("fig1_entropy_rate_fill_pressure")


def fig2_cleanup_spikes_dynamic_residual() -> None:
    T = 180
    t = np.arange(T + 1)
    r = 0.9
    mmax = 80.0
    m0 = 8.0
    cleanup_threshold = 0.83
    retain_fraction_after_cleanup = 0.18
    mem = np.zeros_like(t, dtype=float)
    residual = np.zeros_like(t, dtype=float)
    heat_spikes = np.zeros_like(t, dtype=float)
    mem[0] = m0
    residual[0] = 0.0
    for i in range(1, len(t)):
        rho = mem[i-1] / mmax
        alloc = 0.06 * (-np.log(max(1 - rho, 1e-3)))
        mem[i] = mem[i-1] + r + alloc
        residual[i] = residual[i-1] + 0.12 * max(0, rho - 0.65)  # rising risk of unrecoverable residue
        if mem[i] / mmax > cleanup_threshold:
            clean_amount = mem[i] - (m0 + retain_fraction_after_cleanup * (mem[i] - m0))
            heat_spikes[i] = 0.75 * clean_amount
            residual[i] += 0.18 * clean_amount
            mem[i] = m0 + retain_fraction_after_cleanup * (mem[i] - m0)
    cum_heat = np.cumsum(heat_spikes)
    df = pd.DataFrame({"t": t, "memory_used": mem, "fill_ratio": mem/mmax, "cleanup_heat_spikes": heat_spikes, "cumulative_cleanup_heat": cum_heat, "accumulated_residual_irreversibility": residual})
    df.to_csv(DATA / "fig2_cleanup_spikes_dynamic_residual.csv", index=False)
    plt.figure(figsize=(6.4, 3.9))
    plt.plot(t, mem, label="memory used")
    plt.plot(t, heat_spikes, label="cleanup heat spikes")
    plt.plot(t, residual, label="accumulated residual irreversibility")
    plt.axhline(mmax, linestyle="--", label="Mmax")
    plt.xlabel("update step")
    plt.ylabel("bits, heat, or residual proxy")
    plt.title("Finite memory turns delayed erasure into cleanup events")
    plt.legend(fontsize=8)
    savefig("fig2_cleanup_spikes_dynamic_residual")


def fig3_uncomputation_vs_cleanup() -> None:
    t = np.arange(0, 121)
    gen_rate = 0.8
    # Strategy A: uncompute after output copy delay; memory cycles, low erasure heat but sync/copy burden.
    delay = 24
    mem_uncomp = 10 + gen_rate * (t % delay)
    sync_cost_uncomp = 0.22 * t + 0.15 * mem_uncomp
    heat_uncomp = 0.06 * t  # small non-erasure overhead proxy
    # Strategy B: irreversible cleanup every delay steps; memory cycles, heat spikes.
    mem_clean = 10 + gen_rate * (t % delay)
    heat_spikes = np.where((t > 0) & (t % delay == 0), gen_rate * delay * 0.7, 0.0)
    heat_clean = np.cumsum(heat_spikes) + 0.03 * t
    # Strategy C: do nothing; memory grows.
    mem_log = 10 + gen_rate * t
    df = pd.DataFrame({
        "t": t,
        "memory_uncomputation": mem_uncomp,
        "sync_cost_uncomputation": sync_cost_uncomp,
        "heat_uncomputation_proxy": heat_uncomp,
        "memory_cleanup": mem_clean,
        "cumulative_heat_cleanup": heat_clean,
        "memory_logging_only": mem_log,
    })
    df.to_csv(DATA / "fig3_uncomputation_vs_cleanup.csv", index=False)
    plt.figure(figsize=(6.4, 3.9))
    plt.plot(t, mem_log, label="reversible logging only: memory grows")
    plt.plot(t, mem_uncomp, label="uncomputation: memory released if path retained")
    plt.plot(t, heat_clean, label="irreversible cleanup: cumulative heat")
    plt.plot(t, sync_cost_uncomp, label="uncomputation sync/copy burden")
    plt.xlabel("update step")
    plt.ylabel("memory or cost proxy")
    plt.title("Uncomputation differs from irreversible cleanup")
    plt.legend(fontsize=8)
    savefig("fig3_uncomputation_vs_cleanup")


def fig4_cleanup_interval_tradeoff() -> None:
    intervals = np.arange(4, 121)
    r = 1.0
    # Per update average cleanup heat does not depend much on interval in ideal linear accounting.
    cleanup_avg = 0.50 * r * np.ones_like(intervals, dtype=float)
    # But refresh/storage pressure rises with interval.
    refresh_avg = 0.010 * (r * intervals) ** 1.25
    # Failure risk rises sharply when cleanup interval too long.
    fail_risk = 22.0 / (1.0 + np.exp(-(intervals - 82.0) / 8.0))
    # Too frequent cleanup has overhead as well.
    scheduling_overhead = 4.0 / intervals
    total = cleanup_avg + refresh_avg + fail_risk + scheduling_overhead
    df = pd.DataFrame({"cleanup_interval": intervals, "avg_cleanup_heat": cleanup_avg, "avg_refresh_pressure": refresh_avg, "failure_risk_penalty": fail_risk, "scheduling_overhead": scheduling_overhead, "total_policy_cost": total})
    df.to_csv(DATA / "fig4_cleanup_interval_tradeoff.csv", index=False)
    plt.figure(figsize=(6.4, 3.9))
    plt.plot(intervals, cleanup_avg, label="erasure floor per update")
    plt.plot(intervals, refresh_avg, label="refresh/storage pressure")
    plt.plot(intervals, fail_risk, label="failure-risk penalty")
    plt.plot(intervals, total, label="total policy cost")
    plt.xlabel("cleanup interval $T_c$")
    plt.ylabel("average cost proxy")
    plt.title("Cleanup scheduling creates a housekeeping tradeoff")
    plt.legend(fontsize=8)
    savefig("fig4_cleanup_interval_tradeoff")


def fig5_externalization_latency() -> None:
    f = np.linspace(0, 1, 101)  # fraction externalized
    local_memory = 100 * (1 - f)
    write_verify_sync = 15 * f + 40 * f**2
    latency = 0.15 + 1.25 * f**1.7
    task_window = 0.75
    delay_penalty = 65 / (1 + np.exp(-(latency - task_window) * 14))
    useful_capacity = 100 * f * (latency <= task_window) + 100 * f * np.exp(-4*np.maximum(0, latency-task_window)) * (latency > task_window)
    df = pd.DataFrame({
        "externalized_fraction": f,
        "local_memory_pressure": local_memory,
        "write_verify_sync_cost": write_verify_sync,
        "latency": latency,
        "task_window": task_window,
        "delay_penalty": delay_penalty,
        "useful_external_capacity": useful_capacity,
    })
    df.to_csv(DATA / "fig5_externalization_latency.csv", index=False)
    plt.figure(figsize=(6.4, 3.9))
    plt.plot(f, local_memory, label="local memory pressure")
    plt.plot(f, write_verify_sync, label="write/verify/sync cost")
    plt.plot(f, delay_penalty, label="delay penalty")
    plt.plot(f, useful_capacity, label="useful external capacity")
    plt.xlabel("fraction of garbage externalized")
    plt.ylabel("cost or capacity proxy")
    plt.title("Externalization shifts boundary and adds latency")
    plt.legend(fontsize=8)
    savefig("fig5_externalization_latency")


def fig6_lossy_compression_active_forgetting() -> None:
    c = np.linspace(0, 1, 101)  # compression aggressiveness / forgetting fraction
    memory_after = 100 * (1 - 0.85*c)
    residual_irreversibility = 65 * c**1.3
    task_distortion = 95 / (1 + np.exp(-(c - 0.62) * 16))  # small until critical compression
    refresh_savings = 70 * c
    erasure_heat = 32 * c
    total_cost = (100 - refresh_savings) + erasure_heat + 0.75*task_distortion + 0.45*residual_irreversibility
    df = pd.DataFrame({
        "compression_aggressiveness": c,
        "memory_after": memory_after,
        "residual_irreversibility": residual_irreversibility,
        "task_distortion": task_distortion,
        "refresh_savings": refresh_savings,
        "erasure_heat": erasure_heat,
        "total_cost_proxy": total_cost,
    })
    df.to_csv(DATA / "fig6_lossy_compression_active_forgetting.csv", index=False)
    plt.figure(figsize=(6.4, 3.9))
    plt.plot(c, memory_after, label="memory after compression")
    plt.plot(c, residual_irreversibility, label="residual irreversibility")
    plt.plot(c, task_distortion, label="task distortion")
    plt.plot(c, total_cost, label="total cost proxy")
    plt.xlabel("lossy compression / active forgetting level")
    plt.ylabel("bits or cost proxy")
    plt.title("Active forgetting trades memory for uncertainty and heat")
    plt.legend(fontsize=8)
    savefig("fig6_lossy_compression_active_forgetting")


def fig7_regime_diagram() -> None:
    r_vals = np.linspace(0.05, 2.4, 96)
    m_vals = np.linspace(20, 220, 96)
    R, M = np.meshgrid(r_vals, m_vals)
    t_fill = M / R
    # Heuristic regime codes
    # 0 stable reversible logging, 1 periodic cleanup, 2 externalization/compression, 3 failure/collapse
    regime = np.zeros_like(R, dtype=int)
    regime[(t_fill < 120) & (t_fill >= 55)] = 1
    regime[(t_fill < 55) & (M > 70)] = 2
    regime[(t_fill < 55) & (M <= 70)] = 3
    df = pd.DataFrame({"garbage_rate": R.ravel(), "memory_capacity": M.ravel(), "fill_time": t_fill.ravel(), "regime_code": regime.ravel()})
    df.to_csv(DATA / "fig7_bounded_memory_regime_diagram.csv", index=False)
    plt.figure(figsize=(6.4, 4.2))
    plt.contourf(R, M, regime, levels=[-0.5,0.5,1.5,2.5,3.5], alpha=0.85)
    cbar = plt.colorbar(ticks=[0,1,2,3])
    cbar.ax.set_yticklabels(["logging stable", "periodic cleanup", "externalize/compress", "failure risk"])
    plt.contour(R, M, t_fill, levels=[55,120], linestyles="--")
    plt.xlabel("garbage entropy rate $r_G$")
    plt.ylabel("memory capacity $M_{max}$")
    plt.title("Bounded-memory regimes under sustained reversible updates")
    savefig("fig7_bounded_memory_regime_diagram")


def fig8_syndrome_style_turnover() -> None:
    # Generic high-rate finite-record turnover, not a no-go theorem.
    cycle = np.logspace(-7, -3, 120)
    n_records = 1e6
    bits_per_record = 1.0
    T_kelvin = 0.02
    kB = 1.380649e-23
    landauer = n_records * bits_per_record * kB * T_kelvin * np.log(2) / cycle
    actual_overhead = 1e-12 * n_records * (1e-6 / cycle) ** 0.65
    refresh_clock = 2e-13 * n_records * (1e-6 / cycle)
    total = landauer + actual_overhead + refresh_clock
    df = pd.DataFrame({
        "cycle_time_s": cycle,
        "landauer_lower_bound_W": landauer,
        "overhead_proxy_W": actual_overhead,
        "refresh_clock_proxy_W": refresh_clock,
        "total_proxy_W": total,
    })
    df.to_csv(DATA / "fig8_syndrome_style_turnover.csv", index=False)
    plt.figure(figsize=(6.4, 3.9))
    plt.loglog(cycle, landauer, label="Landauer lower bound")
    plt.loglog(cycle, actual_overhead, label="implementation overhead proxy")
    plt.loglog(cycle, refresh_clock, label="refresh/clock proxy")
    plt.loglog(cycle, total, label="total turnover proxy")
    plt.gca().invert_xaxis()
    plt.xlabel("record cycle time (s)")
    plt.ylabel("power proxy (W)")
    plt.title("High-rate syndrome-style records instantiate the P2 ledger")
    plt.legend(fontsize=8)
    savefig("fig8_syndrome_style_turnover")


def main() -> None:
    fig1_entropy_rate_and_fill_pressure()
    fig2_cleanup_spikes_dynamic_residual()
    fig3_uncomputation_vs_cleanup()
    fig4_cleanup_interval_tradeoff()
    fig5_externalization_latency()
    fig6_lossy_compression_active_forgetting()
    fig7_regime_diagram()
    fig8_syndrome_style_turnover()


if __name__ == "__main__":
    main()
