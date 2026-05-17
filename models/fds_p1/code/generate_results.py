#!/usr/bin/env python3
"""
Generate deterministic synthetic demonstrations for FDS-P1 v0.2.

The simulations are not empirical fits. They illustrate the model relations in
"Physical Distinction Carriers and Erasure Maps" using simple finite-record,
readout, accounting-boundary, and thermodynamic-accounting proxies.
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


def savefig(name: str) -> None:
    for ext in ("pdf", "png"):
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=220)
    plt.close()


def gaussian_binary_error(dnr: np.ndarray) -> np.ndarray:
    """Bayes error for two equal-variance Gaussian readout states.

    DNR = |mu1 - mu0| / sigma. Equal priors and equal variance give
    P_e = Phi(-DNR/2) = 0.5 erfc(DNR/(2 sqrt(2))).
    """
    return 0.5 * np.array([math.erfc(float(x) / (2 * math.sqrt(2))) for x in dnr])


def figure_1_dnr() -> None:
    dnr = np.linspace(0.05, 12.0, 300)
    p_err = gaussian_binary_error(dnr)
    reliability = 1.0 - p_err
    eps_levels = [1e-1, 1e-2, 1e-3]
    rows = []
    for eps in eps_levels:
        idx = int(np.argmax(p_err <= eps))
        rows.append((eps, dnr[idx]))
    df = pd.DataFrame({"DNR_delta_over_sigma": dnr,
                       "bayes_readout_error": p_err,
                       "reliability": reliability})
    df.to_csv(DATA / "fig1_dnr_readout.csv", index=False)

    plt.figure(figsize=(6.4, 4.1))
    plt.semilogy(dnr, p_err, label="readout error")
    for eps, req in rows:
        plt.axhline(eps, linestyle="--", linewidth=0.9)
        plt.axvline(req, linestyle=":", linewidth=0.9)
        plt.text(req + 0.08, eps * 1.25, f"epsilon={eps:g}", fontsize=8)
    plt.xlabel("distinction-to-noise ratio DNR = |mu1-mu0| / sigma")
    plt.ylabel("Bayes readout error")
    plt.title("DNR controls physical carrier qualification")
    plt.legend(frameon=False)
    savefig("fig1_dnr_readout")


def figure_2_retention_refresh() -> None:
    barrier = np.linspace(0.1, 22.0, 260)  # E_b/kBT
    tau0 = 1.0
    tau_rec = tau0 * np.exp(barrier)
    tau_task = 1e5
    # Probability that record survives the task without refresh under exponential failure.
    survival = np.exp(-tau_task / tau_rec)
    # Minimal refresh rate proxy needed to maintain a record with shorter intrinsic lifetime.
    # If tau_rec < tau_task, refresh roughly every tau_rec; otherwise no forced refresh.
    refresh_rate = np.where(tau_rec < tau_task, 1.0 / tau_rec, 0.0)
    e_refresh = 20.0  # dimensionless energy per refresh event, arbitrary units
    refresh_power = e_refresh * refresh_rate
    df = pd.DataFrame({"barrier_E_over_kBT": barrier,
                       "record_lifetime_tau_rec": tau_rec,
                       "task_window_tau_task": tau_task,
                       "survival_probability_no_refresh": survival,
                       "refresh_rate_proxy": refresh_rate,
                       "refresh_power_proxy": refresh_power})
    df.to_csv(DATA / "fig2_retention_refresh.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(6.4, 4.1))
    ax1.semilogy(barrier, tau_rec, label="intrinsic lifetime tau_rec")
    ax1.axhline(tau_task, linestyle="--", linewidth=0.9, label="task window tau_task")
    ax1.set_xlabel("stability barrier E_b / kBT")
    ax1.set_ylabel("lifetime / update-time units")
    ax2 = ax1.twinx()
    ax2.plot(barrier, refresh_power, linestyle=":", label="refresh power proxy")
    ax2.set_ylabel("refresh power proxy")
    ax1.set_title("Record stability and refresh cost")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, frameon=False, fontsize=8)
    savefig("fig2_retention_refresh")


def entropy_bits(prob: np.ndarray) -> float:
    p = np.asarray(prob, dtype=float)
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def figure_3_accounting_boundary() -> None:
    n_in = 256
    hx = math.log2(n_in)
    # A map from 256 inputs to 16 visible records loses 4 bits at the visible level.
    n_visible = 16
    hy = math.log2(n_visible)
    visible_preimage_loss = hx - hy
    side_fraction = np.linspace(0.0, 1.0, 101)
    side_bits_inside = visible_preimage_loss * side_fraction
    erasure_relative_A = np.maximum(visible_preimage_loss - side_bits_inside, 0.0)
    memory_fill_pressure = side_bits_inside
    heat_floor = math.log(2) * erasure_relative_A
    df = pd.DataFrame({"side_record_fraction_inside_accounting_boundary": side_fraction,
                       "visible_preimage_loss_bits": visible_preimage_loss,
                       "side_record_bits_inside_A": side_bits_inside,
                       "erasure_bits_relative_to_A": erasure_relative_A,
                       "memory_fill_pressure_bits": memory_fill_pressure,
                       "landauer_floor_over_kBT_relative_to_A": heat_floor})
    df.to_csv(DATA / "fig3_accounting_boundary.csv", index=False)

    plt.figure(figsize=(6.4, 4.1))
    plt.plot(side_fraction, erasure_relative_A, label="erasure bits relative to A")
    plt.plot(side_fraction, memory_fill_pressure, label="side-record memory fill inside A")
    plt.plot(side_fraction, heat_floor, linestyle="--", label="heat floor/kBT relative to A")
    plt.xlabel("fraction of missing preimage kept as side records inside A")
    plt.ylabel("bits or dimensionless heat bound")
    plt.title("Accounting boundary separates erasure from side-record pressure")
    plt.legend(frameon=False, fontsize=8)
    savefig("fig3_accounting_boundary")


def figure_4_dissipative_projection() -> None:
    steps = np.arange(0, 121)
    erased_bits_per_step = 2.0
    abstract = np.zeros_like(steps, dtype=float)
    overwrite = math.log(2) * erased_bits_per_step * steps
    side_memory = erased_bits_per_step * steps
    memory_capacity = 150.0
    cleanup_bits = np.maximum(side_memory - memory_capacity, 0.0)
    delayed_cleanup = math.log(2) * cleanup_bits
    compression_loss = 0.6 * overwrite  # lossy many-to-one compression in this toy model
    df = pd.DataFrame({"step": steps,
                       "abstract_projection_heat_over_kBT": abstract,
                       "physical_overwrite_heat_over_kBT": overwrite,
                       "reversible_side_memory_bits": side_memory,
                       "delayed_cleanup_heat_over_kBT": delayed_cleanup,
                       "lossy_compression_heat_over_kBT": compression_loss})
    df.to_csv(DATA / "fig4_dissipative_projection.csv", index=False)

    plt.figure(figsize=(6.4, 4.1))
    plt.plot(steps, abstract, label="abstract projection")
    plt.plot(steps, overwrite, label="dissipative projection: overwrite")
    plt.plot(steps, delayed_cleanup, label="reversible logging then cleanup")
    plt.plot(steps, side_memory * 0.2, linestyle=":", label="side memory pressure (scaled)")
    plt.xlabel("update step")
    plt.ylabel("dimensionless heat or scaled memory")
    plt.title("Logical projection versus dissipative projection")
    plt.legend(frameon=False, fontsize=8)
    savefig("fig4_dissipative_projection")


def figure_5_refresh_erasure_ledger() -> None:
    t = np.arange(0, 180)
    records = 50 + 0.45 * t
    q_hold = 0.006 * records
    q_refresh = 0.00022 * records**2
    q_clock = 0.18 + 0.001 * t
    q_phys = q_hold + q_refresh + q_clock
    erasure_bits = np.zeros_like(t, dtype=float)
    for k, bits in [(45, 120), (90, 180), (135, 220)]:
        erasure_bits[k] = bits
    q_info = math.log(2) * erasure_bits
    cumulative_phys = np.cumsum(q_phys)
    cumulative_info = np.cumsum(q_info)
    df = pd.DataFrame({"time": t,
                       "records_maintained": records,
                       "holding_power_proxy": q_hold,
                       "refresh_power_proxy": q_refresh,
                       "clocking_power_proxy": q_clock,
                       "Q_phys_power_proxy": q_phys,
                       "erasure_bits_event": erasure_bits,
                       "Q_info_event_over_kBT": q_info,
                       "cumulative_Q_phys_proxy": cumulative_phys,
                       "cumulative_Q_info_over_kBT": cumulative_info})
    df.to_csv(DATA / "fig5_refresh_erasure_ledger.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(6.4, 4.1))
    ax1.plot(t, cumulative_phys, label="cumulative Q_phys: hold+refresh+clock")
    ax1.step(t, cumulative_info, where="post", label="cumulative Q_info erasure floor")
    ax1.plot(t, cumulative_phys + cumulative_info, label="combined ledger")
    ax1.set_xlabel("time / update units")
    ax1.set_ylabel("dimensionless cost proxy")
    ax1.set_title("Refresh cost and erasure cost are distinct ledger terms")
    ax1.legend(frameon=False, fontsize=8)
    savefig("fig5_refresh_erasure_ledger")


def figure_6_energy_flow_diagram() -> None:
    # Fixed illustrative flow values in units of kBT.
    flows = {
        "Main reset": 100.0,
        "Visible heat": 42.0,
        "Side record": 30.0,
        "Feedback memory": 18.0,
        "Work/source account": 10.0,
    }
    df = pd.DataFrame([{"channel": k, "dimensionless_account_over_kBT": v} for k, v in flows.items()])
    df.to_csv(DATA / "fig6_energy_flow_accounting.csv", index=False)

    plt.figure(figsize=(6.5, 4.2))
    ax = plt.gca()
    ax.axis("off")
    ax.set_title("Full accounting boundary can remove sub-bound illusion", pad=12)
    # Node boxes
    boxes = {
        "main": (0.05, 0.55, "main register\nreset"),
        "visible": (0.55, 0.75, "visible heat\n42 kBT"),
        "side": (0.55, 0.52, "side record\n30 kBT eq."),
        "feedback": (0.55, 0.29, "feedback memory\n18 kBT eq."),
        "work": (0.55, 0.06, "work/source\n10 kBT eq."),
        "full": (0.05, 0.12, "full boundary A\n100 kBT account"),
    }
    for x, y, text in boxes.values():
        ax.text(x, y, text, ha="center", va="center", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="black", lw=0.8))
    # Arrows from main to accounts
    for key in ["visible", "side", "feedback", "work"]:
        x2, y2, _ = boxes[key]
        ax.annotate("", xy=(x2-0.12, y2), xytext=(0.18, 0.55),
                    arrowprops=dict(arrowstyle="->", lw=1.0))
    ax.annotate("visible-only view: 42 < 100", xy=(0.38, 0.82), xytext=(0.08, 0.9),
                arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=9)
    ax.annotate("complete A-accounting:\n42+30+18+10 = 100", xy=(0.32, 0.18), xytext=(0.48, 0.15),
                arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    savefig("fig6_energy_flow_accounting")


def figure_7_time_resolution_tradeoff() -> None:
    dt = np.logspace(-3, 1, 240)  # tick interval
    b_tick = 16.0
    b_erase_per_tick = 4.0
    update_throughput = b_tick / dt
    landauer_power = math.log(2) * b_erase_per_tick / dt
    engineering_power = landauer_power + 0.018 * update_throughput**1.25
    df = pd.DataFrame({"tick_interval_delta_t": dt,
                       "update_throughput_bits_per_time": update_throughput,
                       "landauer_floor_power_over_kBT_per_time": landauer_power,
                       "engineering_power_proxy": engineering_power})
    df.to_csv(DATA / "fig7_time_resolution_tradeoff.csv", index=False)

    plt.figure(figsize=(6.4, 4.1))
    plt.loglog(dt, update_throughput, label="update throughput b_tick/dt")
    plt.loglog(dt, landauer_power, label="erasure lower bound")
    plt.loglog(dt, engineering_power, linestyle="--", label="engineering proxy")
    plt.gca().invert_xaxis()
    plt.xlabel("tick interval Delta t")
    plt.ylabel("rate or power proxy")
    plt.title("Sharper register time requires higher turnover")
    plt.legend(frameon=False, fontsize=8)
    savefig("fig7_time_resolution_tradeoff")


def main() -> None:
    figure_1_dnr()
    figure_2_retention_refresh()
    figure_3_accounting_boundary()
    figure_4_dissipative_projection()
    figure_5_refresh_erasure_ledger()
    figure_6_energy_flow_diagram()
    figure_7_time_resolution_tradeoff()
    print(f"Generated figures in {FIG}")
    print(f"Generated data in {DATA}")


if __name__ == "__main__":
    main()
