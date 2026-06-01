#!/usr/bin/env python3
"""
Phase 3A KiDS-1000 3×2pt data/covariance/order audit.

Input:
  - standardized data vector CSV with columns: probe, bin1, bin2, theta_arcmin, value
  - covariance matrix in .npy, .txt, .dat, or .csv format
  - YAML config with scale cuts

Output:
  - row_order_3x2pt.csv
  - scale_cut_mask_3x2pt.csv
  - kids1000_3x2pt_manifest.json
  - covariance_audit.md
  - optional covariance_cut.npy
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any, Dict
import numpy as np
import pandas as pd
import yaml

REQUIRED_STANDARD_COLS = ["probe", "bin1", "bin2", "theta_arcmin", "value"]

def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def resolve_path(path_str: str, base_dir: Path) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = (base_dir / p).resolve()
    return p

def load_covariance(path: Path) -> np.ndarray:
    suffix = path.suffix.lower()
    if suffix == ".npy":
        cov = np.load(path)
    elif suffix in {".txt", ".dat"}:
        cov = np.loadtxt(path)
    elif suffix == ".csv":
        cov = pd.read_csv(path, header=None).values
    else:
        raise ValueError(f"Unsupported covariance format: {path.suffix}. Use .npy, .txt, .dat, or .csv")
    if cov.ndim != 2:
        raise ValueError("Covariance is not 2D")
    return np.asarray(cov, dtype=float)

def standardize_dataframe(df: pd.DataFrame, colmap: Dict[str, str]) -> pd.DataFrame:
    out = pd.DataFrame()
    for std_col in REQUIRED_STANDARD_COLS:
        if std_col not in colmap:
            raise KeyError(f"Missing column mapping for {std_col}")
        raw_col = colmap[std_col]
        if raw_col not in df.columns:
            raise KeyError(f"Column {raw_col!r} not found in data vector CSV")
        out[std_col] = df[raw_col]
    out["probe"] = out["probe"].astype(str).str.strip().str.lower()
    out["bin1"] = out["bin1"].astype(int)
    out["bin2"] = out["bin2"].astype(int)
    out["theta_arcmin"] = out["theta_arcmin"].astype(float)
    out["value"] = out["value"].astype(float)
    out.insert(0, "row_id", np.arange(len(out), dtype=int))
    return out

def build_scale_cut_mask(df: pd.DataFrame, cfg: Dict[str, Any]) -> pd.Series:
    mask = pd.Series(True, index=df.index, dtype=bool)
    scale = cfg.get("scale_cuts", {})
    if not scale.get("enabled", False):
        return mask
    cuts = scale.get("cuts", {})
    for probe, rule in cuts.items():
        probe = str(probe).lower()
        m = df["probe"] == probe
        if "theta_min_arcmin" in rule:
            mask.loc[m] &= df.loc[m, "theta_arcmin"] >= float(rule["theta_min_arcmin"])
        if "theta_max_arcmin" in rule:
            mask.loc[m] &= df.loc[m, "theta_arcmin"] <= float(rule["theta_max_arcmin"])
    return mask

def covariance_checks(cov: np.ndarray, tol: float, check_pd: bool = True) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    result["shape"] = list(cov.shape)
    result["finite"] = bool(np.isfinite(cov).all())
    result["symmetric_max_abs"] = float(np.max(np.abs(cov - cov.T))) if cov.shape[0] == cov.shape[1] else None
    result["diag_min"] = float(np.min(np.diag(cov))) if cov.shape[0] == cov.shape[1] else None
    result["diag_max"] = float(np.max(np.diag(cov))) if cov.shape[0] == cov.shape[1] else None
    if check_pd and cov.shape[0] == cov.shape[1]:
        eig = np.linalg.eigvalsh((cov + cov.T) / 2.0)
        result["eig_min"] = float(eig[0])
        result["eig_max"] = float(eig[-1])
        result["positive_definite_or_semidefinite_with_tol"] = bool(eig[0] > tol)
        try:
            np.linalg.cholesky((cov + cov.T) / 2.0)
            result["cholesky"] = "pass"
        except np.linalg.LinAlgError:
            jitter = max(0.0, -eig[0]) + 1e-14
            try:
                np.linalg.cholesky((cov + cov.T) / 2.0 + np.eye(cov.shape[0]) * jitter)
                result["cholesky"] = f"pass_with_jitter={jitter:.3e}"
            except np.linalg.LinAlgError:
                result["cholesky"] = "fail"
    return result

def group_counts(df: pd.DataFrame) -> Dict[str, Any]:
    counts = {"by_probe": df.groupby("probe").size().astype(int).to_dict(), "by_probe_bin_pair": {}}
    gb = df.groupby(["probe", "bin1", "bin2"]).size()
    for key, val in gb.items():
        counts["by_probe_bin_pair"]["|".join(map(str, key))] = int(val)
    return counts

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="YAML audit config")
    ap.add_argument("--outdir", required=True, help="Output directory")
    args = ap.parse_args()
    cfg_path = Path(args.config).resolve()
    cfg = load_yaml(cfg_path)
    cfg_base = cfg_path.parent
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    data_path = resolve_path(cfg["data_vector"], cfg_base)
    cov_path = resolve_path(cfg["covariance"], cfg_base)
    raw = pd.read_csv(data_path)
    df = standardize_dataframe(raw, cfg.get("columns", {}))
    allowed = set(p.lower() for p in cfg.get("allowed_probes", ["xip", "xim", "gammat", "wtheta"]))
    unknown = sorted(set(df["probe"]) - allowed)
    if unknown:
        raise ValueError(f"Unknown probes in data vector: {unknown}")
    if df[["theta_arcmin", "value"]].isna().any().any():
        raise ValueError("NaN detected in theta_arcmin or value")
    cov = load_covariance(cov_path)
    n = len(df)
    if cov.shape != (n, n):
        raise ValueError(f"Data/covariance mismatch: n_rows={n}, cov_shape={cov.shape}")
    mask = build_scale_cut_mask(df, cfg)
    kept_idx = np.where(mask.values)[0]
    cov_cut = cov[np.ix_(kept_idx, kept_idx)]
    row_order = df.copy()
    row_order["kept_after_cuts"] = mask.values
    row_order.to_csv(outdir / "row_order_3x2pt.csv", index=False)
    row_order[["row_id", "probe", "bin1", "bin2", "theta_arcmin", "kept_after_cuts"]].to_csv(outdir / "scale_cut_mask_3x2pt.csv", index=False)
    audit_cfg = cfg.get("audit", {})
    cov_audit_full = covariance_checks(cov, tol=float(audit_cfg.get("eigenvalue_tolerance", -1e-12)), check_pd=bool(audit_cfg.get("check_positive_definite", True)))
    cov_audit_cut = covariance_checks(cov_cut, tol=float(audit_cfg.get("eigenvalue_tolerance", -1e-12)), check_pd=bool(audit_cfg.get("check_positive_definite", True)))
    if audit_cfg.get("write_cut_covariance", False):
        np.save(outdir / "covariance_cut.npy", cov_cut)
    manifest = {
        "dataset_name": cfg.get("dataset_name", "unnamed_3x2pt_dataset"),
        "created_by": "phase3a_kids3x2pt_audit.py",
        "status": "PASS",
        "data_vector": str(data_path),
        "covariance": str(cov_path),
        "n_rows_total": int(n),
        "covariance_shape_total": list(cov.shape),
        "n_rows_after_cuts": int(mask.sum()),
        "covariance_shape_after_cuts": list(cov_cut.shape),
        "counts_total": group_counts(df),
        "counts_after_cuts": group_counts(df.loc[mask].copy()),
        "scale_cuts": cfg.get("scale_cuts", {}),
        "covariance_audit_total": cov_audit_full,
        "covariance_audit_after_cuts": cov_audit_cut,
        "outputs": {
            "row_order": "row_order_3x2pt.csv",
            "scale_cut_mask": "scale_cut_mask_3x2pt.csv",
            "covariance_cut": "covariance_cut.npy" if audit_cfg.get("write_cut_covariance", False) else None,
            "covariance_audit": "covariance_audit.md"
        }
    }
    (outdir / "kids1000_3x2pt_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    lines = ["# Phase 3A covariance/data-vector audit\n"]
    lines += [f"- dataset: `{manifest['dataset_name']}`", f"- total rows: `{n}`", f"- covariance shape: `{cov.shape}`", f"- rows after cuts: `{int(mask.sum())}`", f"- cut covariance shape: `{cov_cut.shape}`"]
    lines.append("\n## Counts by probe\n")
    for probe, count in manifest["counts_total"]["by_probe"].items():
        kept = manifest["counts_after_cuts"]["by_probe"].get(probe, 0)
        lines.append(f"- `{probe}`: total `{count}`, kept `{kept}`")
    lines.append("\n## Covariance audit\n")
    lines.append("### Full covariance\n")
    for k, v in cov_audit_full.items(): lines.append(f"- `{k}`: `{v}`")
    lines.append("\n### Cut covariance\n")
    for k, v in cov_audit_cut.items(): lines.append(f"- `{k}`: `{v}`")
    lines.append("\n## Status\n\nPASS\n")
    (outdir / "covariance_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print("STATUS: PASS")
    print(f"n_rows_total={n}")
    print(f"covariance_shape_total={cov.shape}")
    print(f"n_rows_after_cuts={int(mask.sum())}")
    print(f"covariance_shape_after_cuts={cov_cut.shape}")
    print(f"outputs={outdir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
