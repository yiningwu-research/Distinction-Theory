#!/usr/bin/env python3
"""Normal-form demonstrations for FDS-X3 v1.1.

These figures are qualitative operation-closure illustrations. They are not
coupling-constant fits, Standard Model simulations, or empirical weights. They
encode primary-role coverage, weak cross-role participation, and the difference
between a new mediator and a new irreducible operation primitive.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

operations = [
    "Encapsulation\n(strong)",
    "Connection\n(EM)",
    "Identity transformation\n(weak)",
    "Causal-geometric\naccounting (gravity)",
]
short_ops = ["enc", "conn", "id", "geom"]
requirements = [
    "hadronic/baryonic\ntokens",
    "remote\ndetectability",
    "sector conversion\n/ pruning",
    "causal-geometric\nconstraint",
]
short_req = ["tokens", "detect", "update", "geometry"]

# Qualitative coverage matrix: rows=operation classes, columns=required functions.
# Entries are normal-form role scores, not coupling constants or empirical data.
# Diagonal dominance encodes primary role. Off-diagonal entries encode the fact
# that real interactions are coupled and can participate weakly in multiple tasks.
coverage = np.array([
    [1.00, 0.12, 0.03, 0.04],  # Strong: hadronic/baryonic encapsulation
    [0.22, 1.00, 0.07, 0.06],  # EM: atomic/molecular stability + connection
    [0.05, 0.08, 1.00, 0.05],  # Weak: flavor/particle-sector update
    [0.07, 0.10, 0.05, 1.00],  # Gravity: causal-geometric / stress-energy accounting
])
weights = np.array([1.10, 1.00, 1.00, 1.15])
target = np.ones(len(requirements))

# A hypothetical redundant fifth mediator: it does not add a new operation primitive;
# it only weakly duplicates existing connection/boundary roles.
redundant_fifth = np.array([0.00, 0.18, 0.00, 0.10])
new_primitive = np.array([0.00, 0.00, 0.00, 0.00])  # represented separately in tree

coverage_df = pd.DataFrame(coverage, index=operations, columns=requirements)
coverage_df.to_csv(DATA / "operation_requirement_coverage.csv")

params = {
    "description": "Deterministic normal-form operation-closure model for X3 v1.1.",
    "operations": operations,
    "requirements": requirements,
    "coverage_note": "Qualitative primary-role scores, not coupling constants or empirical weights.",
    "weights": weights.tolist(),
    "target": target.tolist(),
    "redundant_fifth": redundant_fifth.tolist(),
}
(DATA / "simulation_parameters.json").write_text(json.dumps(params, indent=2), encoding="utf-8")


def subset_metrics(mask: np.ndarray, include_redundant: bool = False) -> tuple[np.ndarray, float, float]:
    cov = coverage[mask].sum(axis=0) if mask.any() else np.zeros(len(requirements))
    if include_redundant:
        cov = cov + redundant_fifth
    cov = np.minimum(cov, 1.0)
    residual = np.maximum(target - cov, 0.0)
    loss = float(np.sum(weights * residual**2))
    score = float(np.mean(cov))
    return cov, loss, score

rows = []
for bits in itertools.product([0, 1], repeat=len(operations)):
    mask = np.array(bits, dtype=bool)
    subset = "+".join([short_ops[i] for i, b in enumerate(bits) if b]) or "none"
    cov, loss, score = subset_metrics(mask)
    rows.append({
        "subset": subset,
        "num_operations": int(mask.sum()),
        "closure_loss": loss,
        "closure_score": score,
        **{f"coverage_{short_req[i]}": cov[i] for i in range(len(requirements))}
    })
subset_df = pd.DataFrame(rows).sort_values(["num_operations", "closure_loss"])
subset_df.to_csv(DATA / "subset_closure_loss.csv", index=False)

# Figure 1: Four-operation closure square.
fig, ax = plt.subplots(figsize=(3.6, 2.6))
ax.axis("off")
positions = {
    "Strong\nencapsulation\nhadrons": (0.12, 0.78),
    "EM\nconnection\nsignals": (0.88, 0.78),
    "Weak\nidentity change\nflavor/prune": (0.88, 0.22),
    "Gravity\ngeometry\nstress-energy": (0.12, 0.22),
}
for label, (x, y) in positions.items():
    ax.text(x, y, label, ha="center", va="center", fontsize=7.6,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="black", lw=1.2))
ax.text(0.5, 0.5, "finite distinction\nmaintenance", ha="center", va="center", fontsize=8,
        bbox=dict(boxstyle="round,pad=0.55", fc="white", ec="black", lw=1.4))
# Light guide lines indicate closure relation without implying a dynamical flow.
coords = list(positions.values())
for (x1,y1),(x2,y2) in zip(coords, coords[1:]+coords[:1]):
    ax.plot([x1, x2], [y1, y2], lw=0.8, alpha=0.35)
for x,y in coords:
    ax.plot([x, 0.5], [y, 0.5], lw=0.6, alpha=0.25)
ax.set_title("Four operation classes", fontsize=9)
fig.tight_layout()
fig.savefig(FIG / "fig1_closure_square.pdf")
fig.savefig(FIG / "fig1_closure_square.png", dpi=200)
plt.close(fig)

# Figure 2: Coverage matrix.
fig, ax = plt.subplots(figsize=(7.8, 4.9))
im = ax.imshow(coverage, vmin=0, vmax=1, cmap="Greys")
ax.set_xticks(np.arange(len(requirements)))
ax.set_yticks(np.arange(len(operations)))
ax.set_xticklabels(requirements, rotation=24, ha="right")
ax.set_yticklabels(["Strong", "EM", "Weak", "Gravity"])
for i in range(coverage.shape[0]):
    for j in range(coverage.shape[1]):
        ax.text(j, i, f"{coverage[i,j]:.2f}", ha="center", va="center", fontsize=8.6)
ax.set_title("Qualitative operation coverage matrix (normal-form scores)")
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("role coverage (not coupling strength)")
fig.tight_layout()
fig.savefig(FIG / "fig2_coverage_matrix.pdf")
fig.savefig(FIG / "fig2_coverage_matrix.png", dpi=200)
plt.close(fig)

# Figure 3: Remove-one plus redundant-fifth comparison.
full_mask = np.ones(len(operations), dtype=bool)
_, full_loss, _ = subset_metrics(full_mask)
labels = ["all four\npresent"]
losses = [full_loss]
for i, op in enumerate(short_ops):
    mask = full_mask.copy(); mask[i] = False
    _, loss, _ = subset_metrics(mask)
    labels.append(f"remove\n{op}")
    losses.append(loss)
_, loss_with_redundant, _ = subset_metrics(full_mask, include_redundant=True)
labels.append("add redundant\nfifth mediator")
losses.append(loss_with_redundant)
remove_df = pd.DataFrame({"case": labels, "closure_loss": losses})
remove_df.to_csv(DATA / "remove_one_failure.csv", index=False)

fig, ax = plt.subplots(figsize=(8.4, 4.5))
ax.bar(np.arange(len(losses)), losses, edgecolor="black")
ax.set_xticks(np.arange(len(losses)))
ax.set_xticklabels(labels)
ax.set_ylabel("normal-form residual closure loss")
ax.set_title("Remove-one test and redundant-fifth comparison")
ax.text(0.5, 0.93, "scores are arbitrary normal-form values", transform=ax.transAxes,
        ha="center", va="center", fontsize=8.6)
fig.tight_layout()
fig.savefig(FIG / "fig3_remove_one_failure.pdf")
fig.savefig(FIG / "fig3_remove_one_failure.png", dpi=200)
plt.close(fig)

# Figure 4: New-force classification tree.
fig, ax = plt.subplots(figsize=(8.4, 5.4))
ax.axis("off")
boxes = [
    (0.5, 0.88, "candidate\nnew interaction"),
    (0.5, 0.70, "new irreducible\ndistinction operation?"),
    (0.16, 0.49, "encapsulation-like\n(hidden confinement,\nbinding sector)"),
    (0.38, 0.49, "connection-like\n(portal, dark photon,\nlong-range mediator)"),
    (0.62, 0.49, "identity-update-like\n(decay, flavor,\nstate conversion)"),
    (0.84, 0.49, "boundary-like\n(geometry, scalar,\nstress-energy channel)"),
    (0.5, 0.22, "genuinely new\noperation primitive\n=> expands X3 closure")
]
for x, y, text in boxes:
    ax.text(x, y, text, ha="center", va="center", fontsize=9.0,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="black", lw=1.0))
ax.annotate("", xy=(0.5,0.76), xytext=(0.5,0.83), arrowprops=dict(arrowstyle="->", lw=1))
for x in [0.16,0.38,0.62,0.84]:
    ax.annotate("", xy=(x,0.57), xytext=(0.5,0.66), arrowprops=dict(arrowstyle="->", lw=1))
ax.annotate("", xy=(0.5,0.30), xytext=(0.5,0.66), arrowprops=dict(arrowstyle="->", lw=1.1))
ax.text(0.50, 0.61, "no: classify as instance / sector extension", ha="center", fontsize=8.4)
ax.text(0.57, 0.39, "yes", ha="center", fontsize=9)
ax.set_title("Fifth-force audit: new mediator vs. new operation primitive", fontsize=13)
fig.tight_layout()
fig.savefig(FIG / "fig4_new_force_tree.pdf")
fig.savefig(FIG / "fig4_new_force_tree.png", dpi=200)
plt.close(fig)

# Figure 5: P/X relation map.
fig, ax = plt.subplots(figsize=(3.7, 2.5))
ax.axis("off")
items = [
    (0.08, 0.72, "P4\ninternal loss"),
    (0.28, 0.72, "P3\nexternal records"),
    (0.48, 0.72, "P6\nthroughput"),
    (0.68, 0.72, "P7\nprotection"),
    (0.30, 0.32, "X2\nweak identity\norientation"),
    (0.62, 0.32, "X3\nfour-operation\nclosure")
]
for x,y,text in items:
    ax.text(x,y,text,ha="center",va="center",fontsize=6.6,
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="black"))
for (x1,y1,_),(x2,y2,_) in zip(items[:4], items[1:4]):
    ax.annotate("", xy=(x2-0.06,y2), xytext=(x1+0.06,y1), arrowprops=dict(arrowstyle="->", lw=1))
ax.annotate("", xy=(0.55,0.36), xytext=(0.36,0.36), arrowprops=dict(arrowstyle="->", lw=1.2))
ax.annotate("", xy=(0.62,0.42), xytext=(0.68,0.64), arrowprops=dict(arrowstyle="->", lw=1))
ax.annotate("", xy=(0.30,0.42), xytext=(0.48,0.64), arrowprops=dict(arrowstyle="->", lw=1))
ax.text(0.47,0.14,"X2 supplies the weak-sector module; X3 places it in the operation taxonomy.",ha="center",fontsize=6.2)
ax.set_title("X3 relation map", fontsize=9)
fig.tight_layout()
fig.savefig(FIG / "fig5_relation_map.pdf")
fig.savefig(FIG / "fig5_relation_map.png", dpi=200)
plt.close(fig)

print(f"Wrote figures to {FIG}")
print(f"Wrote data to {DATA}")
