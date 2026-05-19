#!/usr/bin/env python3
"""
Deterministic normal-form demonstrations for FDS-Q1 v1.2.
These figures are conceptual normal forms only, not quantum dynamical simulations
and not empirical fits. They document the quantitative definitions used in the
paper: boundary-promotion entropy, finite-access reconstruction, redundancy
thresholds, and record-availability timing.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "figure.titlesize": 12,
})


def savefig(name: str) -> None:
    for ext in ["pdf", "png"]:
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=230)
    plt.close()


def h2_binary(p: float) -> float:
    p = np.clip(p, 1e-12, 1-1e-12)
    return float(-(p*np.log2(p) + (1-p)*np.log2(1-p)))


def sigmoid(x):
    return 1/(1+np.exp(-x))

# ---------------------------------------------------------------------
# Figure 1: causal map / record-boundary diagram
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.3, 3.9))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6.6)
ax.axis("off")


def box(x, y, w, h, label, fc="white", lw=1.1, ls="-"):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="black", lw=lw, linestyle=ls)
    ax.add_patch(patch)
    ax.text(x+w/2, y+h/2, label, ha="center", va="center")
    return patch


def arrow(x1, y1, x2, y2, label=None, style="->", ls="-", rad=0.0):
    arr = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=12,
                          lw=1.15, linestyle=ls, color="black",
                          connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(arr)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2+0.22, label, ha="center", va="center")

# Sealed lab boundary and accessible domains
lab = FancyBboxPatch((0.7, 1.0), 5.8, 4.7, boxstyle="round,pad=0.12", fc="#f5f5f5", ec="black", lw=1.3, linestyle="--")
ax.add_patch(lab)
ax.text(3.6, 5.45, "friend-lab boundary", ha="center", va="center")
box(1.05, 3.25, 1.10, 0.72, "system\nS", "#e8f1ff")
box(2.55, 3.22, 1.28, 0.78, "friend\nF", "#eaffea")
box(4.25, 3.08, 1.22, 1.02, "internal\nrecord z_F", "#fff2cc")
box(4.10, 1.55, 1.62, 0.75, "environment\nfragments E_i", "#eeeeff")
box(7.35, 3.2, 1.28, 0.78, "Wigner\nW", "#ffecec")
box(7.15, 1.58, 1.75, 0.74, "accessible\nrecord z_W", "#fff2cc")

arrow(2.15, 3.62, 2.55, 3.62, "interaction")
arrow(3.83, 3.62, 4.25, 3.62, "writes")
arrow(5.45, 3.5, 7.35, 3.55, "limited channel", ls="--")
arrow(5.0, 3.05, 5.0, 2.3, "leakage", ls="--")
arrow(5.72, 1.93, 7.15, 1.95, "sampled fragments", ls="--")
arrow(7.98, 3.2, 8.0, 2.32, "readout")

ax.text(5.15, 0.72, r"finite-capacity cut: promote only if $H_2(Z_F|Z_W)\leq \epsilon$", ha="center", va="center")
ax.text(5.15, 0.28, "Record-boundary mismatch is not inferred coherence; coherence requires isolation assumptions.", ha="center", va="center", fontsize=8)
plt.tight_layout()
savefig("fig1_record_boundary_causal_map")

# ---------------------------------------------------------------------
# Figure 2: boundary-promotion condition and mismatch entropy
# Normal form: I/H = 1-exp(-lambda x), M/H = exp(-lambda x)
# ---------------------------------------------------------------------
x = np.linspace(0, 1, 301)
lam = 4.2
I_over_H = 1 - np.exp(-lam*x)
M_over_H = np.exp(-lam*x)
err_proxy = M_over_H  # schematic lower-bound proxy, not exact Fano inversion
epsilon = 0.08
pd.DataFrame({
    "leakage_strength": x,
    "I_over_H": I_over_H,
    "mismatch_entropy_over_H": M_over_H,
    "schematic_error_proxy": err_proxy,
    "epsilon": epsilon,
}).to_csv(DATA/"boundary_promotion_condition.csv", index=False)

fig, ax = plt.subplots(figsize=(7.0, 3.45))
ax.plot(x, M_over_H, label=r"mismatch $H_2(Z_F|Z_W)/H_2(Z_F)=e^{-\lambda x}$")
ax.plot(x, I_over_H, label=r"access $I_2(Z_F;Z_W)/H_2(Z_F)=1-e^{-\lambda x}$")
ax.axhline(epsilon, color="black", ls="--", lw=1, label=r"promotion tolerance $\epsilon$")
ax.fill_between(x, 0, 1, where=(M_over_H<=epsilon), alpha=0.12, label="promotable region")
ax.set_xlabel("cross-boundary leakage / communication strength x")
ax.set_ylabel("normalized information quantity")
ax.set_title("Boundary-promotion condition: friend record becomes Wigner-accessible only after mismatch falls")
ax.set_ylim(-0.03, 1.05)
ax.grid(True, alpha=0.25)
ax.legend(loc="center right")
savefig("fig2_boundary_promotion")

# ---------------------------------------------------------------------
# Figure 3: decoherence vs record availability
# ---------------------------------------------------------------------
t = np.linspace(0, 10, 400)
D_env = 1 - np.exp(-1.35*t)                 # distinguishability leakage into environment
Crec_F = sigmoid(5.2*(t-1.2))               # friend internal record stabilizes early
W_access = sigmoid(2.6*(t-5.4))             # Wigner access opens later
record_F = np.minimum(D_env, Crec_F)
record_W = np.minimum(D_env, W_access)
threshold = 0.72
pd.DataFrame({
    "time": t,
    "environmental_distinguishability": D_env,
    "friend_record_stability": Crec_F,
    "wigner_boundary_access": W_access,
    "friend_record_condition": record_F,
    "wigner_record_condition": record_W,
    "threshold": threshold,
}).to_csv(DATA/"decoherence_vs_record_availability.csv", index=False)

fig, ax = plt.subplots(figsize=(7.0, 3.55))
ax.plot(t, D_env, label=r"environmental distinguishability $D_{ij}(t)$")
ax.plot(t, Crec_F, label=r"friend record stability $C^F_{rec}(t)$")
ax.plot(t, W_access, label=r"Wigner boundary access $I_2(Z_F;Z_W)$ proxy")
ax.plot(t, record_W, ls="--", label="Wigner operational record condition")
ax.axhline(threshold, color="black", ls=":", lw=1.1, label="task threshold")
ax.set_xlabel("time [normalized units]")
ax.set_ylabel("normalized diagnostic")
ax.set_title("Decoherence, internal record stability, and external record availability can occur at different times")
ax.set_ylim(-0.02, 1.05)
ax.grid(True, alpha=0.25)
ax.legend(loc="lower right")
savefig("fig3_decoherence_vs_record_availability")

# ---------------------------------------------------------------------
# Figure 4: three-bit toy model and finite-access reconstruction
# ---------------------------------------------------------------------
p0 = 0.70
H_ZF = h2_binary(p0)
R = np.arange(0, 21)
lam_R = 0.22
I_R = H_ZF * (1 - np.exp(-lam_R*R))
M_R = H_ZF * np.exp(-lam_R*R)
# finite Wigner capacity cap example
C_W = 0.55
I_cap = np.minimum(I_R, C_W)
M_cap = H_ZF - I_cap
# simple Fano-compatible lower-bound proxy for binary case: Pe >= h2^{-1}(Hcond), approximate by grid
ps = np.linspace(1e-5, 0.5, 5000)
h_grid = -(ps*np.log2(ps)+(1-ps)*np.log2(1-ps))
Pe_lower = np.interp(np.minimum(M_cap, 1.0), h_grid, ps)

pd.DataFrame({
    "redundancy_fragments": R,
    "H_ZF_bits": H_ZF,
    "I_unlimited_bits": I_R,
    "mismatch_unlimited_bits": M_R,
    "C_W_bits": C_W,
        "record_availability_horizon_definition": "tau_RAH = inf{t: I_2(Z_internal;Z_external(t)) >= H_2(Z_internal)-epsilon}",
    "I_capped_bits": I_cap,
    "mismatch_capped_bits": M_cap,
    "fano_binary_error_lower_proxy": Pe_lower,
}).to_csv(DATA/"three_bit_toy_model.csv", index=False)

fig, ax = plt.subplots(figsize=(7.0, 3.6))
ax.plot(R, M_R, marker="o", ms=3, label=r"mismatch $M_{F|W}$, no capacity cap")
ax.plot(R, M_cap, marker="s", ms=3, label=rf"mismatch with $C_W={C_W:.2f}$ bits cap")
ax.plot(R, Pe_lower, marker="^", ms=3, label="Fano-style error lower proxy")
ax.axhline(H_ZF, color="black", lw=0.8, ls=":", label=rf"$H_2(Z_F)={H_ZF:.3f}$ bits for $p_0=0.70$")
ax.set_xlabel("environmental redundancy fragments $R_E$")
ax.set_ylabel("bits or probability proxy")
ax.set_title("Three-bit toy model: redundancy lowers mismatch, finite Wigner capacity leaves residual uncertainty")
ax.set_ylim(-0.03, 1.05)
ax.grid(True, alpha=0.25)
ax.legend(loc="upper right")
savefig("fig4_three_bit_toy_model")

# ---------------------------------------------------------------------
# Figure 5: boundary-promotion lattice / regimes
# Normal form: eta = I/H = 1 - exp(-lambda*x); mismatch = 1 - eta
# ---------------------------------------------------------------------
x2 = np.linspace(0, 1, 500)
eta = 1 - np.exp(-4.2*x2)
M = 1 - eta
eps_norm = 0.10
partial_cut = 1 - eps_norm
fig, ax = plt.subplots(figsize=(7.0, 2.9))
ax.plot(x2, eta, lw=1.8, label=r"promotion strength $\eta_{F\to W}=I_2/H_2$")
ax.plot(x2, M, lw=1.4, ls="--", label=r"mismatch $M_{F|W}/H_2=1-\eta$")
ax.axhline(partial_cut, color="black", ls=":", lw=1.1, label=r"promotion threshold $1-\epsilon/H_2$")
ax.fill_between(x2, 0, eta, where=(eta < 0.15), alpha=0.10)
ax.fill_between(x2, 0, eta, where=((eta >= 0.15) & (eta < partial_cut)), alpha=0.10)
ax.fill_between(x2, 0, eta, where=(eta >= partial_cut), alpha=0.14)
ax.text(0.06, 0.12, "no\npromotion", ha="center", va="center")
ax.text(0.45, 0.45, "partial leakage /\ntransition", ha="center", va="center")
ax.text(0.86, 0.88, "Wigner-promotable\nrecord", ha="center", va="center")
ax.set_xlabel("cross-boundary record availability coordinate x")
ax.set_ylabel("normalized information")
ax.set_title("Boundary-promotion lattice: from internal record to Wigner-promotable fact")
ax.set_ylim(-0.03, 1.05)
ax.grid(True, alpha=0.2)
ax.legend(loc="lower right", fontsize=7)
pd.DataFrame({
    "availability_coordinate": x2,
    "promotion_strength_eta": eta,
    "mismatch_over_H": M,
    "epsilon_over_H": eps_norm,
}).to_csv(DATA/"promotion_lattice.csv", index=False)
savefig("fig5_boundary_alignment_regimes")

# ---------------------------------------------------------------------
# Figure 6: relation map / quantum technology diagnostics
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.3, 4.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis("off")

def rbox(x, y, w, h, label, fc="white"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="black", lw=1.05)
    ax.add_patch(p)
    ax.text(x+w/2, y+h/2, label, ha="center", va="center")
    return p

rbox(4.0, 6.0, 2.0, 0.6, "FDS Core")
rbox(3.75, 5.0, 2.5, 0.6, "T1 finite budgets")
rbox(3.75, 4.0, 2.5, 0.6, "O1 finite register")
rbox(3.55, 3.0, 2.9, 0.65, "Q1 finite record\nboundaries", "#fff2cc")
rbox(0.55, 1.9, 2.2, 0.72, "P3/P4\nside records + loss")
rbox(3.55, 1.9, 2.9, 0.72, "Q2 scalable quantum\ncomputation costs")
rbox(7.05, 1.9, 2.3, 0.72, "P7 invariant\nside ledgers")
rbox(2.0, 0.65, 2.4, 0.72, "device metrics:\nT1, T2, tau_rec")
rbox(5.55, 0.65, 2.75, 0.72, "record metrics:\ntau_RAH, C_rec, I_int/ext")

def arr_pts(a, b):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=12, lw=1.05))

arr_pts((5,6.0),(5,5.6)); arr_pts((5,5.0),(5,4.6)); arr_pts((5,4.0),(5,3.65));
arr_pts((4.3,3.0),(2.2,2.62)); arr_pts((5,3.0),(5,2.62)); arr_pts((5.9,3.0),(7.8,2.62))
arr_pts((4.5,1.9),(3.2,1.37)); arr_pts((5.55,1.9),(6.95,1.37))
ax.text(5,0.18,"Q1 separates coherence preservation, internal stability, record availability horizon, and erasure history.",ha="center",fontsize=8)
savefig("fig6_relation_and_device_metrics")

# ---------------------------------------------------------------------
# Summary JSON with formulas / values
# ---------------------------------------------------------------------
summary = {
    "normal_form_status": "schematic, not quantum dynamical simulation",
    "boundary_promotion_formula": "I/H = 1 - exp(-lambda*x), M/H = exp(-lambda*x)",
    "lambda_x": lam,
    "logistic_agreement_formula": "P_agree(x) = 1/(1+exp(-a*(x-x_c)))",
    "toy_model": {
        "p0": p0,
        "H_ZF_bits": H_ZF,
        "lambda_R": lam_R,
        "C_W_bits": C_W,
        "record_availability_horizon_definition": "tau_RAH = inf{t: I_2(Z_internal;Z_external(t)) >= H_2(Z_internal)-epsilon}",
        "mismatch_at_R0_bits": float(M_cap[0]),
        "mismatch_at_R20_bits": float(M_cap[-1]),
    },
}
(DATA/"model_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(f"Generated figures in {FIG}")
print(f"Generated data in {DATA}")
