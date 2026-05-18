#!/usr/bin/env python3
"""
Deterministic synthetic normal-form model for
FDS-M3: Meaning as Actionable Semantic Quotient.

The model generates illustrative data and figures for the paper.
These are synthetic normal-form examples, not empirical evidence.
"""

from __future__ import annotations

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

rng = np.random.default_rng(37)


def savefig(name: str) -> None:
    for ext in ("pdf", "png"):
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=220)
    plt.close()


def rounded_box(ax, xy, text, width=1.8, height=0.62, fontsize=10):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.03,rounding_size=0.04",
        linewidth=1.2, facecolor="white", edgecolor="black"
    )
    ax.add_patch(patch)
    ax.text(x + width/2, y + height/2, text, ha="center", va="center", fontsize=fontsize)
    return patch


def arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=12, linewidth=1.1))


def fig1_pipeline():
    fig, ax = plt.subplots(figsize=(10.5, 3.2))
    ax.axis("off")
    labels = [
        "candidate\ndistinctions",
        "M1 attention\nadmission",
        "M2 FDS-value\nranking",
        "M2 goal\nstabilization",
        "M3 semantic\nquotient",
        "action / prediction\nverification / coordination",
    ]
    xs = np.linspace(0.15, 8.9, len(labels))
    y = 1.2
    for i, (x, lab) in enumerate(zip(xs, labels)):
        rounded_box(ax, (x, y), lab, width=1.45, height=0.68, fontsize=9)
        if i < len(labels) - 1:
            arrow(ax, (x+1.45, y+0.34), (xs[i+1], y+0.34))
    ax.text(4.7, 0.35, "Meaning enters when compression preserves downstream relevance", ha="center", fontsize=10)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 2.6)
    savefig("fig1_m3_pipeline")


def fig2_compression_not_meaning():
    # Synthetic compression levels and policy loss.
    comp = np.linspace(0, 1, 80)
    irrelevant = 0.08 + 0.04*np.sin(5*comp)
    actionable = 0.02 + 0.12*comp**2
    false = 0.05 + 1.4*np.maximum(comp-0.35, 0)**1.7
    df = pd.DataFrame({"compression": comp, "irrelevant_loss": irrelevant, "policy_preserving_loss": actionable, "false_compression_loss": false})
    df.to_csv(DATA / "fig2_compression_not_meaning.csv", index=False)

    plt.figure(figsize=(7.2, 4.5))
    plt.plot(comp, irrelevant, label="lossless/irrelevant compression")
    plt.plot(comp, actionable, label="policy-preserving compression")
    plt.plot(comp, false, label="false compression")
    plt.axhline(0.25, linestyle="--", linewidth=1, label="semantic tolerance")
    plt.xlabel("compression strength")
    plt.ylabel("downstream policy loss")
    plt.title("Synthetic normal-form illustration: compression is not meaning")
    plt.legend(fontsize=8)
    savefig("fig2_compression_not_meaning")


def fig3_policy_quotient():
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.axis("off")
    # Fine distinctions grouped into valid and invalid classes.
    fine_x = 0.6
    ys = np.linspace(3.6, 0.6, 6)
    actions = ["avoid", "avoid", "approach", "approach", "verify", "avoid"]
    classes_good = ["Q1", "Q1", "Q2", "Q2", "Q3", "Q4"]
    for i, (y, act) in enumerate(zip(ys, actions)):
        rounded_box(ax, (fine_x, y), f"d{i+1}\n{act}", width=0.95, height=0.45, fontsize=8)
    # Good quotient classes
    qx = 3.1
    qy = [3.25, 2.1, 1.1, 0.35]
    qlabels = ["Q1\navoid", "Q2\napproach", "Q3\nverify", "Q4\navoid"]
    for y, lab in zip(qy, qlabels):
        rounded_box(ax, (qx, y), lab, width=1.05, height=0.55, fontsize=8)
    # arrows
    for i, y in enumerate(ys):
        target_idx = [0,0,1,1,2,3][i]
        arrow(ax, (fine_x+0.95, y+0.22), (qx, qy[target_idx]+0.27))
    # Policy
    rounded_box(ax, (5.5, 1.8), "quotient\npolicy", width=1.1, height=0.6, fontsize=9)
    rounded_box(ax, (7.1, 1.8), "low\npolicy loss", width=1.2, height=0.6, fontsize=9)
    arrow(ax, (4.15, 2.1), (5.5, 2.1))
    arrow(ax, (6.6, 2.1), (7.1, 2.1))
    ax.text(1.0, 4.35, "fine distinctions", ha="center", fontsize=10)
    ax.text(3.6, 4.35, "policy-preserving\nquotient", ha="center", fontsize=10)
    ax.text(6.1, 4.35, "downstream\naction", ha="center", fontsize=10)
    ax.set_xlim(0, 8.8)
    ax.set_ylim(0, 4.8)
    savefig("fig3_policy_preserving_quotient")


def fig4_embedding_policy_dissociation():
    n = 260
    embedding_similarity = rng.uniform(0, 1, n)
    # policy equivalence only partially correlated; add false friends and hidden equivalents.
    policy_equiv = 0.25 + 0.5*embedding_similarity + rng.normal(0, 0.22, n)
    policy_equiv = np.clip(policy_equiv, 0, 1)
    false_friends = (embedding_similarity > 0.72) & (policy_equiv < 0.42)
    hidden_equiv = (embedding_similarity < 0.35) & (policy_equiv > 0.75)
    df = pd.DataFrame({"embedding_similarity": embedding_similarity, "policy_equivalence": policy_equiv, "false_friend": false_friends, "hidden_equivalent": hidden_equiv})
    df.to_csv(DATA / "fig4_embedding_policy_dissociation.csv", index=False)

    plt.figure(figsize=(6.8, 5.0))
    plt.scatter(embedding_similarity, policy_equiv, s=18, alpha=0.55, label="candidate pair")
    plt.scatter(embedding_similarity[false_friends], policy_equiv[false_friends], marker="x", s=42, label="embedding-near / policy-different")
    plt.scatter(embedding_similarity[hidden_equiv], policy_equiv[hidden_equiv], marker="^", s=38, label="embedding-far / policy-equivalent")
    plt.axvline(0.72, linestyle="--", linewidth=1)
    plt.axhline(0.5, linestyle="--", linewidth=1)
    plt.xlabel("embedding similarity")
    plt.ylabel("policy equivalence / action agreement")
    plt.title("Synthetic normal-form illustration: embedding similarity is not meaning")
    plt.legend(fontsize=8)
    savefig("fig4_embedding_policy_dissociation")


def fig5_semantic_deficit_collapse():
    delta = np.linspace(0, 1.6, 120)
    policy_preserve = 1/(1 + np.exp(5*(delta-0.65)))
    false_merge = 1/(1 + np.exp(-6*(delta-0.55)))
    proxy_meaning = 1/(1 + np.exp(-5*(delta-0.75)))
    halluc_completion = 1/(1 + np.exp(-7*(delta-0.95)))
    df = pd.DataFrame({"Delta_sem": delta, "policy_preservation": policy_preserve, "false_merging": false_merge, "proxy_meaning": proxy_meaning, "unsupported_completion": halluc_completion})
    df.to_csv(DATA / "fig5_semantic_deficit_collapse.csv", index=False)

    plt.figure(figsize=(7.2, 4.7))
    plt.plot(delta, policy_preserve, label="policy preservation")
    plt.plot(delta, false_merge, label="false merging")
    plt.plot(delta, proxy_meaning, label="proxy meaning")
    plt.plot(delta, halluc_completion, label="unsupported completion")
    plt.axvline(0.65, linestyle="--", linewidth=1, label="collapse threshold")
    plt.xlabel("semantic capacity deficit $\\Delta_{sem}$")
    plt.ylabel("normalized level")
    plt.title("Synthetic normal-form illustration: semantic deficit and collapse")
    plt.legend(fontsize=8)
    savefig("fig5_semantic_deficit_collapse")


def fig6_false_compression():
    # Create a confusion matrix: quotient classes vs true policy labels.
    true = np.array([0,0,0,1,1,1,2,2,2,3,3,3])
    quotient = np.array([0,0,1,1,1,2,2,2,2,3,0,3])
    n_true, n_q = 4, 4
    mat = np.zeros((n_true, n_q))
    for t, q in zip(true, quotient):
        mat[t, q] += 1
    df = pd.DataFrame(mat, columns=[f"Q{j+1}" for j in range(n_q)], index=[f"A{i+1}" for i in range(n_true)])
    df.to_csv(DATA / "fig6_false_compression_matrix.csv")

    plt.figure(figsize=(6.2, 4.8))
    plt.imshow(mat, aspect="auto")
    plt.colorbar(label="number of fine distinctions")
    plt.xticks(range(n_q), [f"quotient Q{j+1}" for j in range(n_q)], rotation=25, ha="right")
    plt.yticks(range(n_true), [f"true action A{i+1}" for i in range(n_true)])
    plt.title("Synthetic normal-form illustration: false compression")
    for i in range(n_true):
        for j in range(n_q):
            plt.text(j, i, int(mat[i,j]), ha="center", va="center")
    savefig("fig6_false_compression_matrix")


def fig7_shared_meaning_sync():
    z = np.linspace(0, 1.8, 140)
    # Nonlinear threshold-style collapse around Z=1.
    coordination = 1/(1 + np.exp(9*(z-1.0)))
    quotient_mismatch = 1/(1 + np.exp(-8*(z-0.92)))
    false_coordination = 1/(1 + np.exp(-10*(z-1.08)))
    df = pd.DataFrame({"Z_sem_sync": z, "coordination_success": coordination, "quotient_mismatch": quotient_mismatch, "false_coordination": false_coordination})
    df.to_csv(DATA / "fig7_shared_meaning_sync.csv", index=False)

    plt.figure(figsize=(7.2, 4.7))
    plt.plot(z, coordination, label="coordination success")
    plt.plot(z, quotient_mismatch, label="quotient mismatch")
    plt.plot(z, false_coordination, label="false coordination")
    plt.axvline(1.0, linestyle="--", linewidth=1, label="$Z_{sem-sync}=1$ threshold")
    plt.axvspan(1.0, z.max(), alpha=0.08, label="overload region")
    plt.xlabel("semantic synchronization load factor $Z_{sem-sync}$")
    plt.ylabel("normalized level")
    plt.title("Synthetic normal-form illustration: shared meaning synchronization")
    plt.legend(fontsize=8)
    savefig("fig7_shared_meaning_sync")


def fig8_recovery_refinement():
    t = np.arange(0, 121)
    shock = ((t >= 30) & (t <= 60)).astype(float)
    deficit = 0.25 + 0.95*shock + 0.45*np.exp(-np.maximum(t-60,0)/26.0)*(t>60)
    refinement = 1/(1+np.exp(-(t-75)/9))
    policy_preservation = 0.85 - 0.55*shock - 0.35*np.exp(-np.maximum(t-60,0)/35)*(t>60) + 0.45*refinement
    policy_preservation = np.clip(policy_preservation, 0.05, 0.98)
    false_compression = 1 - policy_preservation + 0.06*np.sin(t/8)
    false_compression = np.clip(false_compression, 0, 1)
    df = pd.DataFrame({"time": t, "semantic_deficit": deficit, "quotient_refinement": refinement, "policy_preservation": policy_preservation, "false_compression": false_compression})
    df.to_csv(DATA / "fig8_recovery_refinement.csv", index=False)

    plt.figure(figsize=(7.3, 4.7))
    plt.plot(t, deficit, label="semantic deficit")
    plt.plot(t, policy_preservation, label="policy preservation")
    plt.plot(t, false_compression, label="false compression")
    plt.plot(t, refinement, label="quotient refinement")
    plt.axvspan(30, 60, alpha=0.15, label="overload interval")
    plt.xlabel("time")
    plt.ylabel("normalized level")
    plt.title("Synthetic normal-form illustration: meaning recovery by quotient refinement")
    plt.legend(fontsize=8)
    savefig("fig8_recovery_refinement")


def main():
    fig1_pipeline()
    fig2_compression_not_meaning()
    fig3_policy_quotient()
    fig4_embedding_policy_dissociation()
    fig5_semantic_deficit_collapse()
    fig6_false_compression()
    fig7_shared_meaning_sync()
    fig8_recovery_refinement()
    print(f"Generated figures in {FIG}")
    print(f"Generated data in {DATA}")


if __name__ == "__main__":
    main()
