#!/usr/bin/env python3
"""
Deterministic normal-form numerical demonstrations for FDS-P6 v1.1.
These figures illustrate the speed-precision-resource ledger and exit-channel
logic. They are not empirical fits, device data, or universal phase diagrams.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 7.5,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
})

# Global parameters for reproducibility
D_EFF = 8.0                  # effective task dimension proxy
DELTA = 1e-3                 # target failure probability
RESOURCE_BUDGETS = [120, 220, 360]
RESOURCE_LIMIT = 240.0       # illustrative sustainable internal rate for failure contour
KB = 1.380649e-23
T_K = 300.0
LANDAUER_J_PER_BIT = KB * T_K * np.log(2.0)

params = pd.DataFrame([
    {"parameter": "D_EFF", "value": D_EFF, "description": "effective task dimension proxy"},
    {"parameter": "DELTA", "value": DELTA, "description": "target failure probability in confidence term"},
    {"parameter": "RESOURCE_LIMIT", "value": RESOURCE_LIMIT, "description": "illustrative sustainable internal throughput/resource threshold"},
    {"parameter": "v_max_rel", "value": 1.0, "description": "normalized relativistic causal upper bound"},
    {"parameter": "v_max_robot", "value": 0.25, "description": "normalized engineered sensor/actuator communication speed"},
    {"parameter": "v_max_bio", "value": 0.06, "description": "normalized biological/neural/diffusive speed"},
    {"parameter": "LANDAUER_J_PER_BIT_300K", "value": LANDAUER_J_PER_BIT, "description": "toy calibration only; not used as universal dissipation law"},
])
params.to_csv(DATA / "simulation_parameters.csv", index=False)

# -----------------------------
# Figure 1: speed-precision load surface with failure contour
# -----------------------------
update_speed = np.linspace(0.5, 20.0, 180)  # 1/tau, arbitrary update units
precision = np.logspace(-3, -0.2, 160)      # epsilon, smaller means tighter tolerance
U, Eps = np.meshgrid(update_speed, precision)
B_load = D_EFF * U * np.log2(1.0 / Eps)

fig, ax = plt.subplots(figsize=(6.6, 4.3))
mesh = ax.pcolormesh(U, Eps, B_load, shading="auto")
ax.contour(U, Eps, B_load, levels=[RESOURCE_LIMIT], colors="black", linewidths=1.2)
ax.text(10.8, 0.011, "failure boundary\n(toy threshold)", fontsize=8, ha="center")
ax.set_yscale("log")
ax.invert_yaxis()
ax.set_xlabel(r"maintenance speed $\nu_{\rm upd}=1/\tau$ [arb.]")
ax.set_ylabel(r"precision tolerance $\varepsilon$")
ax.set_title("Speed-precision throughput burden")
cbar = fig.colorbar(mesh, ax=ax)
cbar.set_label(r"$\mathcal{B}_{\varepsilon,\tau}=R_{\min}(\varepsilon)/\tau$ [bits/time]")
fig.savefig(FIG / "fig1_speed_precision_load.pdf")
fig.savefig(FIG / "fig1_speed_precision_load.png")
plt.close(fig)
pd.DataFrame({"update_speed": U.ravel(), "epsilon": Eps.ravel(), "throughput_burden": B_load.ravel(), "failure_boundary": RESOURCE_LIMIT}).to_csv(DATA / "fig1_speed_precision_load.csv", index=False)

# -----------------------------
# Figure 2: resource ledger decomposition vs speed
# -----------------------------
speed = np.linspace(0.2, 18.0, 220)
epsilon_fixed = 0.02
R_task = D_EFF * np.log2(1 / epsilon_fixed)
R_rate = R_task * speed
sense = 0.30 * R_rate
update = 0.40 * R_rate
verify = 0.16 * speed * np.log2(1 / DELTA)
p_err_proxy = 0.025 + 0.20 / (1 + np.exp(-(speed - 10.0)))
correct = speed * 13.0 * p_err_proxy
sync = 0.045 * speed**1.35
ledger_total = sense + update + verify + correct + sync

fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.stackplot(speed, sense, update, verify, correct, sync,
             labels=["sense", "update", "verify", "correct", "sync"])
ax.plot(speed, ledger_total, linewidth=1.6, label="audit total")
ax.axhline(RESOURCE_LIMIT, linestyle="--", linewidth=1.1, color="black", label="sustainable threshold")
ax.set_xlabel(r"maintenance speed $1/\tau$ [arb.]")
ax.set_ylabel("resource / power ledger proxy")
ax.set_title("P6 resource ledger grows under speed pressure")
ax.legend(loc="upper left", ncol=2)
fig.savefig(FIG / "fig2_resource_ledger.pdf")
fig.savefig(FIG / "fig2_resource_ledger.png")
plt.close(fig)
pd.DataFrame({"speed": speed, "sense": sense, "update": update, "verify": verify, "correct": correct, "sync": sync, "total": ledger_total, "threshold": RESOURCE_LIMIT}).to_csv(DATA / "fig2_resource_ledger.csv", index=False)

# -----------------------------
# Figure 3: finite resource error floor
# -----------------------------
speed_grid = np.linspace(0.5, 20.0, 300)
fig, ax = plt.subplots(figsize=(6.5, 4.2))
rows = []
for budget in RESOURCE_BUDGETS:
    # invert normal-form cost: budget ~= a*speed*log2(1/eps)+b*speed*log2(1/delta)
    a = 8.0
    b = 1.05 * np.log2(1/DELTA)
    available_for_precision = np.maximum(budget / speed_grid - b, 0.05)
    eps_min = 2 ** (-available_for_precision / a)
    eps_min = np.clip(eps_min, 1e-4, 0.7)
    ax.plot(speed_grid, eps_min, label=f"budget={budget}")
    rows.extend([{"speed": s, "resource_budget": budget, "epsilon_min": e} for s, e in zip(speed_grid, eps_min)])
ax.set_yscale("log")
ax.set_xlabel(r"maintenance speed $1/\tau$ [arb.]")
ax.set_ylabel(r"minimum achievable tolerance $\varepsilon_{\min}$")
ax.set_title("Finite resources impose a latency-precision tradeoff")
ax.legend(title="resource")
fig.savefig(FIG / "fig3_error_floor.pdf")
fig.savefig(FIG / "fig3_error_floor.png")
plt.close(fig)
pd.DataFrame(rows).to_csv(DATA / "fig3_error_floor.csv", index=False)

# -----------------------------
# Figure 4: causal horizon maintenance with effective propagation speeds
# -----------------------------
tau = np.linspace(0.02, 2.0, 300)
speeds = {"relativistic upper bound": 1.0, "robotic link": 0.25, "biological/diffusive": 0.06}
demand_radius = 0.55
rows = []
fig, ax1 = plt.subplots(figsize=(6.6, 4.2))
for label, vmax in speeds.items():
    reachable = vmax * tau
    ax1.plot(tau, reachable, label=fr"$v_{{\max}}$ {label}")
    burden = np.maximum(demand_radius - reachable, 0) ** 2 * 90
    for t, r, b in zip(tau, reachable, burden):
        rows.append({"tau": t, "vmax_label": label, "vmax": vmax, "causal_reach": r, "demand_radius": demand_radius, "prediction_burden": b})
ax1.axhline(demand_radius, linestyle="--", color="black", label="task horizon demand")
ax1.set_xlabel(r"update window $\tau$ [arb.]")
ax1.set_ylabel("reachable boundary radius [normalized]")
ax1.set_title("Effective causal reach limits real-time maintenance")
ax1.legend(loc="upper left")
fig.savefig(FIG / "fig4_causal_horizon.pdf")
fig.savefig(FIG / "fig4_causal_horizon.png")
plt.close(fig)
pd.DataFrame(rows).to_csv(DATA / "fig4_causal_horizon.csv", index=False)

# -----------------------------
# Figure 5: externalization break-even under speed pressure
# -----------------------------
L = np.linspace(0, 1.0, 220)  # fraction externalized
internal_fast = 92 * (1 - L) ** 1.45 + 25
write_sync_verify = 12 + 34 * L + 78 * L**2
latency_penalty = 3 + 38 * L**3
coupled = internal_fast + write_sync_verify + latency_penalty
baseline = np.full_like(L, internal_fast[0])
break_even = coupled < baseline[0]
fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.plot(L, internal_fast, label="remaining internal fast-update cost")
ax.plot(L, write_sync_verify, label="external write/sync/verify")
ax.plot(L, latency_penalty, label="latency/retrieval penalty")
ax.plot(L, coupled, linewidth=1.6, label="coupled ledger")
ax.axhline(baseline[0], linestyle="--", label="no-externalization baseline")
if break_even.any():
    ax.fill_between(L, 0, np.max(coupled)*1.05, where=break_even, alpha=0.12, label="break-even region")
ax.set_xlabel("fraction of fast distinctions externalized")
ax.set_ylabel("cost proxy")
ax.set_title("Externalization can relieve speed pressure, but shifts the ledger")
ax.legend(loc="upper center", ncol=2)
fig.savefig(FIG / "fig5_externalization_break_even.pdf")
fig.savefig(FIG / "fig5_externalization_break_even.png")
plt.close(fig)
pd.DataFrame({"externalized_fraction": L, "internal_fast_cost": internal_fast, "write_sync_verify": write_sync_verify, "latency_penalty": latency_penalty, "coupled_ledger": coupled, "baseline": baseline}).to_csv(DATA / "fig5_externalization_break_even.csv", index=False)

# -----------------------------
# Figure 6: invariant compression relief plus toy Landauer-calibrated equivalent
# -----------------------------
q_strength = np.linspace(0, 1.0, 240)
raw_load = np.full_like(q_strength, 120.0)
quotient_update = 120 * (1 - 0.80 * q_strength) + 6
protect_cost = 9 + 45 * q_strength**2.25
task_loss = 6 * np.exp(8 * (q_strength - 0.80)) / (1 + np.exp(8 * (q_strength - 0.80)))
quotient_total = quotient_update + protect_cost + 5 * task_loss
savings = raw_load - quotient_total
# Toy energy calibration if the proxy is interpreted as bit/s at 300 K.
raw_power_floor = raw_load * LANDAUER_J_PER_BIT
quot_power_floor = quotient_total * LANDAUER_J_PER_BIT

fig, ax1 = plt.subplots(figsize=(6.6, 4.2))
ax1.plot(q_strength, raw_load, label="raw local representation")
ax1.plot(q_strength, quotient_update, label="quotient update load")
ax1.plot(q_strength, protect_cost, label="protection ledger")
ax1.plot(q_strength, quotient_total, linewidth=1.6, label="quotient total")
idx = np.argmin(quotient_total)
ax1.axvline(q_strength[idx], linestyle="--", color="black", label="optimal quotient")
ax1.fill_between(q_strength, quotient_total, raw_load, where=(savings > 0), alpha=0.10, label="toy relief region")
ax1.set_xlabel("invariant quotient strength / compression")
ax1.set_ylabel("speed-precision ledger proxy")
ax1.set_title("Invariant compression can reduce maintenance burden")
ax1.legend(loc="upper right", ncol=2)
fig.savefig(FIG / "fig6_invariant_compression.pdf")
fig.savefig(FIG / "fig6_invariant_compression.png")
plt.close(fig)
pd.DataFrame({"q_strength": q_strength, "raw_load": raw_load, "quotient_update_load": quotient_update, "protect_cost": protect_cost, "task_loss_penalty": task_loss, "quotient_total": quotient_total, "toy_savings_proxy": savings, "raw_power_floor_J_per_s_at_300K": raw_power_floor, "quotient_power_floor_J_per_s_at_300K": quot_power_floor}).to_csv(DATA / "fig6_invariant_compression.csv", index=False)

# -----------------------------
# Figure 7: regime diagram with failure boundary
# -----------------------------
spd = np.linspace(0, 1.0, 280)
prec = np.linspace(0, 1.0, 280)
S, P = np.meshgrid(spd, prec)  # S speed demand, P precision demand
load = S * (0.30 + 1.35 * P) + 0.12 * P**2
regime = np.zeros_like(load, dtype=int)
regime[(load > 0.32) & (load <= 0.50)] = 1       # high dissipation
regime[(load > 0.50) & (S > P) & (load <= 0.72)] = 2  # externalize
regime[(load > 0.50) & (P >= S) & (load <= 0.72)] = 3 # invariant
regime[(load > 0.72) & (S < 0.68)] = 4           # relax/latency
regime[(load > 0.86)] = 5                        # failure
fig, ax = plt.subplots(figsize=(6.1, 4.8))
im = ax.imshow(regime, origin="lower", extent=[0,1,0,1], aspect="auto", interpolation="nearest")
ax.contour(S, P, load, levels=[0.86], colors="white", linewidths=1.2)
ax.text(0.86, 0.75, "failure\nboundary", color="white", ha="center", fontsize=8)
ax.set_xlabel("maintenance speed demand")
ax.set_ylabel("precision demand")
ax.set_title("P6 speed-precision finite-boundary regimes")
cbar = fig.colorbar(im, ax=ax, ticks=[0,1,2,3,4,5])
cbar.ax.set_yticklabels(["stable", "high-diss", "externalize", "invariant", "relax", "failure"])
ax.text(0.13, 0.15, "stable", color="white")
ax.text(0.53, 0.35, "high\ndiss", color="white", ha="center")
ax.text(0.78, 0.26, "externalize", color="white", ha="center")
ax.text(0.48, 0.77, "invariant\ncompress", color="white", ha="center")
ax.text(0.22, 0.92, "relax", color="white", ha="center")
fig.savefig(FIG / "fig7_regime_diagram.pdf")
fig.savefig(FIG / "fig7_regime_diagram.png")
plt.close(fig)
pd.DataFrame({"speed_demand": S.ravel(), "precision_demand": P.ravel(), "load": load.ravel(), "regime": regime.ravel(), "failure_load_threshold": 0.86}).to_csv(DATA / "fig7_regime_diagram.csv", index=False)

# -----------------------------
# Figure 8: Physical AI worked example normal form
# -----------------------------
stress = np.linspace(0, 1.0, 240)
cloud_llm = 1 - 1/(1 + np.exp(-9*(stress-0.52)))  # high latency collapse under fast stress
external_log = 1 - 0.72/(1 + np.exp(-7*(stress-0.64))) - 0.08*stress
local_reflex = 1 - 0.40/(1 + np.exp(-12*(stress-0.76))) - 0.04*stress
invariant = 1 - 0.34/(1 + np.exp(-12*(stress-0.86))) - 0.02*stress
failure_line = 0.5
fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.plot(stress, cloud_llm, label="cloud LLM controller")
ax.plot(stress, external_log, label="external log / RAG")
ax.plot(stress, local_reflex, label="local feedback / morphology")
ax.plot(stress, invariant, label="invariant-carrier agent")
ax.axhline(failure_line, linestyle=":", color="black", label="task failure line")
ax.axvline(0.86, linestyle="--", color="gray", label="protection-breaking load")
ax.set_xlabel("speed-precision stress")
ax.set_ylabel("boundary task performance proxy")
ax.set_ylim(0,1.05)
ax.set_title("Physical AI: throughput can dominate model capacity")
ax.legend(loc="lower left")
fig.savefig(FIG / "fig8_physical_ai_normal_form.pdf")
fig.savefig(FIG / "fig8_physical_ai_normal_form.png")
plt.close(fig)
pd.DataFrame({"stress": stress, "cloud_llm_controller": cloud_llm, "external_log_agent": external_log, "local_feedback_morphology": local_reflex, "invariant_carrier_agent": invariant, "failure_line": failure_line}).to_csv(DATA / "fig8_physical_ai_normal_form.csv", index=False)

print(f"Generated figures in {FIG}")
print(f"Generated data in {DATA}")
