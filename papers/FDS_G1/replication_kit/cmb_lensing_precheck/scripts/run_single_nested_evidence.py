#!/usr/bin/env python3
"""Run or resume one UltraNest evidence job."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cmb_lensing_precheck.mcmc.evidence import (
    EvidenceLikelihood,
    MODEL_PARAMS,
    prior_transform,
    run_ultranest,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, choices=sorted(MODEL_PARAMS))
    parser.add_argument("--variant", default="act_baseline")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--live-points", type=int, default=1000)
    parser.add_argument("--min-ess", type=int, default=1000)
    parser.add_argument("--dlogz", type=float, default=0.05)
    parser.add_argument(
        "--max-improvement-loops",
        type=int,
        default=1,
        help=(
            "UltraNest reactive improvement loops after the initial target is met. "
            "Keeping this finite avoids pathological root widening when much of the "
            "registered prior maps outside the emulator domain."
        ),
    )
    args = parser.parse_args()

    np.random.seed(args.seed)
    outdir = ROOT / args.outdir
    like = EvidenceLikelihood(args.model, variant=args.variant, amplitude_param="ln10As")

    def transform(cube):
        arr = np.asarray(cube)
        if arr.ndim == 1:
            return prior_transform(arr[None, :], args.model)[0]
        return prior_transform(arr, args.model)

    t0 = time.time()
    status = "completed"
    exception = None
    try:
        result = run_ultranest(
            like.log_likelihood,
            transform,
            len(MODEL_PARAMS[args.model]),
            outdir,
            min_num_live_points=args.live_points,
            min_ess=args.min_ess,
            dlogz=args.dlogz,
            max_num_improvement_loops=args.max_improvement_loops,
        )
    except Exception as exc:
        results_path = outdir / "info" / "results.json"
        if not results_path.exists() or results_path.stat().st_mtime < t0:
            raise
        saved = json.loads(results_path.read_text())
        result = {"logZ": float(saved["logz"]), "logZerr": float(saved["logzerr"])}
        status = "recovered_after_ultranest_exception"
        exception = f"{type(exc).__name__}: {exc}"
    elapsed = time.time() - t0

    summary = {
        "model": args.model,
        "variant": args.variant,
        "outdir": str(outdir.relative_to(ROOT)),
        "seed": args.seed,
        "live_points": args.live_points,
        "min_ess": args.min_ess,
        "dlogz": args.dlogz,
        "max_improvement_loops": args.max_improvement_loops,
        "walltime_s": elapsed,
        "status": status,
        "logZ": result["logZ"],
        "logZerr": result["logZerr"],
    }
    if exception is not None:
        summary["exception"] = exception
    summary_path = outdir / "codex_run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
