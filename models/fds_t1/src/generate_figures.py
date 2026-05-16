from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from fds_t1_model import (
    default_gaussian_scenario, delayed_observer_scenario, default_binary_scenario,
    gaussian_rate_distortion_dmin, gaussian_rate_required,
    binary_rate_distortion_dmin, transition_indices
)

OUT = Path(__file__).resolve().parents[1] / "figures"
DATA = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)


def savefig(name):
    plt.tight_layout()
    plt.savefig(OUT / f"{name}.png", dpi=220)
    plt.savefig(OUT / f"{name}.pdf")
    plt.close()

# Gaussian finite-observer scenario
t, capacities, cacc, labels = default_gaussian_scenario()
switches = transition_indices(labels)

with open(DATA / "gaussian_capacity_timeseries.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t"] + list(capacities.keys()) + ["Cacc", "active_bottleneck"])
    for i in range(len(t)):
        writer.writerow([t[i]] + [capacities[k][i] for k in capacities] + [cacc[i], labels[i]])

# Fig 1: Capacity bottleneck switching
plt.figure(figsize=(7.2, 4.8))
for name, values in capacities.items():
    plt.plot(t, values, label=name)
plt.plot(t, cacc, linewidth=3.0, label="accessible capacity")
for idx in switches:
    plt.axvline(t[idx], linestyle="--", linewidth=1.0)
plt.xlabel("time")
plt.ylabel("capacity (bits per update window)")
plt.title("Finite-observer accessible capacity as a bottleneck minimum")
plt.legend()
savefig("fig1_capacity_bottleneck_switching")

# Fig 2: Gaussian error floor
sigma2 = 1.0
dmin = gaussian_rate_distortion_dmin(cacc, sigma2=sigma2)
epsilon = 0.004
r_target = gaussian_rate_required(epsilon, sigma2=sigma2)
plt.figure(figsize=(7.2, 4.8))
plt.plot(t, dmin, linewidth=2.5, label="minimal distortion floor")
plt.axhline(epsilon, linestyle="--", linewidth=1.4, label="target distortion")
for idx in switches:
    plt.axvline(t[idx], linestyle="--", linewidth=1.0)
plt.xlabel("time")
plt.ylabel("Gaussian MSE distortion")
plt.title("Rate-distortion error floor under bottleneck collapse")
plt.legend()
savefig("fig2_gaussian_error_floor_kinks")

# Fig 3: Deficit and heat lower bound
delta = np.maximum(r_target - cacc, 0.0)
qdot_kbt_units = np.log(2.0) * delta  # tau=1, units k_B T per update window
with open(DATA / "gaussian_deficit_heat.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t", "R_target_bits", "Cacc_bits", "Delta_FDS_bits", "Qdot_over_kBT"])
    for i in range(len(t)):
        writer.writerow([t[i], r_target, cacc[i], delta[i], qdot_kbt_units[i]])
plt.figure(figsize=(7.2, 4.8))
plt.plot(t, delta, linewidth=2.5, label="capacity deficit")
plt.plot(t, qdot_kbt_units, linewidth=2.5, label="Landauer lower-bound heat rate")
plt.xlabel("time")
plt.ylabel("bits or kBT units per update window")
plt.title("Fixed-distortion deficit and maintenance heat lower bound")
plt.legend()
savefig("fig3_deficit_and_heat_spike")

# Fig 4: Observer-relative entropy divergence
t2, cap2, cacc2, labels2 = delayed_observer_scenario()
H0 = 5.0
s1 = np.maximum(H0 - cacc, 0.0)
s2 = np.maximum(H0 - cacc2, 0.0)
gap = s1 - s2
with open(DATA / "observer_entropy_gap.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t", "S_res_observer_1_bits", "S_res_observer_2_bits", "entropy_gap_bits"])
    for i in range(len(t)):
        writer.writerow([t[i], s1[i], s2[i], gap[i]])
plt.figure(figsize=(7.2, 4.8))
plt.plot(t, gap, linewidth=2.5)
plt.axhline(0.0, linestyle="--", linewidth=1.0)
plt.xlabel("time")
plt.ylabel("observer entropy gap (bits)")
plt.title("Observer-relative entropy divergence under unequal causal access")
savefig("fig4_observer_entropy_divergence")

# Fig 5: Binary-source distortion floor
tb, capb, caccb, labelsb = default_binary_scenario()
dmin_b = binary_rate_distortion_dmin(caccb, p=0.5)
with open(DATA / "binary_distortion_timeseries.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t", "Cacc_bits_per_symbol", "Dmin_hamming"])
    for i in range(len(tb)):
        writer.writerow([tb[i], caccb[i], dmin_b[i]])
plt.figure(figsize=(7.2, 4.8))
plt.plot(tb, dmin_b, linewidth=2.5)
plt.xlabel("time")
plt.ylabel("minimal Hamming distortion")
plt.title("Binary-source error floor under finite accessible capacity")
savefig("fig5_binary_error_floor")

# Fig 6: Minimal no-rescue deficit map
c_grid = np.linspace(0.0, 5.0, 301)
r_grid = np.linspace(0.0, 5.0, 301)
C, R = np.meshgrid(c_grid, r_grid)
Delta = R - C
plt.figure(figsize=(6.2, 5.2))
plt.contourf(C, R, np.maximum(Delta, 0.0), levels=20)
plt.plot(c_grid, c_grid, linewidth=2.2, label="Rmin = Cacc boundary")
plt.xlabel("accessible capacity Cacc")
plt.ylabel("task demand Rmin")
plt.title("Minimal no-rescue deficit map")
plt.legend()
plt.colorbar(label="positive deficit")
savefig("fig6_minimal_deficit_map")
