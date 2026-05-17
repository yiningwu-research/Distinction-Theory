#!/usr/bin/env python3
"""
Generate deterministic synthetic figures for FDS-N1 v0.2.
These are normal-form demonstrations, not fits to empirical systems.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DAT = ROOT / "data"
FIG.mkdir(exist_ok=True)
DAT.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 160,
    "savefig.dpi": 200,
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 7,
})


def savefig(name):
    plt.tight_layout()
    plt.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.savefig(FIG / f"{name}.png", bbox_inches="tight")
    plt.close()

# -----------------------------------------------------------------------------
# Fig. 1: Phase A/B/C time-series normal form with K and maintenance load L_M.
# -----------------------------------------------------------------------------
T = 240
K = np.zeros(T)
LM = np.zeros(T)
Phi = np.zeros(T)
S = np.zeros(T)
Ext = np.zeros(T)
q = np.zeros(T)
ell = np.zeros(T)
Delta = np.zeros(T)
Zclog = np.zeros(T)
K[0] = 18.0
Phi[0] = 160.0
q[0] = 4.0
ell[0] = 8.0
for t in range(T-1):
    stress = 0.45 + 0.006*t + 0.45*np.exp(-((t-95)/28)**2) + 0.25*np.exp(-((t-182)/20)**2)
    Cint_eff = max(8, 80 - 0.16*K[t] - 0.10*ell[t])
    Cext_eff = max(0, 18*Ext[t] - 0.12*Zclog[t]**2 - 1.0*Ext[t])
    Corg = max(0, Cint_eff + Cext_eff - 0.04*K[t] - 0.03*Zclog[t])
    demand = 58 + 17*stress
    Delta[t] = max(0, demand - Corg)
    gate = Phi[t] / (Phi[t] + 38.0)
    S_drive = gate*(0.055*max(K[t]-58,0) + 0.10*max(65-Phi[t],0))
    S[t+1] = max(0, 0.87*S[t] + S_drive)
    Ext_drive = max(Delta[t]-9, 0)*0.020
    Ext[t+1] = np.clip(0.90*Ext[t] + Ext_drive - 0.010*Zclog[t], 0, 14)
    Zclog[t+1] = max(0, 0.94*Zclog[t] + 0.24*Ext[t])
    surv = (0.45*q[t] + 0.06*(1+Delta[t]))/(1+0.03*LM[t]) if t>0 else 0.0
    q[t+1] = np.clip(q[t] + 0.015*surv*(30-q[t]) - 0.006*q[t] + 0.006*S[t], 0, 32)
    growth = 0.17*Delta[t] + 0.012*K[t]*max(Delta[t]-4,0)/20
    pruning = 0.050*S[t]*K[t]/(K[t]+30)
    ext_relief = 0.035*Ext[t]*K[t]/(K[t]+40)
    invariant_comp = 0.018*q[t]
    K[t+1] = max(0, K[t] + growth - pruning - ext_relief - invariant_comp - 0.015*K[t])
    LM[t+1] = max(0, 4 + 0.060*K[t+1]**1.28 - 1.20*q[t+1] - 0.35*Ext[t+1] + 0.04*Zclog[t+1]**2)
    # Phase C resource-loss feedback after a breach.
    resource_in = 5.2/(1+0.012*ell[t])
    Phi[t+1] = Phi[t] + resource_in - 0.34*LM[t+1] - 0.45*S[t+1] - 0.18*Ext[t+1]
    if Phi[t+1] < 35:
        ell[t+1] = ell[t] + 0.60*(35-Phi[t+1])/35 + 0.08*LM[t+1] - 0.55*q[t+1]/30
    else:
        ell[t+1] = max(0, 0.92*ell[t] + 0.030*Delta[t] + 0.015*LM[t+1] - 0.16*S[t+1] - 0.18*q[t+1]/30)
    Phi[t+1] = max(0, min(170, Phi[t+1]))
Delta[-1] = Delta[-2]
LM[0] = max(0, 4 + 0.060*K[0]**1.28 - 1.20*q[0])
fig1 = pd.DataFrame({"t":np.arange(T), "structural_complexity_K":K, "maintenance_load_LM":LM,
                     "resource_Phi":Phi, "pruning_S":S, "externalization_Eext":Ext,
                     "invariant_residue_q":q, "boundary_loss_ell":ell, "capacity_deficit_Delta":Delta,
                     "environmental_clogging_Zext":Zclog})
fig1.to_csv(DAT/"fig1_phase_abc_time_series.csv", index=False)
plt.figure(figsize=(6.4,4.1))
plt.plot(K, label="structural complexity K")
plt.plot(LM, label="maintenance load L_M")
plt.plot(Phi/3, label="resource reserve Phi / 3")
plt.plot(S, label="pruning effort S")
plt.plot(Ext, label="externalization E_ext")
plt.plot(q, label="invariant residue q")
plt.plot(ell, label="boundary loss ell")
plt.axvspan(0, 84, alpha=0.08, label="Phase A")
plt.axvspan(84, 166, alpha=0.07, label="Phase B")
plt.axvspan(166, T, alpha=0.08, label="Phase C risk")
plt.xlabel("update step")
plt.ylabel("normalized units")
plt.title("Phase-A growth, Phase-B regulation, and Phase-C feedback")
plt.legend(ncol=2)
savefig("fig1_phase_abc_time_series")

# -----------------------------------------------------------------------------
# Fig. 2: C_org decomposition and deficit/load pressure.
# -----------------------------------------------------------------------------
stress = np.linspace(0, 1, 160)
Cmem = 85 - 20*stress
Cchannel = 80 - 12*stress
Cupdate = 75 - 25*stress**1.3
Cresource = 90/(1+1.6*stress)
Clat = 82 - 35*stress**1.8
Cver = 78 - 22*stress
Cint_eff = np.minimum.reduce([Cmem, Cchannel, Cupdate, Cresource, Clat, Cver])
Cext_raw = 32*stress
Cext_eff = Cext_raw - 9*stress - 7*stress**2 - 6/(1+np.exp(-12*(stress-0.72)))
Cext_eff = np.maximum(Cext_eff, 0)
Ccoord = 4 + 9*stress**2
Corg = Cint_eff + Cext_eff - Ccoord
Rmin = 58 + 42*stress
Delta2 = np.maximum(Rmin - Corg, 0)
load_pressure = 6 + 0.16*Delta2 + 0.012*Delta2**2
pd.DataFrame({"stress":stress, "Cint_eff":Cint_eff, "Cext_eff":Cext_eff, "Ccoord":Ccoord,
              "Corg":Corg, "Rmin":Rmin, "Delta_N1":Delta2, "maintenance_load_pressure":load_pressure}).to_csv(DAT/"fig2_corg_deficit.csv", index=False)
plt.figure(figsize=(6.4,4.0))
plt.plot(stress, Rmin, label="task demand R_min")
plt.plot(stress, Cint_eff, label="internal bottleneck capacity")
plt.plot(stress, Cext_eff, label="effective external capacity")
plt.plot(stress, Corg, label="C_org after coordination costs")
plt.plot(stress, Delta2, label="capacity deficit Delta_N1")
plt.plot(stress, load_pressure, label="load pressure")
plt.xlabel("environmental / task stress")
plt.ylabel("bits, capacity, or load proxy")
plt.title("Operationalizing organizational capacity and deficit")
plt.legend(ncol=2)
savefig("fig2_corg_deficit")

# -----------------------------------------------------------------------------
# Fig. 3: Pruning viability window.
# -----------------------------------------------------------------------------
p = np.linspace(0, 1.0, 160)
K_final = 95*np.exp(-1.9*p) + 12
under_overload = 55*np.exp(-6*p)
over_prune = 80/(1+np.exp(-14*(p-0.62)))
ell_final = 8 + under_overload + over_prune
Phi_min = 105 - 0.45*ell_final - 0.08*K_final + 14*np.exp(-((p-0.35)/0.18)**2)
q_res = 8 + 45*p*np.exp(-1.2*p)
pd.DataFrame({"pruning_strength":p, "final_K":K_final, "final_boundary_loss":ell_final,
              "minimum_resource_Phi":Phi_min, "invariant_residue":q_res}).to_csv(DAT/"fig3_pruning_window.csv", index=False)
plt.figure(figsize=(6.2,4.0))
plt.plot(p, ell_final, label="final boundary loss ell (U-shaped)")
plt.plot(p, K_final, label="final structural complexity K")
plt.plot(p, Phi_min, label="minimum resource reserve Phi")
plt.plot(p, q_res, label="invariant residue q")
plt.axvspan(0.20, 0.52, alpha=0.12, label="viability window")
plt.xlabel("pruning strength")
plt.ylabel("loss, load, or resource proxy")
plt.title("Pruning has a viability window")
plt.legend()
savefig("fig3_pruning_viability_window")

# -----------------------------------------------------------------------------
# Fig. 4: Externalization with environmental clogging.
# -----------------------------------------------------------------------------
f = np.linspace(0, 1, 180)
Z = 1.8*f**1.5/(1+0.6*f)
local_pressure = 100*(1-f)**1.25 + 5
write_sync = 8 + 14*f + 20*f**2
verify_retrieve = 5 + 10*Z + 45*Z**2
latency = 6/(1+np.exp(-16*(f-0.68))) + 12*f**2
raw_ext = 95*f
Cext_eff = raw_ext - write_sync - verify_retrieve - latency
pd.DataFrame({"externalized_fraction":f, "environmental_clogging_Zext":Z, "local_pressure":local_pressure,
              "write_sync_cost":write_sync, "verify_retrieve_cost":verify_retrieve, "latency_penalty":latency,
              "effective_external_capacity":Cext_eff}).to_csv(DAT/"fig4_externalization_clogging_roi.csv", index=False)
plt.figure(figsize=(6.4,4.0))
plt.plot(f, local_pressure, label="local maintenance pressure")
plt.plot(f, write_sync, label="write/sync cost")
plt.plot(f, verify_retrieve, label="verify/retrieve cost from clogging")
plt.plot(f, latency, label="latency penalty")
plt.plot(f, Cext_eff, label="C_ext^eff")
plt.axhline(0, linestyle="--", linewidth=0.8)
plt.xlabel("fraction of load externalized")
plt.ylabel("cost or capacity proxy")
plt.title("Externalization shifts load and can clog the environment")
plt.legend(ncol=2)
savefig("fig4_externalization_clogging_roi")

# -----------------------------------------------------------------------------
# Fig. 5: Bounded self-organization regimes with Phase C.
# -----------------------------------------------------------------------------
r = np.linspace(0.2, 2.4, 160)
Fin = np.linspace(15, 165, 150)
R, F = np.meshgrid(r, Fin)
score = np.zeros_like(R)
score[(F > 115*R + 20)] = 0  # Phase A sustainable growth / slack
score[(F <= 115*R + 20) & (F > 72*R + 22)] = 1  # Phase B maintenance/pruning
score[(F <= 72*R + 22) & (F > 46*R + 16)] = 2  # externalization/compression
score[(F <= 46*R + 16)] = 3  # Phase C/collapse risk
pd.DataFrame({"garbage_or_deficit_rate":R.ravel(), "resource_input":F.ravel(), "regime":score.ravel()}).to_csv(DAT/"fig5_phase_abc_regimes.csv", index=False)
plt.figure(figsize=(5.8,4.2))
cf = plt.contourf(R, F, score, levels=[-0.5,0.5,1.5,2.5,3.5], alpha=0.9)
cbar = plt.colorbar(cf, ticks=[0,1,2,3])
cbar.ax.set_yticklabels(["Phase A slack", "Phase B regulate", "externalize/compress", "Phase C risk"])
plt.contour(R, F, score, levels=[0.5,1.5,2.5], colors="k", linewidths=0.6)
plt.xlabel("deficit / novelty pressure")
plt.ylabel("resource input F_in")
plt.title("Bounded self-organization regimes")
savefig("fig5_phase_abc_regimes")

# -----------------------------------------------------------------------------
# Fig. 6: T3-style survival score for invariant residues.
# -----------------------------------------------------------------------------
names = np.array(["raw detail", "local rule", "modular routine", "external log", "skill", "invariant q"])
maint = np.array([82, 55, 38, 46, 28, 14], dtype=float)
verify = np.array([18, 15, 12, 26, 10, 8], dtype=float)
refresh = np.array([24, 20, 13, 16, 9, 6], dtype=float)
boundary_u = np.array([28, 45, 58, 48, 66, 72], dtype=float)
pred_u = np.array([20, 36, 48, 42, 58, 64], dtype=float)
score_surv = (boundary_u + pred_u)/(maint + verify + refresh + 1e-6)
prob = np.exp(1.3*score_surv); prob = prob/prob.sum()
pd.DataFrame({"structure":names, "maintenance_cost":maint, "verification_cost":verify,
              "refresh_cost":refresh, "boundary_utility":boundary_u, "predictive_utility":pred_u,
              "survival_score":score_surv, "selection_probability":prob}).to_csv(DAT/"fig6_invariant_selection_score.csv", index=False)
plt.figure(figsize=(6.5,4.0))
x = np.arange(len(names))
plt.bar(x-0.18, score_surv, width=0.36, label="survival score S(phi)")
plt.bar(x+0.18, 10*prob, width=0.36, label="selection probability x10")
plt.xticks(x, names, rotation=25, ha="right")
plt.ylabel("score or scaled probability")
plt.title("Phase-B residue selection favors useful low-maintenance invariants")
plt.legend()
savefig("fig6_invariant_selection_score")

# -----------------------------------------------------------------------------
# Fig. 7: Active-boundary ablation criterion.
# -----------------------------------------------------------------------------
t = np.arange(80)
normal = 18*np.exp(-t/45) + 8 + 3*np.sin(t/12)
frozen = 18 + 0.22*t + 3*np.sin(t/13)
random = 22 + 0.14*t + 7*np.abs(np.sin(t/7))
passive = 16 + 0.02*t
pd.DataFrame({"t":t, "normal_update":normal, "frozen_update":frozen,
              "randomized_update":random, "passive_structure":passive}).to_csv(DAT/"fig7_active_boundary_ablation.csv", index=False)
plt.figure(figsize=(6.3,4.0))
plt.plot(t, normal, label="normal do(U)")
plt.plot(t, frozen, label="freeze do(U_empty)")
plt.plot(t, random, label="randomize update")
plt.plot(t, passive, label="passive stable structure")
plt.xlabel("future time")
plt.ylabel("boundary-maintenance loss")
plt.title("Active-boundary ablation criterion")
plt.legend()
savefig("fig7_active_boundary_ablation")

# -----------------------------------------------------------------------------
# Fig. 8: Domain bridge mapping table rendered as figure.
# -----------------------------------------------------------------------------
domains = ["Protocell", "Neural", "Robot", "Organization", "Civilization"]
cols = ["Boundary B", "Loss ell", "Update U", "Pruning S", "Externalization", "Invariant q"]
rows = [
    ["membrane/gradients", "leakage", "metabolic repair", "reaction pruning", "niche cues", "autocatalytic motif"],
    ["control/report", "prediction loss", "plasticity/attention", "forget/sleep", "tools/notes", "skill/concept"],
    ["safety/task", "damage/failure", "controller update", "cache/policy prune", "maps/cloud", "robust policy"],
    ["institution", "coordination loss", "rule update", "bureaucracy trim", "archives/ledgers", "norm/procedure"],
    ["law/culture", "collapse/drift", "governance", "reform/simplify", "libraries/web", "culture meme"],
]
pd.DataFrame(rows, columns=cols, index=domains).to_csv(DAT/"fig8_domain_bridge_template.csv")
fig, ax = plt.subplots(figsize=(9.0,3.8))
ax.axis('off')
table = ax.table(cellText=rows, rowLabels=domains, colLabels=cols, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(7)
table.scale(1.0, 1.45)
for (row, col), cell in table.get_celld().items():
    if row == 0 or col == -1:
        cell.set_text_props(weight='bold')
    cell.set_linewidth(0.5)
ax.set_title("Domain bridge template: examples are mappings, not proofs", pad=10)
savefig("fig8_domain_bridge_template")

print(f"Generated figures and data in {ROOT}")
