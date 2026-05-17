#!/usr/bin/env python3
"""
Generate deterministic synthetic simulations for FDS-O2 v0.2.
These simulations are illustrative finite-register diagnostics, not fits to clock,
cosmological, detector, or human-subject data.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

np.random.seed(42)


def savefig(name: str):
    plt.tight_layout()
    plt.savefig(FIG / f"{name}.pdf")
    plt.savefig(FIG / f"{name}.png", dpi=220)
    plt.close()


# ---------------------------------------------------------------------
# Fig. 1: finite history, finite register, and non-injectivity / arrow strength.
# ---------------------------------------------------------------------
steps = np.arange(0, 101)
input_bits = 0.36 + 0.16 * np.sin(steps / 8.0) + 0.006 * steps
input_bits = np.clip(input_bits, 0.10, None)
history_bits = np.cumsum(input_bits)
capacity = np.full_like(steps, 18.0, dtype=float)
retained_bits = np.minimum(history_bits, capacity)
lost_bits = np.maximum(history_bits - capacity, 0.0)
# For a uniform toy code, compatible histories scale as 2^(lost bits).
noninjectivity_bits = lost_bits
arrow_strength = noninjectivity_bits / (retained_bits + 1.0)
heat_floor_units = noninjectivity_bits

pd.DataFrame({
    "step": steps,
    "input_bits": input_bits,
    "cumulative_history_bits": history_bits,
    "finite_register_capacity_bits": capacity,
    "retained_record_bits": retained_bits,
    "noninjectivity_loss_bits_H_past_given_record": noninjectivity_bits,
    "arrow_strength_loss_over_retained": arrow_strength,
    "minimum_erasure_heat_units_kBTln2": heat_floor_units,
}).to_csv(DATA / "fig1_history_register_noninjectivity.csv", index=False)

fig, ax1 = plt.subplots(figsize=(7.4, 4.6))
ax1.plot(steps, history_bits, label="cumulative history demand")
ax1.plot(steps, capacity, linestyle="--", label="finite register capacity")
ax1.plot(steps, retained_bits, label="retained record bits")
ax1.plot(steps, noninjectivity_bits, label="lost past bits H(past|record)")
ax1.set_xlabel("update index")
ax1.set_ylabel("bits")
ax2 = ax1.twinx()
ax2.plot(steps, arrow_strength, linestyle=":", label="arrow-strength index")
ax2.set_ylabel("loss / retained")
idx = np.argmax(history_bits > capacity)
if history_bits[idx] > capacity[idx]:
    ax1.axvline(steps[idx], linestyle=":", label="first non-injective overwrite")
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, fontsize=8, loc="upper left")
plt.title("Finite register time: memory fill increases non-injectivity")
savefig("fig1_history_register_noninjectivity")


# ---------------------------------------------------------------------
# Fig. 2: fixed memory versus append-only logging.
# ---------------------------------------------------------------------
T = np.arange(0, 131)
write_rate = 0.55 + 0.004 * T + 0.08 * np.sin(T / 11.0)
write_rate = np.clip(write_rate, 0.2, None)
fixed_capacity = 28.0
written = np.cumsum(write_rate)
fixed_memory = np.minimum(written, fixed_capacity)
fixed_erasure = np.maximum(written - fixed_capacity, 0.0)
append_memory = written.copy()
gc_start = 90
gc_rate = 0.85
append_late_erasure = np.maximum(T - gc_start, 0) * gc_rate
append_memory_after_gc = np.maximum(append_memory - append_late_erasure, 0.0)
fixed_heat = fixed_erasure
append_immediate_heat = 0.18 * append_late_erasure  # delayed cleanup, not immediate overwrite

pd.DataFrame({
    "time": T,
    "fixed_memory_bits": fixed_memory,
    "fixed_overwrite_bits": fixed_erasure,
    "append_memory_after_gc_bits": append_memory_after_gc,
    "append_late_gc_bits": append_late_erasure,
    "fixed_heat_units_kBTln2": fixed_heat,
    "append_delayed_heat_units_kBTln2": append_immediate_heat,
}).to_csv(DATA / "fig2_overwrite_vs_append.csv", index=False)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.4, 5.8), sharex=True)
ax1.plot(T, fixed_memory, label="fixed memory: retained log")
ax1.plot(T, append_memory_after_gc, label="append/expanded memory after GC")
ax1.axhline(fixed_capacity, linestyle="--", label="fixed capacity")
ax1.set_ylabel("stored bits")
ax1.legend(fontsize=8)
ax2.plot(T, fixed_erasure, label="fixed memory: cumulative overwrite")
ax2.plot(T, append_late_erasure, label="expanded memory: delayed cleanup")
ax2.plot(T, fixed_heat, linestyle="--", label="fixed heat floor")
ax2.plot(T, append_immediate_heat, linestyle=":", label="delayed heat proxy")
ax2.axvline(gc_start, linestyle=":", label="late cleanup begins")
ax2.set_xlabel("update time")
ax2.set_ylabel("bits / heat units")
ax2.legend(fontsize=8)
plt.suptitle("Append-only logging delays erasure; finite memory forces overwrite")
savefig("fig2_overwrite_vs_append")


# ---------------------------------------------------------------------
# Fig. 3: latency-induced apparent causal inversion.
# ---------------------------------------------------------------------
n_events = 160
true_times = 0.22 * np.arange(n_events, dtype=float)
base_latency = 0.45 + 0.18 * np.sin(true_times / 2.5)
load = 8.0 * np.exp(-0.5 * ((true_times - 19.5) / 2.6) ** 2) + 5.0 * np.exp(-0.5 * ((true_times - 27.0) / 1.5) ** 2)
jitter = 0.23 * np.sin(true_times / 0.75) + 0.07 * np.cos(true_times / 0.33)
latency = np.clip(base_latency + load + jitter, 0.0, None)
recorded_times = true_times + latency
window = 26
local_inversions = np.zeros(n_events, dtype=int)
max_latency_gap_violation = np.zeros(n_events)
for i in range(n_events):
    jmax = min(n_events, i + window + 1)
    inv = 0
    violation = 0.0
    for j in range(i + 1, jmax):
        gap = true_times[j] - true_times[i]
        diff = latency[i] - latency[j]
        if diff > gap:
            inv += 1
            violation = max(violation, diff - gap)
    local_inversions[i] = inv
    max_latency_gap_violation[i] = violation

pd.DataFrame({
    "event_index": np.arange(n_events),
    "source_time": true_times,
    "latency": latency,
    "recorded_time": recorded_times,
    "local_order_inversions": local_inversions,
    "max_latency_gap_violation": max_latency_gap_violation,
}).to_csv(DATA / "fig3_latency_causal_inversion.csv", index=False)

fig, ax1 = plt.subplots(figsize=(7.4, 4.6))
ax1.plot(true_times, latency, label="load-dependent latency")
ax1.plot(true_times, max_latency_gap_violation, linestyle=":", label="max inversion margin")
ax1.set_xlabel("source time")
ax1.set_ylabel("time units")
ax2 = ax1.twinx()
ax2.plot(true_times, local_inversions, linestyle="--", label="local apparent causal inversions")
ax2.set_ylabel("inversions in local window")
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, fontsize=8, loc="upper left")
plt.title("Latency can make recorded order differ from causal source order")
savefig("fig3_latency_causal_inversion")


# ---------------------------------------------------------------------
# Fig. 4: finite clock precision.
# ---------------------------------------------------------------------
N = 650
rng = np.random.default_rng(7)
inter_arrivals = rng.exponential(scale=0.8, size=N)
inter_arrivals[250:360] *= 0.22
inter_arrivals[480:530] *= 0.35
event_times = np.cumsum(inter_arrivals)
tick_sizes = np.linspace(0.10, 4.2, 48)
collision_fraction = []
resolved_fraction = []
partial_order_fraction = []
max_occupancy = []
for dt in tick_sizes:
    ticks = np.floor(event_times / dt).astype(int)
    _, counts = np.unique(ticks, return_counts=True)
    collided_events = counts[counts > 1].sum()
    collision_fraction.append(collided_events / N)
    resolved_fraction.append(len(counts) / N)
    partial_order_fraction.append(1.0 - len(counts) / N)
    max_occupancy.append(counts.max())

pd.DataFrame({
    "tick_size": tick_sizes,
    "collision_fraction": collision_fraction,
    "resolved_tick_fraction": resolved_fraction,
    "partial_order_fraction": partial_order_fraction,
    "maximum_events_per_tick": max_occupancy,
}).to_csv(DATA / "fig4_clock_precision.csv", index=False)

plt.figure(figsize=(7.4, 4.6))
plt.plot(tick_sizes, collision_fraction, label="events sharing finite clock tick")
plt.plot(tick_sizes, resolved_fraction, label="distinct ticks per event")
plt.plot(tick_sizes, partial_order_fraction, label="partial-order ambiguity")
plt.plot(tick_sizes, np.array(max_occupancy) / max(max_occupancy), linestyle=":", label="max tick occupancy (normalized)")
plt.xlabel("clock tick width")
plt.ylabel("fraction / normalized value")
plt.title("Finite clock precision coarsens temporal order")
plt.legend(fontsize=8)
savefig("fig4_clock_precision")


# ---------------------------------------------------------------------
# Fig. 5: synchronization bottleneck between finite observers.
# ---------------------------------------------------------------------
channel_capacity = np.linspace(0.5, 40.0, 80)  # bits per exchange interval
needed_order_bits = 22.0
latency_uncertainty = 1.8
jitter_floor = 0.25
sync_uncertainty = jitter_floor + latency_uncertainty + needed_order_bits / channel_capacity
# If channel capacity also drops records, agreement probability declines.
agreement_probability = np.exp(-needed_order_bits / (channel_capacity * 1.35)) * np.exp(-latency_uncertainty / 10.0)
ambiguity_band = sync_uncertainty

pd.DataFrame({
    "channel_capacity_bits_per_interval": channel_capacity,
    "needed_order_bits": needed_order_bits,
    "synchronization_uncertainty": sync_uncertainty,
    "agreement_probability_proxy": agreement_probability,
    "ambiguity_band_width": ambiguity_band,
}).to_csv(DATA / "fig5_synchronization_bottleneck.csv", index=False)

fig, ax1 = plt.subplots(figsize=(7.4, 4.6))
ax1.plot(channel_capacity, sync_uncertainty, label="synchronization uncertainty")
ax1.plot(channel_capacity, ambiguity_band, linestyle=":", label="simultaneity ambiguity band")
ax1.set_xlabel("record-exchange channel capacity")
ax1.set_ylabel("time-equivalent uncertainty")
ax2 = ax1.twinx()
ax2.plot(channel_capacity, agreement_probability, linestyle="--", label="shared-order agreement proxy")
ax2.set_ylabel("agreement probability proxy")
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, fontsize=8, loc="upper right")
plt.title("Synchronization is a finite-channel record-exchange problem")
savefig("fig5_synchronization_bottleneck")


# ---------------------------------------------------------------------
# Fig. 6: projection semigroup / non-injectivity metric.
# ---------------------------------------------------------------------
K0 = 16
k_values = np.array([16, 14, 12, 10, 8, 6, 4])
retained_bits = k_values
compatible_histories_bits = K0 - k_values
compatible_histories = 2 ** compatible_histories_bits
loss_H_past_given_record = compatible_histories_bits
min_heat_units = loss_H_past_given_record
memory_fill = 1.0 - k_values / K0
arrow_strength_proj = loss_H_past_given_record / (k_values + 1)

pd.DataFrame({
    "retained_depth_k": k_values,
    "retained_record_bits": retained_bits,
    "compatible_histories_per_record": compatible_histories,
    "loss_H_past_given_record_bits": loss_H_past_given_record,
    "minimum_heat_units_kBTln2": min_heat_units,
    "memory_fill_proxy": memory_fill,
    "arrow_strength_index": arrow_strength_proj,
}).to_csv(DATA / "fig6_projection_noninjectivity.csv", index=False)

fig, ax1 = plt.subplots(figsize=(7.4, 4.6))
ax1.plot(k_values, retained_bits, marker="o", label="retained record bits")
ax1.plot(k_values, loss_H_past_given_record, marker="s", label="non-injectivity loss H(past|record)")
ax1.set_xlabel("retained depth k after projection")
ax1.set_ylabel("bits")
ax1.invert_xaxis()
ax2 = ax1.twinx()
ax2.plot(k_values, arrow_strength_proj, marker="^", linestyle="--", label="arrow-strength index")
ax2.set_ylabel("loss / retained")
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, fontsize=8, loc="upper right")
plt.title("Dissipative projection increases compatible past histories")
savefig("fig6_projection_noninjectivity")


# ---------------------------------------------------------------------
# Fig. 7: AI long-context temporal collapse as finite register projection.
# ---------------------------------------------------------------------
tokens = np.arange(0, 64001, 800)
context_window = 16000.0
task_history = tokens * (0.72 + 0.12 * np.sin(tokens / 9000.0))
exact_context = np.minimum(task_history, context_window)
compressed_summary = np.maximum(task_history - context_window, 0.0) * 0.18
lost_order_information = np.maximum(task_history - context_window - compressed_summary, 0.0)
order_confusion_index = lost_order_information / (task_history + 1.0)
plan_drift_proxy = 1 - np.exp(-4.0 * order_confusion_index)

pd.DataFrame({
    "tokens_processed": tokens,
    "task_temporal_history_bits_proxy": task_history,
    "exact_context_bits_proxy": exact_context,
    "compressed_summary_bits_proxy": compressed_summary,
    "lost_order_information_bits_proxy": lost_order_information,
    "order_confusion_index": order_confusion_index,
    "plan_drift_proxy": plan_drift_proxy,
}).to_csv(DATA / "fig7_ai_long_context_temporal_collapse.csv", index=False)

fig, ax1 = plt.subplots(figsize=(7.4, 4.6))
ax1.plot(tokens, task_history, label="task temporal history demand")
ax1.plot(tokens, exact_context, label="exact context retained")
ax1.plot(tokens, compressed_summary, label="compressed summary")
ax1.plot(tokens, lost_order_information, label="lost ordering information")
ax1.axhline(context_window, linestyle="--", label="context window")
ax1.set_xlabel("tokens / updates processed")
ax1.set_ylabel("bits proxy")
ax2 = ax1.twinx()
ax2.plot(tokens, plan_drift_proxy, linestyle=":", label="temporal-confusion / plan-drift proxy")
ax2.set_ylabel("dimensionless proxy")
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, fontsize=7, loc="upper left")
plt.title("Long-context systems: finite register projection causes temporal collapse")
savefig("fig7_ai_long_context_temporal_collapse")

print(f"Generated figures and data in {ROOT}")
