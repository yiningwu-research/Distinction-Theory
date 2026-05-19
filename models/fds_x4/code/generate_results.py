#!/usr/bin/env python3
"""Generate deterministic normal-form figures for FDS-X4 v1.1.

The figures are conceptual/algebraic demonstrations, not empirical fits.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

BASE = Path(__file__).resolve().parents[1]
FIG = BASE / "figures"
DATA = BASE / "data"
FIG.mkdir(exist_ok=True, parents=True)
DATA.mkdir(exist_ok=True, parents=True)

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "figure.dpi": 160,
    "savefig.bbox": "tight",
})

# Figure 1: occupancy algebra
n = np.arange(0, 11)
fermion_allowed = (n <= 1).astype(int)
boson_allowed = np.ones_like(n)
fig, ax = plt.subplots(figsize=(6.0, 3.2))
ax.step(n, boson_allowed + 0.08, where="mid", linewidth=2, label="bosonic mode allowed")
ax.step(n, fermion_allowed - 0.08, where="mid", linewidth=2, label="fermionic address allowed")
ax.scatter([0, 1], [fermion_allowed[0] - 0.08, fermion_allowed[1] - 0.08], s=35)
ax.scatter(n, boson_allowed + 0.08, s=18)
ax.set_ylim(-0.35, 1.35)
ax.set_yticks([0, 1])
ax.set_yticklabels(["forbidden", "allowed"])
ax.set_xticks(n)
ax.set_xlabel("occupation number $n_i$")
ax.set_title("Exclusive fermionic occupancy vs bosonic mode occupation")
ax.legend(loc="center right")
ax.grid(True, alpha=0.25)
fig.savefig(FIG / "fig1_occupancy_algebra.pdf")
fig.savefig(FIG / "fig1_occupancy_algebra.png")
plt.close(fig)
pd.DataFrame({"n": n, "fermion_allowed": fermion_allowed, "boson_allowed": boson_allowed}).to_csv(DATA / "occupancy_algebra.csv", index=False)

# Figure 2: address diversity under filling + ambiguity cost + verification error rate
M = 18
N = np.arange(0, 41)
fermion_div = np.minimum(N, M)
boson_div = np.ones_like(N, dtype=float)
boson_div[0] = 0
boson_div += 0.08 * np.log1p(N)
boson_div = np.minimum(boson_div, M)
p2_div = np.ceil(N / 2).clip(0, M)
p4_div = np.ceil(N / 4).clip(0, M)
# normal-form collision bookkeeping cost; zero for p=1
amb_p2 = N * np.log2(2)
amb_p4 = N * np.log2(4)
# verification error rate under fixed bandwidth (grows with collisions per address)
beta = 0.06
collisions_p2 = N - p2_div  # extra events beyond first per address
collisions_p4 = N - p4_div
error_p2 = 1 - np.exp(-beta * collisions_p2)
error_p4 = 1 - np.exp(-beta * collisions_p4)
fig, ax = plt.subplots(figsize=(6.2, 3.6))
ax.plot(N, fermion_div, linewidth=2, label="Pauli $p=1$: $D_1(N)=N$")
ax.plot(N, p2_div, linestyle="--", linewidth=2, label=r"finite cutoff $p=2$: $\lceil N/2\rceil$")
ax.plot(N, p4_div, linestyle="-.", linewidth=2, label=r"finite cutoff $p=4$: $\lceil N/4\rceil$")
ax.plot(N, boson_div, linestyle=":", linewidth=2, label="bosonic ground-mode toy")
ax.axhline(M, linestyle="--", linewidth=1)
ax.text(1, M + 0.4, "available addresses M", fontsize=8)
ax.set_xlabel("occupancy events N")
ax.set_ylabel("occupied addresses D(N)")
ax.set_title("Address diversity and multi-occupancy ambiguity cost")
ax.grid(True, alpha=0.25)
ax2 = ax.twinx()
ax2.plot(N, amb_p2, linestyle="--", linewidth=1.2, alpha=0.6, label=r"normal-form $C_{amb}(p=2)$")
ax2.plot(N, amb_p4, linestyle=":", linewidth=1.2, alpha=0.6, label=r"normal-form $C_{amb}(p=4)$")
ax2.plot(N[::2], error_p2[::2], linestyle="--", linewidth=1.0, alpha=0.35, color="gray", marker="s", markersize=2.5, label=r"verification error rate $p=2$")
ax2.plot(N[::2], error_p4[::2], linestyle=":", linewidth=1.0, alpha=0.35, color="gray", marker="o", markersize=2.5, label=r"verification error rate $p=4$")
ax2.set_ylabel("ambiguity / error rate [arb.]")
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines + lines2, labels + labels2, loc="upper left", fontsize=7)
fig.savefig(FIG / "fig2_address_diversity.pdf")
fig.savefig(FIG / "fig2_address_diversity.png")
plt.close(fig)
pd.DataFrame({
    "N": N,
    "fermion_diversity_p1": fermion_div,
    "p2_diversity": p2_div,
    "p4_diversity": p4_div,
    "boson_diversity_toy": boson_div,
    "ambiguity_cost_p2": amb_p2,
    "ambiguity_cost_p4": amb_p4,
    "verification_error_p2": error_p2,
    "verification_error_p4": error_p4,
}).to_csv(DATA / "address_diversity.csv", index=False)

# Figure 3: atomic shell cartoon
shells = ["1s", "2s", "2p", "3s", "3p", "4s"]
capacities = np.array([2, 2, 6, 2, 6, 2])
electrons = 18
remaining = electrons
fermion_fill = []
for c in capacities:
    f = min(c, remaining)
    fermion_fill.append(f)
    remaining -= f
boson_fill = np.array([electrons, 0, 0, 0, 0, 0])
x = np.arange(len(shells))
width = 0.35
fig, ax = plt.subplots(figsize=(6.2, 3.4))
ax.bar(x - width / 2, fermion_fill, width, label="Pauli shell filling")
ax.bar(x + width / 2, boson_fill, width, label="ground-collapse toy contrast")
ax.set_xticks(x)
ax.set_xticklabels(shells)
ax.set_ylabel("electrons assigned")
ax.set_title("Forced shell diversity vs address-collapse toy contrast")
ax.legend()
ax.grid(True, axis="y", alpha=0.25)
fig.savefig(FIG / "fig3_shell_filling.pdf")
fig.savefig(FIG / "fig3_shell_filling.png")
plt.close(fig)
pd.DataFrame({"shell": shells, "capacity": capacities, "pauli_fill": fermion_fill, "ground_collapse_toy": boson_fill}).to_csv(DATA / "shell_filling.csv", index=False)

# Figure 4: degeneracy pressure normal form
rho = np.logspace(-2, 2, 200)
P_nonrel = rho ** (5/3)
P_rel = 0.35 * rho ** (4/3)
P_no_ex = np.zeros_like(rho)
fig, ax = plt.subplots(figsize=(6.0, 3.4))
ax.loglog(rho, P_nonrel, linewidth=2, label=r"fermion degeneracy $P\propto n^{5/3}$")
ax.loglog(rho, P_rel, linestyle="--", linewidth=2, label=r"relativistic trend $P\propto n^{4/3}$")
ax.loglog(rho, P_no_ex + 1e-3, linestyle=":", linewidth=2, label="no-exclusion toy floor")
ax.set_xlabel("number density n [normalized]")
ax.set_ylabel("pressure [normalized]")
ax.set_title("Degeneracy pressure as macroscopic address protection")
ax.legend(loc="upper left")
ax.grid(True, which="both", alpha=0.25)
fig.savefig(FIG / "fig4_degeneracy_pressure.pdf")
fig.savefig(FIG / "fig4_degeneracy_pressure.png")
plt.close(fig)
pd.DataFrame({"density": rho, "P_nonrel": P_nonrel, "P_rel": P_rel, "P_no_exclusion": P_no_ex}).to_csv(DATA / "degeneracy_pressure.csv", index=False)

# Figure 5: stability scaling
N2 = np.arange(1, 301)
E_ferm = -1.0 * N2
E_no = -0.08 * (N2 ** (5/3))
E_super = -0.02 * (N2 ** 2)
fig, ax = plt.subplots(figsize=(6.0, 3.4))
ax.plot(N2, E_ferm, linewidth=2, label=r"stable matter: $E\gtrsim -C N$")
ax.plot(N2, E_no, linestyle="--", linewidth=2, label=r"collapse-prone toy: $E\sim -C N^{5/3}$")
ax.plot(N2, E_super, linestyle=":", linewidth=2, label=r"stronger collapse toy: $E\sim -C N^2$")
ax.set_xlabel("fermionic occupancy events N")
ax.set_ylabel("energy scale [normalized]")
ax.set_title("Stability scaling with and without address protection")
ax.legend(loc="lower left")
ax.grid(True, alpha=0.25)
fig.savefig(FIG / "fig5_stability_scaling.pdf")
fig.savefig(FIG / "fig5_stability_scaling.png")
plt.close(fig)
pd.DataFrame({"N": N2, "E_fermion": E_ferm, "E_no_exclusion": E_no, "E_supercollapse": E_super}).to_csv(DATA / "stability_scaling.csv", index=False)

# Figure 6: physical dependency chain
fig, ax = plt.subplots(figsize=(4.2, 6.4))
ax.axis("off")
labels = [
    "finite quantum\naddress",
    "$({a_i^\\dagger})^2=0$\nnilpotent occupancy",
    "forced address\ndiversity",
    "shell structure +\nchemical diversity",
    "bulk matter\nstability",
    "degeneracy pressure +\ncompact support",
]
y_positions = np.linspace(0.90, 0.18, len(labels))
x0 = 0.50
box_w = 0.82
box_h = 0.11
for i, (y0, lab) in enumerate(zip(y_positions, labels)):
    ax.add_patch(Rectangle((x0 - box_w/2, y0 - box_h/2), box_w, box_h, fill=False, linewidth=1.6))
    ax.text(x0, y0, lab, ha="center", va="center", fontsize=10)
    if i < len(labels) - 1:
        ax.add_patch(FancyArrowPatch((x0, y0 - box_h/2 - 0.008), (x0, y_positions[i+1] + box_h/2 + 0.008), arrowstyle="->", mutation_scale=14, linewidth=1.4))
ax.text(0.5, 0.045, "X4: collision-free fermionic address protection", ha="center", fontsize=11)
fig.savefig(FIG / "fig6_address_protection_flow.pdf")
fig.savefig(FIG / "fig6_address_protection_flow.png")
plt.close(fig)

meta = {
    "description": "Deterministic normal-form demonstrations for FDS-X4 v1.1. Values are conceptual/algebraic, not empirical fits.",
    "figures": [
        "fig1_occupancy_algebra",
        "fig2_address_diversity",
        "fig3_shell_filling",
        "fig4_degeneracy_pressure",
        "fig5_stability_scaling",
        "fig6_address_protection_flow",
    ],
    "available_addresses_M": M,
    "shell_demo_electrons": electrons,
    "address_diversity_bound": "D_p(N) >= ceil(N/p); Pauli case p=1 gives D_1(N)=N when sufficient addresses exist.",
    "ambiguity_cost": "Normal-form C_amb(N,p) proportional to N log2 p, not empirical thermodynamic data.",
}
(DATA / "model_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(f"Generated figures and data under {BASE}")
