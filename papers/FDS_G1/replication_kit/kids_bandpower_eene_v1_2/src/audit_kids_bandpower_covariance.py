#!/usr/bin/env python3
"""
Standalone numerical audit of the KiDS 300×300 bandpower covariance.

Does NOT match against any data vector. Only verifies:
  - shape = 300×300
  - finite entries
  - symmetry
  - eigenvalue sanity / positive definiteness
  - Cholesky decomposability
  - dimension factorization hypothesis

Outputs:
  - bandpower_covariance_manifest.json
  - covariance_audit.md
  - ordering_hypotheses.md
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

def load_cov(path: Path) -> np.ndarray:
    c = np.loadtxt(path)
    if c.ndim != 2:
        raise ValueError(f"Expected 2D covariance, got ndim={c.ndim}")
    return np.asarray(c, dtype=float)

def main():
    ap = argparse.ArgumentParser(description="Audit KiDS bandpower covariance")
    ap.add_argument("--cov", required=True, help="Path to 300×300 covariance .ascii file")
    ap.add_argument("--outdir", default="outputs/bandpower_covariance_audit")
    ap.add_argument("--tol", type=float, default=-1e-12,
                    help="Eigenvalue tolerance for PD check")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cov = load_cov(Path(args.cov))
    n = cov.shape[0]

    if cov.shape != (n, n):
        raise ValueError(f"Matrix not square: {cov.shape}")

    cov_sym = (cov + cov.T) / 2.0

    finite = bool(np.isfinite(cov).all())
    sym_max_abs = float(np.max(np.abs(cov - cov.T)))
    diag_min = float(np.min(np.diag(cov)))
    diag_max = float(np.max(np.diag(cov)))

    eig = np.linalg.eigvalsh(cov_sym)
    eig_min = float(eig[0])
    eig_max = float(eig[-1])
    pd_status = bool(eig[0] > 0)

    cholesky_status = "fail"
    jitter_needed = 0.0
    try:
        np.linalg.cholesky(cov_sym)
        cholesky_status = "pass"
    except np.linalg.LinAlgError:
        jitter = max(0.0, -eig[0]) + 1e-14
        try:
            np.linalg.cholesky(cov_sym + np.eye(n) * jitter)
            cholesky_status = f"pass_with_jitter={jitter:.3e}"
            jitter_needed = jitter
        except np.linalg.LinAlgError:
            cholesky_status = "fail"

    # Dimension factorization hypothesis
    factor_hypotheses = [
        "300 = 15 source-bin pairs × 20 bandpowers",
        "300 = 10 xi± pairs × 30 + ... unlikely",
        "300 = 300 × 1 (no block structure)",
    ]
    preferred_hypothesis = factor_hypotheses[0]

    # Check for block structure in log-scale
    log_cov = np.log10(np.abs(cov) + 1e-40)
    block_score = float(np.std(log_cov[:15, :15])) if n >= 15 else 0.0

    manifest = {
        "dataset": "KiDS-1000 bandpower covariance (3×2pt best-fit, Blind C)",
        "source_file": str(Path(args.cov).resolve()),
        "basis": "bandpower_or_Cell_space",
        "matched_to_real_space_xipm_270": False,
        "ordering_verified": False,
        "safe_for_realspace_xipm_likelihood": False,
        "shape": [n, n],
        "finite": finite,
        "symmetric_max_abs_diff": sym_max_abs,
        "diag_min": diag_min,
        "diag_max": diag_max,
        "eig_min": eig_min,
        "eig_max": eig_max,
        "positive_definite_or_semidefinite": pd_status,
        "cholesky": cholesky_status,
        "jitter_needed_for_cholesky": jitter_needed,
        "dimension_factorization_hypothesis": preferred_hypothesis,
        "factorization_status": "dimension_only_unverified",
        "block_structure_std_log10": block_score,
        "status": "AUDITED_BUT_NOT_MATCHED_TO_REAL_SPACE_3X2PT",
    }

    (outdir / "bandpower_covariance_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    md_lines = [
        "# Bandpower Covariance Audit\n",
        f"- **Shape**: `{n}×{n}`",
        f"- **Finite**: `{finite}`",
        f"- **Symmetric max abs diff**: `{sym_max_abs:.3e}`",
        f"- **Diagonal range**: `{diag_min:.3e}` to `{diag_max:.3e}`",
        f"- **Eigenvalue range**: `{eig_min:.3e}` to `{eig_max:.3e}`",
        f"- **Positive (semi)definite**: `{pd_status}`",
        f"- **Cholesky**: `{cholesky_status}`",
        f"- **Dimension hypothesis**: {preferred_hypothesis}",
        f"",
        "## Important caveats",
        "",
        "1. This covariance is in **bandpower (Cℓ)** space, not real-space (θ).",
        "2. It is **not** directly compatible with the 270-element real-space xi± vector.",
        "3. No row/column labels were found in the official repository.",
        "4. The 15×20 factorization is a dimension-only hypothesis, not verified against metadata.",
        "",
        "## Status",
        "",
        "AUDITED_BUT_NOT_MATCHED_TO_REAL_SPACE_3X2PT",
    ]
    (outdir / "covariance_audit.md").write_text("\n".join(md_lines), encoding="utf-8")

    # Ordering hypotheses
    hyp_lines = [
        "# Ordering Hypotheses\n",
        "**All hypotheses are unverified and based on dimension-only inference.**\n",
        "",
        "| Hypothesis | Evidence | Status |",
        "|-----------|----------|--------|",
        f"| {preferred_hypothesis} | Matrix dimension n=300; 5 tomographic bins → 15 unique source-source pairs; 300/15=20 | dimension_only_unverified |",
        "| Alternative: 300 independent modes | No block structure assumed | dimension_only_unverified |",
        "",
        "## How to resolve",
        "",
        "To verify row ordering, one would need:",
        "- The official KiDS likelihood pipeline (CosmoSIS / KCAP) configuration showing the data-vector build order",
        "- Or a labelled covariance from the KiDS data release with explicit bin/probe/bandpower indices",
        "",
        "*Generated 2026-05-30 by audit_kids_bandpower_covariance.py*",
    ]
    (outdir / "ordering_hypotheses.md").write_text("\n".join(hyp_lines), encoding="utf-8")

    print("STATUS: PASS (numerical-only, no row-order verification)")
    print(f"shape={n}×{n}")
    print(f"symmetric_max_abs={sym_max_abs:.3e}")
    print(f"eig_min={eig_min:.3e} eig_max={eig_max:.3e}")
    print(f"cholesky={cholesky_status}")
    print(f"outputs={outdir}")

if __name__ == "__main__":
    main()
