#!/usr/bin/env python3
"""
Generate deterministic algebraic and normal-form figures for FDS-X2 v1.1.
These figures illustrate phase counting and the hard/soft separation; they are not empirical fits.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

params = {
    "N_min": 1,
    "N_max": 8,
    "toy_cost_alpha_fields": 1.0,
    "toy_cost_beta_cp": 0.55,
    "toy_cost_gamma_yukawa": 0.20,
    "toy_cost_delta_stability": 0.10,
    "toy_identity_reward": 3.1,
    "toy_benefit_saturation": "benefit switches on at N=3 and saturates thereafter",
    "notes": "Deterministic algebraic/normal-form demonstrations; not empirical fits or precision flavor constraints."
}
(DATA / "simulation_parameters.json").write_text(json.dumps(params, indent=2), encoding="utf-8")

N = np.arange(params["N_min"], params["N_max"] + 1)
angles = N * (N - 1) / 2
raw_phases = N * (N + 1) / 2
removable_phases = 2 * N - 1
physical_phases = np.maximum((N - 1) * (N - 2) / 2, 0)

book = pd.DataFrame({
    "N_CKM": N,
    "mixing_angles": angles.astype(int),
    "raw_unitary_phases": raw_phases.astype(int),
    "removable_quark_rephasings": removable_phases.astype(int),
    "physical_CP_phases": physical_phases.astype(int),
    "first_irreducible_orientation": (N >= 3).astype(int)
})
book.to_csv(DATA / "ckm_phase_count.csv", index=False)

# Fig 1: CKM phase count.
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(N, physical_phases, marker="o", linewidth=2)
ax.axhline(0, linewidth=1)
ax.axvline(3, linestyle="--", linewidth=1)
ax.scatter([3], [1], s=100, zorder=3)
ax.text(3.08, 1.15, "first irreducible\nCP/T orientation", va="bottom", fontsize=9)
ax.text(1.12, 0.22, "N=1,2:\nno physical\nCKM phase", fontsize=9)
ax.set_xlabel(r"CKM-participating flavor dimension $N_{\rm CKM}$")
ax.set_ylabel(r"physical CP phases $\frac{(N-1)(N-2)}{2}$")
ax.set_title("CKM phase counting gives a hard lower bound")
ax.set_xticks(N)
fig.tight_layout()
fig.savefig(FIG / "fig1_ckm_phase_count.pdf")
fig.savefig(FIG / "fig1_ckm_phase_count.png", dpi=220)
plt.close(fig)

# Fig 2: phase bookkeeping.
book.to_csv(DATA / "unitary_phase_bookkeeping.csv", index=False)
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(N, raw_phases, marker="o", label=r"raw phases in $U(N)$")
ax.plot(N, removable_phases, marker="s", label=r"removable quark rephasings")
ax.plot(N, physical_phases, marker="^", label=r"physical CP phases")
ax.fill_between(N, physical_phases, 0, alpha=0.12)
ax.axvline(3, linestyle="--", linewidth=1)
ax.set_xlabel(r"$N_{\rm CKM}$")
ax.set_ylabel("phase count")
ax.set_title("Rephasing removes all CP phases until N = 3")
ax.legend(fontsize=8, frameon=True)
ax.set_xticks(N)
fig.tight_layout()
fig.savefig(FIG / "fig2_phase_bookkeeping.pdf")
fig.savefig(FIG / "fig2_phase_bookkeeping.png", dpi=220)
plt.close(fig)

# Fig 3: hard/soft map with efficiency shading.
efficiency = []
label = []
for n in N:
    if n < 3:
        efficiency.append(0.15)
        label.append("no\nphysical\nphase")
    elif n == 3:
        efficiency.append(1.0)
        label.append("minimal\nCP/T\nchannel")
    else:
        efficiency.append(max(0.25, 1.0 - 0.11 * (n - 3)))
        label.append("allowed;\nextra\noverhead")
cat_df = pd.DataFrame({"N_CKM": N, "distinction_efficiency_proxy": efficiency, "label": label})
cat_df.to_csv(DATA / "hard_soft_categories.csv", index=False)
fig, ax = plt.subplots(figsize=(6.5, 3.5))
bars = ax.bar(N, efficiency, width=0.78)
for n, b, txt in zip(N, bars, label):
    ax.text(n, min(b.get_height()*0.55, 0.72), txt, ha="center", va="center", fontsize=7)
ax.axvline(2.5, linestyle="--", linewidth=1)
ax.axvline(3.5, linestyle="--", linewidth=1)
ax.text(1.5, 1.10, "algebraically insufficient", ha="center", fontsize=9)
ax.text(3.0, 1.10, "first sufficient point", ha="center", fontsize=9, fontweight='bold')
ax.text(5.8, 1.10, "allowed by algebra;\nupper-bound bridge", ha="center", fontsize=9)
ax.set_ylim(0, 1.28)
ax.set_ylabel("normal-form distinction efficiency")
ax.set_xlabel(r"$N_{\rm CKM}$")
ax.set_xticks(N)
ax.set_title("Hard lower bound vs. higher-risk minimality bridge")
fig.tight_layout()
fig.savefig(FIG / "fig3_hard_soft_map.pdf")
fig.savefig(FIG / "fig3_hard_soft_map.png", dpi=220)
plt.close(fig)

# Fig 4: toy flavor cost with benefit saturation.
alpha = params["toy_cost_alpha_fields"]
beta = params["toy_cost_beta_cp"]
gamma = params["toy_cost_gamma_yukawa"]
delta = params["toy_cost_delta_stability"]
reward = params["toy_identity_reward"]
fields = alpha * N
cp_cost = beta * physical_phases
yukawa_proxy = gamma * (2 * N**2)
stability = delta * np.maximum(N - 3, 0) ** 2
benefit = reward * (N >= 3).astype(float)
total = fields + cp_cost + yukawa_proxy + stability - benefit
cost_df = pd.DataFrame({
    "N_CKM": N,
    "field_cost_proxy": fields,
    "cp_phase_calibration_cost_proxy": cp_cost,
    "yukawa_alignment_cost_proxy": yukawa_proxy,
    "stability_constraint_cost_proxy": stability,
    "identity_orientation_benefit": benefit,
    "toy_total_flavor_cost": total
})
cost_df.to_csv(DATA / "toy_flavor_cost.csv", index=False)
fig, ax = plt.subplots(figsize=(6.8, 4.2))
ax.plot(N, total, marker="o", linewidth=2, label="toy net cost")
ax.plot(N, fields + cp_cost + yukawa_proxy + stability, marker="s", linestyle="--", label="flavor-sector overhead")
ax.plot(N, benefit, marker="^", linestyle=":", label="saturating CP/T-orientation benefit")
ax.axvline(3, linestyle="--", linewidth=1, color='gray', alpha=0.6)
idx3 = list(N).index(3)
ax.plot([3], [total[idx3]], marker='D', markersize=8, color='black', zorder=3)
ax.text(3.15, -0.08, "first sufficient point", fontsize=8, rotation=90, va='bottom')
ax.vlines(3, 0, total[idx3], linestyle=':', linewidth=1, alpha=0.5)
ax.text(3.15, total[idx3] + 0.35, "normal-form\nminimum at N=3", fontsize=9)
ax.set_xlabel(r"$N_{\rm CKM}$")
ax.set_ylabel("normal-form value [arb.]")
ax.set_title("Upper-bound bridge: benefit saturates, overhead grows")
ax.set_xticks(N)
fig.tight_layout()
fig.savefig(FIG / "fig4_toy_flavor_cost.pdf")
fig.savefig(FIG / "fig4_toy_flavor_cost.png", dpi=220)
plt.close(fig)

# Fig 5: chain diagram.
fig, ax = plt.subplots(figsize=(7.0, 4.5))
ax.axis("off")
items = [
    ("FDS identity update", "bridge assumption"),
    ("microscopic T orientation", "CPT"),
    ("CP-asymmetric weak carrier", "KM phase counting"),
    (r"$N_{\mathrm{CKM}} \geq 3$", "hard lower bound"),
    (r"$N_{\mathrm{CKM}} = 3$", "minimality bridge")
]
y_positions = np.linspace(0.88, 0.14, len(items))
for i, ((main, sub), y) in enumerate(zip(items, y_positions)):
    box = FancyBboxPatch((0.18, y-0.055), 0.64, 0.088,
                         boxstyle="round,pad=0.02,rounding_size=0.025",
                         linewidth=1.2, facecolor="white", edgecolor="black")
    ax.add_patch(box)
    ax.text(0.5, y+0.005, main, ha="center", va="center", fontsize=11)
    ax.text(0.5, y-0.028, sub, ha="center", va="center", fontsize=8)
    if i < len(items)-1:
        arr = FancyArrowPatch((0.5, y-0.067), (0.5, y_positions[i+1]+0.048),
                              arrowstyle="-|>", mutation_scale=12, linewidth=1.1)
        ax.add_patch(arr)
ax.text(0.05, 0.49, r"hard$\;$conditional$\;$chain", ha="center", va="center", fontsize=9)
ax.text(0.94, 0.16, r"higher-risk$\;$upper-bound$\;$bridge", ha="center", va="center", fontsize=9)
ax.set_title("X2 hard/soft dependency chain", fontsize=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
fig.tight_layout()
fig.savefig(FIG / "fig5_chain_diagram.pdf")
fig.savefig(FIG / "fig5_chain_diagram.png", dpi=220)
plt.close(fig)

print(f"Generated X2 v1.1 figures and data under {ROOT}")
