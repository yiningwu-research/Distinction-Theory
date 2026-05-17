#!/usr/bin/env python3
"""
Deterministic synthetic simulations for FDS-P5 v0.2.
Generates figures and CSV outputs for the capacity-deficit entropy ledger model.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FIG_DIR = os.path.join(BASE, 'figures')
DATA_DIR = os.path.join(BASE, 'data')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def save_fig(name: str):
    pdf = os.path.join(FIG_DIR, f"{name}.pdf")
    png = os.path.join(FIG_DIR, f"{name}.png")
    plt.tight_layout()
    plt.savefig(pdf, bbox_inches='tight')
    plt.savefig(png, dpi=200, bbox_inches='tight')
    plt.close()

# Fig 1: deficit crossing with zero line and shading
stress = np.linspace(0, 1, 220)
R_min = 35 + 85 * stress**1.25
C_int = 74 - 16 * stress
C_ext_eff = 10 + 18*np.exp(-((stress-0.45)/0.28)**2) - 22*np.clip(stress-0.68,0,None)**2
C_coord = 4 + 18 * stress**2
C_eff = C_int + C_ext_eff - C_coord
Delta = R_min - C_eff
Delta_pos = np.maximum(Delta, 0)
I_corr = Delta_pos / 1.0
sigma_pressure = 8 + 0.16*I_corr + 0.006*I_corr**2
cross_idx = np.argmax(Delta > 0)
cross_stress = stress[cross_idx]

pd.DataFrame({
    'stress': stress, 'R_min': R_min, 'C_eff': C_eff, 'Delta': Delta,
    'Delta_positive': Delta_pos, 'I_corr_min': I_corr, 'sigma_pressure': sigma_pressure
}).to_csv(os.path.join(DATA_DIR,'fig1_deficit_crossing.csv'), index=False)

plt.figure(figsize=(5.2,3.7))
plt.plot(stress, R_min, label=r'task demand $R_{\min}$')
plt.plot(stress, C_eff, label=r'effective capacity $C_{\rm eff}$')
plt.plot(stress, Delta_pos, label=r'positive deficit $[\Delta_\epsilon]_+$')
plt.plot(stress, sigma_pressure, label=r'entropy-pressure proxy')
plt.axvline(cross_stress, linestyle='--', linewidth=1, label='deficit crossing')
plt.fill_between(stress, 0, 130, where=(Delta>0), alpha=0.12)
plt.xlabel('environmental / task stress')
plt.ylabel('bits or entropy-rate proxy')
plt.title('Capacity deficit crossing and entropy-production pressure')
plt.legend(fontsize=7, loc='upper left')
save_fig('fig1_deficit_crossing')

# Fig 2: audit ledger decomposition with unique channel assignments
steps = np.arange(0, 160)
st = steps / steps.max()
info = 3 + 7*np.maximum(st-0.25,0)**1.2
hk = 8 + 12*st + 9*np.maximum(st-0.55,0)**2
meas = 3 + 5*st**1.1
sync = 2 + 10*np.maximum(st-0.45,0)**1.6
ext = 1 + 22*np.exp(-((st-0.72)/0.18)**2)
recovery = 0.5 + 18*np.maximum(st-0.82,0)**2
ledger_total = info + hk + meas + sync + ext + recovery
pd.DataFrame({
    'step': steps, 'info_erasure': info, 'housekeeping': hk, 'measurement': meas,
    'synchronization': sync, 'externalization': ext, 'damage_recovery': recovery,
    'unique_channel_total': ledger_total
}).to_csv(os.path.join(DATA_DIR,'fig2_ledger_decomposition.csv'), index=False)

plt.figure(figsize=(5.2,3.7))
plt.stackplot(steps, info, hk, meas, sync, ext, recovery,
              labels=['info/erase','housekeeping','measurement','sync/verify','externalization','damage/recovery'])
plt.plot(steps, ledger_total, linewidth=1.4, label='audit total')
plt.xlabel('update step')
plt.ylabel(r'unique-channel $\dot\Sigma$ proxy')
plt.title('Generalized entropy-production ledger')
plt.legend(fontsize=6, loc='upper left', ncol=2)
save_fig('fig2_ledger_decomposition')

# Fig 3: pruning ROI with one-time cost and area saving
T = np.arange(0, 180)
base = 20 + 0.16*T + 0.0018*T**2
prune_event = 65
pruning_cost = 42*np.exp(-0.5*((T-prune_event)/4.5)**2)
after_relief = 0.55*(T-prune_event)
after_relief[T < prune_event] = 0
pruned = base + pruning_cost - after_relief
pruned = np.maximum(pruned, 18)
over_task_penalty = 8 + 0.0015*(T-70)**2
roi_cum = np.cumsum(base - pruned)
roi_cum -= np.max([0, roi_cum[0]])
area_saving = np.maximum(base-pruned, 0)
pd.DataFrame({
    'time': T, 'no_pruning_sigma': base, 'task_preserving_pruning_sigma': pruned,
    'one_time_pruning_cost': pruning_cost, 'over_pruning_task_penalty': over_task_penalty,
    'instant_saving': base-pruned, 'cumulative_ROI_proxy': roi_cum
}).to_csv(os.path.join(DATA_DIR,'fig3_pruning_roi.csv'), index=False)

plt.figure(figsize=(5.2,3.7))
plt.plot(T, base, label='no pruning')
plt.plot(T, pruned, label='task-preserving pruning')
plt.plot(T, over_task_penalty, label='over-pruning task loss')
plt.fill_between(T, pruned, base, where=(base>pruned), alpha=0.18, label='future dissipation saving')
plt.axvline(prune_event, linestyle='--', linewidth=1, label='pruning event')
plt.xlabel('time horizon')
plt.ylabel(r'entropy-production or loss proxy')
plt.title('Pruning as dissipation ROI')
plt.legend(fontsize=7, loc='upper left')
save_fig('fig3_pruning_roi')

# Fig 4: externalization local vs coupled ledger
frac = np.linspace(0,1,220)
local = 85*(1-frac)**1.1 + 15
write = 8 + 24*frac
verify_retrieve = 4 + 65*frac**2.3
sync_latency = 3 + 20*frac**1.5
env = 2 + 32*np.maximum(frac-0.55,0)**2
coupled = local + write + verify_retrieve + sync_latency + env
pd.DataFrame({
    'externalized_fraction': frac, 'local_entropy': local,
    'write_entropy': write, 'verify_retrieve_entropy': verify_retrieve,
    'sync_latency_entropy': sync_latency, 'environment_entropy': env,
    'coupled_total_entropy': coupled
}).to_csv(os.path.join(DATA_DIR,'fig4_externalization_audit.csv'), index=False)

plt.figure(figsize=(5.2,3.7))
plt.plot(frac, local, label='local ledger')
plt.plot(frac, write+verify_retrieve+sync_latency+env, label='external overhead')
plt.plot(frac, coupled, label='coupled-system ledger')
plt.axhline(local[0], linestyle=':', linewidth=1, label='initial local cost')
plt.xlabel('fraction of records externalized')
plt.ylabel(r'$\dot\Sigma$ proxy')
plt.title('Externalization is entropy relocation, not deletion')
plt.legend(fontsize=7, loc='upper left')
save_fig('fig4_externalization_audit')

# Fig 5: invariant compression and quotient maintenance
labels = ['raw detail','local rule','modular routine','external log','invariant quotient']
hk_cost = np.array([84, 48, 32, 38, 18], dtype=float)
verify = np.array([12, 14, 16, 23, 9], dtype=float)
task_penalty = np.array([2, 5, 7, 8, 6], dtype=float)
total = hk_cost + verify + task_penalty
pd.DataFrame({'strategy': labels, 'housekeeping': hk_cost, 'verification': verify, 'task_penalty': task_penalty, 'total': total}).to_csv(os.path.join(DATA_DIR,'fig5_invariant_compression.csv'), index=False)

x = np.arange(len(labels))
plt.figure(figsize=(5.4,3.7))
plt.bar(x, hk_cost, label='housekeeping')
plt.bar(x, verify, bottom=hk_cost, label='verification')
plt.bar(x, task_penalty, bottom=hk_cost+verify, label='task penalty')
plt.xticks(x, labels, rotation=18, ha='right')
plt.ylabel('future maintenance entropy proxy')
plt.title('Invariant compression can lower maintenance entropy')
plt.legend(fontsize=7)
save_fig('fig5_invariant_compression')

# Fig 6: deficit-resource phase diagram
D = np.linspace(0, 90, 200)
F = np.linspace(20, 160, 200)
DD, FF = np.meshgrid(D, F)
pressure = 25 + 1.15*DD + 0.008*DD**2
# regime codes: 0 stable, 1 high-diss, 2 prune/externalize, 3 collapse risk
regime = np.zeros_like(DD)
regime[(pressure > FF*0.55) & (pressure <= FF*0.9)] = 1
regime[(pressure > FF*0.9) & (pressure <= FF*1.25)] = 2
regime[pressure > FF*1.25] = 3
pd.DataFrame({'deficit': DD.ravel(), 'resource_input': FF.ravel(), 'regime': regime.ravel()}).to_csv(os.path.join(DATA_DIR,'fig6_phase_diagram.csv'), index=False)

plt.figure(figsize=(5.2,3.8))
cs = plt.contourf(DD, FF, regime, levels=[-0.5,0.5,1.5,2.5,3.5])
plt.xlabel(r'positive deficit $[\Delta_\epsilon]_+$')
plt.ylabel(r'resource input $\dot F_{in}$')
plt.title('Maintenance regimes under deficit and finite resources')
cbar = plt.colorbar(cs, ticks=[0,1,2,3])
cbar.ax.set_yticklabels(['stable','high-dissipation','prune/externalize','collapse risk'])
save_fig('fig6_phase_diagram')

# Fig 7: hysteresis with lost invariants / damage
u = np.linspace(0,1,180)
up_deficit = 90*u
down_deficit = 90*u[::-1]
up_sigma = 12 + 0.9*up_deficit + 0.012*up_deficit**2
lost_invariant_gap = 0.22*up_deficit[::-1] + 13*(1-np.exp(-3*u))
down_sigma = 12 + 0.9*down_deficit + 0.012*down_deficit**2 + lost_invariant_gap
pd.DataFrame({
    'path_position': u, 'deficit_increasing': up_deficit, 'sigma_increasing': up_sigma,
    'deficit_decreasing': down_deficit, 'sigma_decreasing': down_sigma,
    'hysteresis_gap': down_sigma - (12 + 0.9*down_deficit + 0.012*down_deficit**2)
}).to_csv(os.path.join(DATA_DIR,'fig7_hysteresis.csv'), index=False)

plt.figure(figsize=(5.2,3.7))
plt.plot(up_deficit, up_sigma, label='deficit increasing')
plt.plot(down_deficit, down_sigma, label='deficit decreasing after overload')
plt.fill_between(down_deficit, 12 + 0.9*down_deficit + 0.012*down_deficit**2, down_sigma, alpha=0.18, label='record/damage/invariant gap')
plt.xlabel(r'positive deficit $[\Delta_\epsilon]_+$')
plt.ylabel(r'$\dot\Sigma$ proxy')
plt.title('Entropy-production hysteresis after deficit crossing')
plt.legend(fontsize=7, loc='upper left')
save_fig('fig7_hysteresis')

# Contact sheet
from PIL import Image, ImageDraw
pngs = [os.path.join(FIG_DIR, f'fig{i}_{suffix}.png') for i, suffix in [
    (1,'deficit_crossing'),(2,'ledger_decomposition'),(3,'pruning_roi'),
    (4,'externalization_audit'),(5,'invariant_compression'),(6,'phase_diagram'),(7,'hysteresis')]]
thumbs=[]
for p in pngs:
    im = Image.open(p).convert('RGB')
    im.thumbnail((420,300))
    canvas = Image.new('RGB',(440,320),'white')
    canvas.paste(im,((440-im.width)//2,(320-im.height)//2))
    thumbs.append(canvas)
cols, rows = 2, 4
sheet = Image.new('RGB',(cols*440, rows*320),'white')
for i, im in enumerate(thumbs):
    sheet.paste(im, ((i%cols)*440, (i//cols)*320))
sheet.save(os.path.join(BASE,'contact_sheet.jpg'), quality=92)

print(f"Generated figures and data in {BASE}")
