"""
Generate deterministic synthetic/model figures for FDS-P7 v1.2.
Run from the paper root directory:
    python code/generate_results.py
Outputs figures as PDF/PNG and tables as CSV.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FIG = os.path.join(ROOT, 'figures')
TAB = os.path.join(ROOT, 'tables')
os.makedirs(FIG, exist_ok=True)
os.makedirs(TAB, exist_ok=True)

plt.rcParams.update({
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.labelsize': 9,
    'legend.fontsize': 8,
    'figure.dpi': 150,
})


def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, f'{name}.pdf'), bbox_inches='tight')
    plt.savefig(os.path.join(FIG, f'{name}.png'), bbox_inches='tight')
    plt.close()

# Scalar Hatano-Nelson-like model:
# H(k, theta) = (t+theta)e^{ik} + (t-theta)e^{-ik} + i gamma.
# For E0=i gamma, nonzero theta creates an ellipse enclosing E0 with orientation sign(theta).
def bloch_energy(k, theta, t=1.0, gamma=0.15):
    return (t + theta) * np.exp(1j*k) + (t - theta) * np.exp(-1j*k) + 1j * gamma


def winding_number(theta, t=1.0, gamma=0.15, e0=None, n=2400):
    if e0 is None:
        e0 = 1j * gamma
    k = np.linspace(0, 2*np.pi, n, endpoint=False)
    z = bloch_energy(k, theta, t, gamma) - e0
    if np.min(np.abs(z)) < 1e-8:
        return 0.0
    phase = np.unwrap(np.angle(z))
    return (phase[-1] - phase[0]) / (2*np.pi)


def winding_int(theta):
    if abs(theta) < 1e-4:
        return 0
    w = winding_number(theta)
    return int(np.sign(w)) if abs(w) > 0.45 else 0

def point_gap_margin(theta, t=1.0, gamma=0.15, e0=None, n=2400):
    if e0 is None:
        e0 = 1j * gamma
    k = np.linspace(0, 2*np.pi, n, endpoint=False)
    return float(np.min(np.abs(bloch_energy(k, theta, t, gamma) - e0)))



def obc_matrix(N, theta, t=1.0, gamma=0.15):
    H = 1j * gamma * np.eye(N, dtype=complex)
    for j in range(N-1):
        H[j+1, j] = t + theta
        H[j, j+1] = t - theta
    return H


def binary_entropy(p):
    p = np.clip(p, 1e-12, 1-1e-12)
    return -(p*np.log2(p) + (1-p)*np.log2(1-p))

# Figure 1: quotient sectors and point-gap winding.
ks = np.linspace(0, 2*np.pi, 1000)
fig, axes = plt.subplots(1, 3, figsize=(8.8, 2.65))
for ax, th in zip(axes, [-0.35, 0.0, 0.35]):
    E = bloch_energy(ks, th)
    ax.plot(E.real, E.imag, lw=1.6)
    ax.scatter([0], [0.15], marker='x', s=28, label='$E_0$')
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(rf'$\theta={th:+.2f}$, $q=\nu={winding_int(th)}$')
    ax.set_xlabel(r'Re $E$')
    ax.set_ylabel(r'Im $E$')
    ax.grid(True, alpha=0.25)
axes[0].legend(frameon=False, loc='best')
savefig('fig1_quotient_winding')
pd.DataFrame({'theta':[-0.35,0,0.35], 'Q_inv_winding':[winding_int(x) for x in [-0.35,0,0.35]], 'g_pg':[point_gap_margin(x) for x in [-0.35,0,0.35]]}).to_csv(os.path.join(TAB,'fig1_quotient_winding.csv'), index=False)

# Figure 2: boundary side-ledger / skin localization.
N = 64
fig, ax = plt.subplots(figsize=(4.6, 3.1))
for th in [-0.35, 0.0, 0.35]:
    H = obc_matrix(N, th)
    vals, vecs = np.linalg.eig(H)
    densities = np.abs(vecs)**2
    densities /= np.maximum(np.sum(densities, axis=0, keepdims=True), 1e-12)
    avg = np.mean(densities, axis=1)
    avg /= np.sum(avg)
    ax.plot(np.arange(1, N+1), avg, marker='o', ms=1.9, lw=1.2, label=rf'$\theta={th:+.2f}$')
ax.set_xlabel('site index')
ax.set_ylabel('average right-eigenstate density')
ax.set_title('NHSE boundary side-ledger: skin localization')
ax.legend(frameon=False)
ax.grid(True, alpha=0.25)
savefig('fig2_boundary_side_ledger')
pd.DataFrame({'site':np.arange(1,N+1)}).to_csv(os.path.join(TAB,'fig2_boundary_side_ledger.csv'), index=False)

# Figure 3: noisy invariant recovery / Fano-style bound.
delta = np.linspace(1e-4, 0.49, 220)
V_sizes = [2, 4, 8, 16]
fig, ax = plt.subplots(figsize=(4.6, 3.1))
for m in V_sizes:
    bound = binary_entropy(delta) + delta*np.log2(max(m-1, 1))
    ax.plot(delta, bound, lw=1.6, label=rf'$|\mathcal{{V}}|={m}$')
ax.set_xlabel(r'invariant readout error $\delta$')
ax.set_ylabel(r'upper bound on $H(V\mid Z,\hat Q)$ [bits]')
ax.set_title('Noisy invariant recovery bound')
ax.legend(frameon=False)
ax.grid(True, alpha=0.25)
savefig('fig3_noisy_invariant_bound')
pd.DataFrame({'delta':delta, **{f'bound_V_{m}': binary_entropy(delta)+delta*np.log2(max(m-1,1)) for m in V_sizes}}).to_csv(os.path.join(TAB,'fig3_noisy_invariant_bound.csv'), index=False)

# Figure 4: positive-part forgetting rate and freezing.
T = np.arange(0, 96)
# Conditional uncertainty trajectories, normal-form not direct quantum entropy.
unprotected_H = 8.0*(1 - np.exp(-T/24.0))
protected_H = 0.12 + 0.32*(1 - np.exp(-T/120.0))
broken_H = protected_H.copy()
idx = T >= 45
broken_H[idx] = protected_H[45] + 6.3*(1 - np.exp(-(T[idx]-45)/18.0))
# Positive-part forgetting rates over unit windows.
def pos_rate(arr):
    return np.r_[0, np.maximum(np.diff(arr), 0)]
fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.1))
axes[0].plot(T, unprotected_H, lw=1.7, label='local record only')
axes[0].plot(T, protected_H, lw=1.7, label='with invariant side-ledger')
axes[0].plot(T, broken_H, lw=1.7, label='protection broken')
axes[0].axvline(45, ls='--', lw=1.0)
axes[0].set_xlabel('update step')
axes[0].set_ylabel(r'$H(V_0\mid R_t,q_t)$ [bits]')
axes[0].set_title('Protected task sector remains recoverable')
axes[0].legend(frameon=False)
axes[0].grid(True, alpha=0.25)
axes[1].plot(T, pos_rate(unprotected_H), lw=1.7, label='local')
axes[1].plot(T, pos_rate(protected_H), lw=1.7, label='protected')
axes[1].plot(T, pos_rate(broken_H), lw=1.7, label='broken')
axes[1].axvline(45, ls='--', lw=1.0)
axes[1].set_xlabel('update step')
axes[1].set_ylabel(r'$\kappa^+_{\rm forget}$ proxy')
axes[1].set_title('Nonlinear freezing of forgetting rate')
axes[1].legend(frameon=False)
axes[1].grid(True, alpha=0.25)
savefig('fig4_forgetting_rate_freezing')
pd.DataFrame({'time':T,'H_local':unprotected_H,'H_protected':protected_H,'H_broken':broken_H,'k_local':pos_rate(unprotected_H),'k_protected':pos_rate(protected_H),'k_broken':pos_rate(broken_H)}).to_csv(os.path.join(TAB,'fig4_forgetting_rate_freezing.csv'), index=False)

# Figure 5: resource ledger relocation, not deletion.
abs_theta = np.linspace(0, 0.8, 180)
bulk = 22*np.exp(-3.2*abs_theta) + 4
boundary = 5 + 36*(1 - np.exp(-4.2*abs_theta))
drive = 6 + 18*abs_theta**2
verify = 2 + 8*np.sqrt(abs_theta + 0.02)
total = bulk + boundary + drive + verify
fig, ax = plt.subplots(figsize=(4.7, 3.1))
ax.stackplot(abs_theta, bulk, boundary, drive, verify, labels=['bulk local erasure','boundary concentration','drive/control','verification'], alpha=0.82)
ax.plot(abs_theta, total, lw=1.6, label='coupled resource ledger')
ax.set_xlabel(r'$|\theta|$ / protection strength')
ax.set_ylabel('resource / entropy proxy')
ax.set_title('Relocation, not deletion')
ax.legend(frameon=False, loc='upper left')
ax.grid(True, alpha=0.25)
savefig('fig5_resource_ledger_relocation')
pd.DataFrame({'abs_theta':abs_theta,'bulk':bulk,'boundary':boundary,'drive_control':drive,'verification':verify,'total':total}).to_csv(os.path.join(TAB,'fig5_resource_ledger_relocation.csv'), index=False)

# Figure 6: dual-channel signature.
theta = np.linspace(-0.8, 0.8, 401)
width = 0.055
# Forgetting feature is large near the protection-breaking point where q becomes unreadable/unstable.
forget_feature = 0.12 + 3.2/(1 + np.exp((np.abs(theta)-0.10)/width))
ledger_rate = 28 + 18*np.sqrt(theta**2 + 0.025**2) + 2.0*theta**2
ledger_slope = np.gradient(ledger_rate, theta)
fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.1))
axes[0].plot(theta, forget_feature, lw=1.7)
axes[0].axvline(0, ls='--', lw=1.0)
axes[0].set_title('forgetting-channel crossover / kink')
axes[0].set_xlabel(r'control parameter $\theta$')
axes[0].set_ylabel(r'$\kappa^+_{\rm forget}$ proxy')
axes[0].grid(True, alpha=0.25)
axes[1].plot(theta, ledger_slope, lw=1.7)
axes[1].axvline(0, ls='--', lw=1.0)
axes[1].set_title('ledger-channel slope feature')
axes[1].set_xlabel(r'control parameter $\theta$')
axes[1].set_ylabel(r'$d\dot\Sigma_{\rm ledger}/d\theta$ proxy')
axes[1].grid(True, alpha=0.25)
savefig('fig6_dual_channel_signature')
pd.DataFrame({'theta':theta,'forget_feature':forget_feature,'ledger_rate':ledger_rate,'ledger_slope':ledger_slope}).to_csv(os.path.join(TAB,'fig6_dual_channel_signature.csv'), index=False)

# Figure 7: P4/metastable/P7 transition region.
x = np.linspace(0, 1, 180)  # local perturbation/coarse graining strength
y = np.linspace(0, 1, 180)  # protection gap / invariant margin
X, Y = np.meshgrid(x, y)
R = np.zeros_like(X)
# 0 P4 ordinary forgetting; 1 metastable learning; 2 P7 protected; 3 protection-breaking transition; 4 collapse; 5 externalize/relax.
R[(Y > X + 0.28)] = 2
R[(Y > X + 0.08) & (Y <= X + 0.28)] = 1
R[(np.abs(Y-X) <= 0.08)] = 3
R[(X > Y + 0.08) & (X < 0.74)] = 0
R[(X >= 0.74) & (Y < 0.38)] = 4
R[(X > Y + 0.08) & (Y >= 0.38)] = 5
fig, ax = plt.subplots(figsize=(4.95, 3.55))
im = ax.imshow(R, origin='lower', extent=[0,1,0,1], aspect='auto', interpolation='nearest')
ax.set_xlabel('local perturbation / coarse-graining strength')
ax.set_ylabel('protection gap / invariant margin')
ax.set_title('P4-to-P7 regime diagram')
ax.text(0.50, 0.61, 'Metastable\nLearning\nZone', ha='center', va='center', fontsize=8.5, bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.78))
ax.text(0.50, 0.50, 'Protection-\nbreaking\ntransition', ha='center', va='center', fontsize=8.0, bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.70))
cbar = plt.colorbar(im, ax=ax, ticks=[0,1,2,3,4,5])
cbar.ax.set_yticklabels(['P4 forgetting','metastable learning','P7 protected','transition','collapse','externalize/relax'])
savefig('fig7_regime_diagram_transition')
pd.DataFrame({'perturbation_strength':X.ravel(),'protection_margin':Y.ravel(),'regime':R.ravel()}).to_csv(os.path.join(TAB,'fig7_regime_diagram_transition.csv'), index=False)

# Figure 8: Physical AI normal-form distinction placement.
# Compare volatile memory vs invariant/morphological/sensorimotor structure under local sensor damage.
damage = np.linspace(0, 1, 160)
volatile = 7.5*(1 - np.exp(-4.5*damage))
external_log = 3.0*(1 - np.exp(-2.2*damage)) + 1.2*damage
invariant_agent = 0.4 + 1.5/(1 + np.exp(-15*(damage-0.72)))
fig, ax = plt.subplots(figsize=(4.7, 3.1))
ax.plot(damage, volatile, lw=1.7, label='volatile local memory')
ax.plot(damage, external_log, lw=1.7, label='externalized log')
ax.plot(damage, invariant_agent, lw=1.7, label='invariant/morphological carrier')
ax.axvline(0.72, ls='--', lw=1.0, label='protection-breaking load')
ax.set_xlabel('local sensor / memory damage proxy')
ax.set_ylabel('task-sector uncertainty proxy')
ax.set_title('Physical AI: hard memory by invariant carriers')
ax.legend(frameon=False)
ax.grid(True, alpha=0.25)
savefig('fig8_physical_ai_implication')
pd.DataFrame({'damage_proxy':damage,'volatile_memory':volatile,'external_log':external_log,'invariant_carrier':invariant_agent}).to_csv(os.path.join(TAB,'fig8_physical_ai_implication.csv'), index=False)

print('Generated P7 v1.2 figures and tables in', ROOT)
