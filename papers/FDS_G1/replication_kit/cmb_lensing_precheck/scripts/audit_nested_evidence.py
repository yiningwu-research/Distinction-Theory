#!/usr/bin/env python3
"""Summarize nested-evidence run completeness and logZ scatter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODELS = ["lcdm", "g1_bg", "g1_mkappa", "g1_m34"]


def read_result(run_dir: Path) -> dict:
    result_path = run_dir / "info" / "results.json"
    points_path = run_dir / "results" / "points.hdf5"
    item = {
        "run": run_dir.name,
        "path": str(run_dir.relative_to(ROOT)),
        "has_points": points_path.exists(),
        "complete": result_path.exists(),
    }
    if result_path.exists():
        data = json.loads(result_path.read_text())
        item.update(
            {
                "logZ": float(data["logz"]),
                "logZerr": float(data["logzerr"]),
                "ess": float(data.get("ess", np.nan)),
                "ncall": int(data.get("ncall", -1)),
                "niter": int(data.get("niter", -1)),
                "insertion_converged": bool(
                    data.get("insertion_order_MWW_test", {}).get("converged", False)
                ),
            }
        )
    return item


def summarize(root: Path) -> dict:
    out = {"root": str(root.relative_to(ROOT)), "models": {}}
    for model in MODELS:
        model_dir = root / model
        runs = []
        if model_dir.exists():
            for run_dir in sorted(p for p in model_dir.iterdir() if p.is_dir() and p.name.startswith("run_")):
                runs.append(read_result(run_dir))

        complete = [r for r in runs if r["complete"]]
        logz = np.array([r["logZ"] for r in complete], dtype=float)
        logzerr = np.array([r["logZerr"] for r in complete], dtype=float)
        out["models"][model] = {
            "runs": runs,
            "n_complete": len(complete),
            "n_incomplete": len(runs) - len(complete),
            "mean_logZ": float(np.mean(logz)) if len(logz) else None,
            "scatter_logZ": float(np.std(logz, ddof=1)) if len(logz) > 1 else 0.0 if len(logz) == 1 else None,
            "mean_logZerr": float(np.mean(logzerr)) if len(logzerr) else None,
        }

    lcdm = out["models"].get("lcdm", {}).get("mean_logZ")
    if lcdm is not None:
        for model, data in out["models"].items():
            if data["mean_logZ"] is not None:
                data["delta_logZ_vs_lcdm"] = float(data["mean_logZ"] - lcdm)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="outputs/nested_evidence/act_only_production")
    parser.add_argument("--out", default="outputs/nested_evidence_audit.json")
    args = parser.parse_args()

    root = ROOT / args.root
    result = summarize(root)
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {out.relative_to(ROOT)}")
    for model, data in result["models"].items():
        print(
            f"{model:10s} complete={data['n_complete']} incomplete={data['n_incomplete']} "
            f"logZ={data['mean_logZ']} scatter={data['scatter_logZ']} "
            f"dlogZ={data.get('delta_logZ_vs_lcdm')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
