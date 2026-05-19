#!/usr/bin/env python3
"""
Generate deterministic normal-form figures for FDS-X5 v1.0.
These demonstrations are conceptual and not empirical fits.
"""
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

np.random.seed(11)
params = {
    "version": "v1.0",
    "seed": 11,
    "num_raw_trajectories": 20,
    "trajectory_steps": 140,
    "law_compression_history_bits": 14000,
    "initial_data_bits": 320,
    "law_bits_base": 110,
    "symmetry_state_count": 112,
    "semigroup_steps": 28,
    "stable_theta": 2.0,
    "drift_amplitude": 0.65,
    "ood_stability_metric": "included in fig2 compression_to_error proxy"
}
(DATA / "simulation_parameters.json").write_text(json.dumps(params, indent=2))
pd.DataFrame([params]).to_csv(DATA / "simulation_parameters.csv", index=False)

# Figure 1: raw histories, strict invariant quotient, equivariant/covariant sector.
t = np.linspace(0, 12, params["trajectory_steps"])
phases = np.linspace(0, 2*np.pi, params["num_raw_trajectories"], endpoint=False)
trajectories = []
strict_invariants = []
eq_x = []
eq_y = []
for k, phi in enumerate(phases):
    noise = 0.07*np.sin(5.3*t + phi) + 0.035*np.cos(9.7*t + 0.3*k)
    amp = 1.0 + 0.08*np.sin(0.5*t + 0.1*k)
    x = amp*np.sin(t + phi) + 0.16*np.sin(2.5*t + 0.5*phi) + noise
    trajectories.append(x)
    dx = np.gradient(x, t)
    inv = np.sqrt(x**2 + dx**2)  # strict-invariant proxy under phase rotation
    strict_invariants.append(pd.Series(inv).rolling(9, center=True, min_periods=1).mean().values)
    # A two-component equivariant/covariant proxy rotates with phase.
    eq_x.append(np.cos(phi)*strict_invariants[-1])
    eq_y.append(np.sin(phi)*strict_invariants[-1])
trajectories = np.array(trajectories)
strict_invariants = np.array(strict_invariants)
eq_radius = np.sqrt(np.mean(np.array(eq_x), axis=0)**2 + np.mean(np.array(eq_y), axis=0)**2)
q_strict = strict_invariants.mean(axis=0)
pd.DataFrame({
    "time": t,
    **{f"x_{i}": trajectories[i] for i in range(trajectories.shape[0])},
    "q_strict_invariant": q_strict,
    "q_equivariant_radius": eq_radius,
}).to_csv(DATA / "fig1_raw_vs_quotient.csv", index=False)
plt.figure(figsize=(7.2,4.4))
for x in trajectories:
    plt.plot(t, x, alpha=0.28, linewidth=0.75)
plt.plot(t, q_strict, linewidth=2.6, label="strict invariant quotient q(t)")
plt.plot(t, eq_radius, linewidth=2.0, linestyle="--", label="equivariant/covariant sector norm")
plt.title("Raw histories compressed into invariant-form sectors")
plt.xlabel("time / update index")
plt.ylabel("state value / compressed sector proxy")
plt.legend(loc="upper right", fontsize=8)
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(FIG / "fig1_raw_histories_invariant_compression.pdf")
plt.savefig(FIG / "fig1_raw_histories_invariant_compression.png", dpi=200)
plt.close()

# Figure 2: law compression ratio and compression-to-error/OOD stability proxies.
form_stability = np.linspace(0.02, 1.0, 150)
L_raw = params["law_compression_history_bits"]
L_data = params["initial_data_bits"]
L_law = params["law_bits_base"] + 190*(1 - form_stability)**2 + 950*(1 - form_stability)**4
compression_ratio = L_raw / (L_law + L_data)
prediction_error = 0.50*(1 - form_stability)**2 + 0.025
ood_stability = 1.0 - 0.72*(1 - form_stability)**1.45
constraint_preservation = 1.0 - 0.85*(1 - form_stability)**2
compression_to_error = compression_ratio / (1 + 20*prediction_error)
pd.DataFrame({
    "form_stability_strength": form_stability,
    "L_raw": L_raw,
    "L_law": L_law,
    "L_data": L_data,
    "compression_ratio": compression_ratio,
    "prediction_error": prediction_error,
    "ood_stability": ood_stability,
    "latent_constraint_preservation": constraint_preservation,
    "compression_to_error_ratio": compression_to_error,
}).to_csv(DATA / "fig2_law_compression_ratio.csv", index=False)
plt.figure(figsize=(7.2,4.4))
plt.plot(form_stability, compression_ratio, label="law compression ratio")
plt.plot(form_stability, compression_to_error, linestyle="--", label="compression-to-error ratio")
plt.plot(form_stability, ood_stability*compression_ratio.max(), linestyle=":", label="OOD stability proxy (scaled)")
plt.title("Invariant-form stability improves law compression")
plt.xlabel("invariant/equivariant/covariant form stability")
plt.ylabel("normalized compression benefit")
plt.legend(fontsize=8)
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(FIG / "fig2_law_compression_ratio.pdf")
plt.savefig(FIG / "fig2_law_compression_ratio.png", dpi=200)
plt.close()

# Figure 3: symmetry/equivariance reduces rule table size.
N = np.arange(4, params["symmetry_state_count"] + 1)
rule_no_form = N**2
rule_strict = (np.ceil(N/4))**2
rule_equiv = N * np.log2(N) * 1.8  # representation law plus local rule
rule_cov = 7*N + 80  # tensor representation / transformation law proxy
rule_top = (np.ceil(np.sqrt(N)))**2
pd.DataFrame({
    "states": N,
    "no_form_compression": rule_no_form,
    "strict_symmetry_orbits": rule_strict,
    "equivariant_representation": rule_equiv,
    "covariant_tensor_rule": rule_cov,
    "structured_quotient_proxy": rule_top,
}).to_csv(DATA / "fig3_symmetry_rule_table_size.csv", index=False)
plt.figure(figsize=(7.2,4.4))
plt.plot(N, rule_no_form, label="no form compression: O(N^2)")
plt.plot(N, rule_strict, label="strict symmetry/orbit quotient")
plt.plot(N, rule_equiv, label="equivariant representation law")
plt.plot(N, rule_cov, label="covariant tensor rule proxy")
plt.plot(N, rule_top, linestyle="--", label="structured quotient proxy")
plt.title("Symmetry, equivariance, and covariance compress rule tables")
plt.xlabel("number of distinguishable states N")
plt.ylabel("rule entries / description proxy")
plt.legend(fontsize=8)
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(FIG / "fig3_symmetry_rule_compression.pdf")
plt.savefig(FIG / "fig3_symmetry_rule_compression.png", dpi=200)
plt.close()

# Figure 4: semigroup/discrete update and exponential compression.
steps = np.arange(params["semigroup_steps"] + 1)
A = np.array([[0.92, 0.07], [-0.04, 0.86]])
q0 = np.array([1.0, 0.35])
qs = [q0]
for _ in steps[1:]:
    qs.append(A @ qs[-1])
qs = np.array(qs)
cont_t = np.linspace(0, params["semigroup_steps"], 260)
cont1 = q0[0]*np.exp(-0.07*cont_t)
cont2 = q0[1]*np.exp(-0.15*cont_t)
pd.DataFrame({"step": steps, "q1_discrete": qs[:,0], "q2_discrete": qs[:,1]}).to_csv(DATA / "fig4_semigroup_discrete.csv", index=False)
pd.DataFrame({"time": cont_t, "q1_exp": cont1, "q2_exp": cont2}).to_csv(DATA / "fig4_semigroup_exponential.csv", index=False)
plt.figure(figsize=(7.2,4.4))
plt.plot(steps, qs[:,0], marker="o", markersize=3, label="discrete update q1: A^t q0")
plt.plot(steps, qs[:,1], marker="o", markersize=3, label="discrete update q2: A^t q0")
plt.plot(cont_t, cont1, linestyle="--", label="continuous generator proxy exp(Lt)")
plt.plot(cont_t, cont2, linestyle="--", label="second exponential mode")
plt.title("Repeated homogeneous updates compress into semigroup form")
plt.xlabel("time / update step")
plt.ylabel("compressed state q")
plt.legend(fontsize=8)
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(FIG / "fig4_semigroup_exponential_compression.pdf")
plt.savefig(FIG / "fig4_semigroup_exponential_compression.png", dpi=200)
plt.close()

# Figure 5: stable constants / dimensionless ratios / drift costs.
x = np.linspace(0, 10, 180)
theta_stable = params["stable_theta"] * np.ones_like(x)
theta_drift = params["stable_theta"] + params["drift_amplitude"]*np.sin(0.8*x) + 0.25*np.sin(2.2*x)
dimensionless_ratio = theta_stable / params["stable_theta"]
extra_bits_drift = np.cumsum(np.abs(np.gradient(theta_drift)))
extra_bits_stable = np.zeros_like(x)
pd.DataFrame({
    "x": x,
    "theta_stable": theta_stable,
    "theta_drift": theta_drift,
    "dimensionless_ratio": dimensionless_ratio,
    "extra_bits_drift": extra_bits_drift,
    "extra_bits_stable": extra_bits_stable,
}).to_csv(DATA / "fig5_constant_invariant_parameter.csv", index=False)
plt.figure(figsize=(7.2,4.4))
plt.plot(x, theta_stable, label="stable parameter theta")
plt.plot(x, theta_drift, label="drifting parameter theta(t)")
plt.plot(x, dimensionless_ratio, linestyle=":", label="dimensionless invariant ratio")
plt.plot(x, extra_bits_drift/extra_bits_drift.max()*3, linestyle="--", label="extra tracking cost proxy")
plt.title("Constants compress by remaining invariant across contexts")
plt.xlabel("context / scale / condition")
plt.ylabel("parameter value / normalized tracking cost")
plt.legend(fontsize=8)
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(FIG / "fig5_constants_as_invariant_parameters.pdf")
plt.savefig(FIG / "fig5_constants_as_invariant_parameters.png", dpi=200)
plt.close()

# Figure 6: Wigner selection diagram as staged filtration.
stages = [
    "all formal\nstructures",
    "finitely\nspecifiable",
    "physically\ninstantiable",
    "form-stable\nunder transformations",
    "law-like\ninvariant-form structures"
]
counts = np.array([10000, 4200, 1100, 260, 65], dtype=float)
pd.DataFrame({"stage": stages, "normal_form_count": counts}).to_csv(DATA / "fig6_wigner_selection.csv", index=False)
plt.figure(figsize=(7.2,4.4))
ypos = np.arange(len(stages))
plt.barh(ypos, counts)
plt.yticks(ypos, stages)
plt.gca().invert_yaxis()
for y, c in zip(ypos, counts):
    plt.text(c + 80, y, f"{int(c)}", va="center", fontsize=8)
plt.title("Physical law selects maintainable invariant-form compressions")
plt.xlabel("normal-form count / measure proxy")
plt.tight_layout()
plt.savefig(FIG / "fig6_wigner_selection_filter.pdf")
plt.savefig(FIG / "fig6_wigner_selection_filter.png", dpi=200)
plt.close()

# Contact sheet.
figs = sorted(FIG.glob("fig*.png"))
cols = 2
rows = int(np.ceil(len(figs)/cols))
plt.figure(figsize=(12, 4.5*rows))
for i, f in enumerate(figs, 1):
    img = plt.imread(f)
    ax = plt.subplot(rows, cols, i)
    ax.imshow(img)
    ax.axis("off")
    ax.set_title(f.stem, fontsize=9)
plt.tight_layout()
plt.savefig(BASE / "contact_sheet_v1_1.png", dpi=180)
plt.close()

print(f"Generated {len(figs)} figures in {FIG}")
