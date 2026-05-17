#!/usr/bin/env python3
"""
Deterministic simulations for FDS-O1 v0.2.

These simulations are synthetic demonstrations. They do not use human-subject,
proprietary, or experimental detector data. Their purpose is to make the
finite-register model operational and reproducible.
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

np.random.seed(42)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def savefig(name):
    plt.tight_layout()
    plt.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.savefig(FIG / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close()


def sim_dynamic_bottlenecks():
    """Dynamic coupling among sensor, channel, memory, record stability and update."""
    u = np.linspace(0, 100, 401)
    # Task demand rises with scene complexity / sampling burden.
    R_task = 2.4 + 0.072 * u

    # Sampling is increased as task complexity rises, but this increases inflow.
    sampling_effort = 0.25 + 0.75 * sigmoid((u - 35) / 12)
    C_sens = 3.0 + 7.0 * sampling_effort - 0.006 * u

    # Channel is fixed and worsens slightly with overhead; compression is triggered
    # as the channel becomes stressed.
    C_chan_raw = 7.1 - 0.0035 * u
    compression = np.clip((R_task - C_chan_raw) / 3.0, 0, 1.4)
    C_chan_eff = C_chan_raw + 1.8 * compression

    # Compression is not free. It consumes update bandwidth and reduces stable
    # record fidelity.
    C_update = 8.9 - 1.7 * compression - 0.006 * u
    C_rec = 8.4 - 1.05 * compression - 0.010 * u

    # Buffer/memory fill is driven by inflow after channel/compression and drained by update.
    fill = np.zeros_like(u)
    du = u[1] - u[0]
    for i in range(1, len(u)):
        inflow = max(R_task[i] - C_chan_eff[i], 0)
        drain = max(C_update[i] - 5.4, 0) * 0.45
        fill[i] = min(5.0, max(0.0, fill[i-1] + du * (0.16 * inflow - 0.08 * drain)))
    C_mem = 8.2 - 0.55 * fill
    C_ext = 7.6 + 0.014 * u - 0.6 * sigmoid((u - 82) / 7)  # external overhead grows late

    caps = np.vstack([C_sens, C_chan_eff, C_mem, C_rec, C_update, C_ext])
    labels = np.array(["sensor", "channel+compression", "memory", "record", "update", "external"])
    C_meas = caps.min(axis=0)
    bottleneck = labels[caps.argmin(axis=0)]
    deficit = R_task - C_meas

    df = pd.DataFrame({
        "complexity": u,
        "R_task": R_task,
        "C_sens": C_sens,
        "C_chan_eff": C_chan_eff,
        "C_mem": C_mem,
        "C_rec": C_rec,
        "C_update": C_update,
        "C_ext": C_ext,
        "C_meas": C_meas,
        "deficit": deficit,
        "compression": compression,
        "buffer_fill": fill,
        "bottleneck": bottleneck,
    })
    df.to_csv(DATA / "dynamic_bottlenecks.csv", index=False)

    plt.figure(figsize=(8.7, 5.6))
    plt.plot(u, R_task, linewidth=2.3, label="task demand")
    for y, lab in [(C_sens, "sensor"), (C_chan_eff, "channel + compression"),
                   (C_mem, "memory"), (C_rec, "record stability"),
                   (C_update, "update throughput"), (C_ext, "external access")]:
        plt.plot(u, y, linewidth=1.0, alpha=0.75, label=lab)
    plt.plot(u, C_meas, linewidth=2.8, linestyle="--", label="accessible measurement capacity")
    crossing_idx = np.where(deficit > 0)[0]
    if len(crossing_idx):
        x0 = u[crossing_idx[0]]
        plt.axvline(x0, linestyle=":", linewidth=1.8)
        plt.text(x0 + 1.5, min(R_task)-0.15, "budget crossing", rotation=90, va="bottom")
    plt.xlabel("scene / task complexity")
    plt.ylabel("usable bits per measurement window")
    plt.title("Dynamic bottleneck coupling in a finite measurement register")
    plt.legend(fontsize=7, ncol=2)
    plt.grid(alpha=0.25)
    savefig("fig1_dynamic_bottleneck_coupling")

    plt.figure(figsize=(8.7, 4.8))
    plt.plot(u, deficit, linewidth=2.2, label="capacity deficit")
    plt.plot(u, compression, linewidth=2.0, label="compression strength")
    plt.plot(u, fill, linewidth=2.0, label="memory/buffer fill")
    plt.axhline(0, linewidth=1.0)
    plt.xlabel("scene / task complexity")
    plt.ylabel("dimensionless diagnostic value")
    plt.title("Compression compensates for channel limits but pushes memory and record constraints")
    plt.legend()
    plt.grid(alpha=0.25)
    savefig("fig2_coupled_diagnostics")

    return df


def sim_buffering():
    """Transient vs sustained crossing with finite buffer."""
    t = np.linspace(0, 220, 441)
    C_meas = 6.2 + 0 * t
    # Background plus a short transient pulse and a sustained pulse.
    R = 5.3 + 0.8 * np.exp(-0.5 * ((t - 55) / 9) ** 2) + 1.75 * sigmoid((t - 120)/4) - 1.2 * sigmoid((t - 182)/6)
    deficit = R - C_meas
    pos_def = np.maximum(deficit, 0)
    Bmax = 18.0
    drain = 0.045
    B = np.zeros_like(t)
    overflow = np.zeros_like(t)
    dt = t[1] - t[0]
    for i in range(1, len(t)):
        candidate = B[i-1] + dt * (pos_def[i] - drain * max(C_meas[i] - R[i], 0))
        if candidate > Bmax:
            overflow[i] = candidate - Bmax
            B[i] = Bmax
        else:
            B[i] = max(0, candidate)
    latency = 1.0 + 0.05 * B + 0.20 * overflow
    error_index = 0.02 + 0.12 * overflow + 0.018 * np.maximum(B - 0.8*Bmax, 0)

    df = pd.DataFrame({"time": t, "R_task": R, "C_meas": C_meas, "deficit": deficit,
                       "positive_deficit": pos_def, "buffer_occupancy": B, "overflow": overflow,
                       "latency_index": latency, "error_index": error_index})
    df.to_csv(DATA / "buffering_transient_sustained.csv", index=False)

    fig, axes = plt.subplots(3, 1, figsize=(8.7, 7.2), sharex=True)
    axes[0].plot(t, R, label="task demand")
    axes[0].plot(t, C_meas, label="measurement capacity")
    axes[0].set_ylabel("bits/window")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.25)
    axes[1].plot(t, B, label="buffer occupancy")
    axes[1].axhline(Bmax, linestyle=":", label="buffer capacity")
    axes[1].set_ylabel("bit-window buffer")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.25)
    axes[2].plot(t, latency, label="latency index")
    axes[2].plot(t, error_index, label="error/merge index")
    axes[2].set_xlabel("time")
    axes[2].set_ylabel("observable signature")
    axes[2].legend(fontsize=8)
    axes[2].grid(alpha=0.25)
    fig.suptitle("Buffers smooth transient budget crossing but sharpen sustained overflow", y=0.995)
    savefig("fig3_buffering_transient_vs_sustained")
    return df


def sim_heat_tradeoff():
    """Fixed memory repeated erase vs expanding memory reversible/low-erasure operation."""
    t = np.linspace(0, 140, 281)
    input_bits = 3.2 + 0.045 * t + 1.8 * sigmoid((t - 80) / 8)
    fixed_mem = 6.5
    # Fixed-memory observer erases/overwrites surplus above memory capacity.
    erase_fixed = np.maximum(input_bits - fixed_mem, 0)
    heat_fixed = 0.20 * input_bits + 1.25 * erase_fixed
    # Expanding-memory observer postpones erasure by allocating physical storage.
    memory_growth = np.cumsum(np.maximum(input_bits - fixed_mem, 0)) * (t[1]-t[0]) * 0.08
    erase_expand = 0.18 * np.maximum(memory_growth - 30, 0)  # late garbage collection only
    heat_expand = 0.20 * input_bits + 0.38 * erase_expand
    spatial_cost = memory_growth

    df = pd.DataFrame({"time": t, "input_bits": input_bits, "erase_fixed": erase_fixed,
                       "heat_fixed_units": heat_fixed, "memory_growth": memory_growth,
                       "erase_expanding": erase_expand, "heat_expanding_units": heat_expand,
                       "spatial_cost": spatial_cost})
    df.to_csv(DATA / "heat_reversible_vs_rewrite.csv", index=False)

    fig, axes = plt.subplots(2, 1, figsize=(8.7, 6.6), sharex=True)
    axes[0].plot(t, heat_fixed, linewidth=2.3, label="fixed memory: repeated overwrite")
    axes[0].plot(t, heat_expand, linewidth=2.3, label="expanding memory: delayed erasure")
    axes[0].set_ylabel(r"heat floor $(k_B T\ln2)$ units")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.25)
    axes[1].plot(t, erase_fixed, label="irreversible erasure, fixed memory")
    axes[1].plot(t, spatial_cost / 10, label="physical storage cost / 10, expanding memory")
    axes[1].plot(t, erase_expand, label="late garbage collection, expanding memory")
    axes[1].set_xlabel("time / acquisition load")
    axes[1].set_ylabel("diagnostic units")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.25)
    fig.suptitle("Housekeeping heat separates reversible sensing from irreversible record reuse", y=0.995)
    savefig("fig4_housekeeping_heat_reversible_vs_fixed")
    return df


def gaussian_blob(X, Y, x0, y0, amp=1.0, sigma=2.0):
    return amp * np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * sigma**2))


def sim_sensor_array():
    """2D sensor-array demonstration of finite update capacity causing false merging/ghosting."""
    n = 64
    x = np.arange(n)
    y = np.arange(n)
    X, Y = np.meshgrid(x, y)
    # Four moving objects at an instant: two are close enough to merge under coarse observation.
    objects = [(18, 22, 1.0, 2.2), (25, 24, 0.95, 2.2), (45, 18, 0.85, 2.5), (42, 45, 0.75, 2.7)]
    true_img = np.zeros((n, n))
    for xo, yo, amp, sig in objects:
        true_img += gaussian_blob(X, Y, xo, yo, amp, sig)
    true_img /= true_img.max()

    # High-capacity observer: near-native resolution, low latency.
    high_obs = true_img + 0.02 * np.random.randn(n, n)
    high_obs = np.clip(high_obs, 0, None)

    # Low-capacity observer: block averaging + rolling ghost from previous frame.
    prev_objects = [(14, 20, 0.5, 3.1), (21, 23, 0.50, 3.1), (47, 16, 0.45, 3.2), (38, 43, 0.42, 3.4)]
    prev_img = np.zeros((n, n))
    for xo, yo, amp, sig in prev_objects:
        prev_img += gaussian_blob(X, Y, xo, yo, amp, sig)
    low_pre = 0.75 * true_img + 0.25 * prev_img
    block = 4
    low_small = low_pre.reshape(n//block, block, n//block, block).mean(axis=(1, 3))
    low_obs = np.kron(low_small, np.ones((block, block)))
    low_obs += 0.01 * np.random.randn(n, n)
    low_obs = np.clip(low_obs, 0, None)

    # Thresholded tracker output: connected coarse regions. We emulate merged tracks with simple mask.
    mask_high = high_obs > 0.28
    mask_low = low_obs > 0.28
    # Track count proxy: local maxima count after coarse gridding.
    def count_peaks(img, thresh=0.28):
        count = 0
        coords = []
        for i in range(3, n-3):
            for j in range(3, n-3):
                window = img[i-2:i+3, j-2:j+3]
                if img[i, j] == window.max() and img[i, j] > thresh:
                    # non-max suppress by distance
                    if all((i-ci)**2 + (j-cj)**2 > 7**2 for ci, cj in coords):
                        coords.append((i, j)); count += 1
        return count, coords
    high_count, high_peaks = count_peaks(high_obs)
    low_count, low_peaks = count_peaks(low_obs)

    summary = pd.DataFrame({
        "observer": ["true", "high_capacity", "low_capacity"],
        "stable_record_classes": [len(objects), high_count, low_count],
        "update_budget_relative": [np.nan, 1.0, 0.34],
        "false_merge_index": [0, max(0, len(objects)-high_count), max(0, len(objects)-low_count)]
    })
    summary.to_csv(DATA / "sensor_array_summary.csv", index=False)

    fig, axes = plt.subplots(1, 4, figsize=(11.2, 3.1))
    panels = [(true_img, "latent scene\n4 moving objects"), (high_obs, "high-capacity record"),
              (low_obs, "low-capacity record\ncoarse + delayed"), (mask_low.astype(float), "stable coarse classes\nmerged/ghosted")]
    for ax, (img, title) in zip(axes, panels):
        ax.imshow(img, origin="lower", interpolation="nearest")
        ax.set_title(title, fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("2D sensor-array budget crossing: finite update capacity causes false merging", y=1.02)
    savefig("fig5_sensor_array_false_merging")
    return summary


def sim_decoherence_interface():
    """Operational record threshold vs decoherence-like environmental information growth."""
    t = np.linspace(0, 10, 501)
    H_branch = 1.0
    tau_d = 1.25
    I_env = H_branch * (1 - np.exp(-t / tau_d))
    thresholds = [0.35, 0.65, 0.90]
    record_curves = []
    data = {"time": t, "I_environment": I_env}
    plt.figure(figsize=(8.3, 5.0))
    plt.plot(t, I_env, linewidth=2.8, label="environmental branch information")
    for th in thresholds:
        # finite apparatus access saturates below/above threshold after a stabilization lag
        tau_rec = t[np.argmax(I_env >= th)] if np.any(I_env >= th) else np.nan
        stab = th * (1 - np.exp(-np.maximum(t - tau_rec, 0) / 0.8)) if not np.isnan(tau_rec) else np.zeros_like(t)
        data[f"record_capacity_{th:.2f}"] = stab
        plt.plot(t, stab, linestyle="--", label=f"stable accessible record, threshold={th:.2f}")
        if not np.isnan(tau_rec):
            plt.axvline(tau_rec, linestyle=":", linewidth=1.0)
    plt.xlabel("time in decoherence units")
    plt.ylabel("bits about branch state")
    plt.title("Interface with decoherence: operational records require finite accessible stabilization")
    plt.legend(fontsize=8)
    plt.grid(alpha=0.25)
    savefig("fig6_decoherence_record_interface")
    df = pd.DataFrame(data)
    df.to_csv(DATA / "decoherence_record_interface.csv", index=False)
    return df


def main():
    dfs = {
        "dynamic_bottlenecks": sim_dynamic_bottlenecks(),
        "buffering": sim_buffering(),
        "heat_tradeoff": sim_heat_tradeoff(),
        "sensor_array": sim_sensor_array(),
        "decoherence_interface": sim_decoherence_interface(),
    }
    summary = pd.DataFrame({
        "simulation": list(dfs.keys()),
        "rows": [len(df) for df in dfs.values()],
        "output_file": [
            "dynamic_bottlenecks.csv",
            "buffering_transient_sustained.csv",
            "heat_reversible_vs_rewrite.csv",
            "sensor_array_summary.csv",
            "decoherence_record_interface.csv",
        ]
    })
    summary.to_csv(DATA / "o1_v2_summary.csv", index=False)
    print("Generated FDS-O1 v0.2 figures and CSV outputs in", ROOT)


if __name__ == "__main__":
    main()
