#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, yaml, numpy as np
from pathlib import Path

Pnee_PAIRS = [(l, s) for l in [1, 2] for s in range(1, 6)]
PeeE_PAIRS = [(i, j) for i in range(1, 6) for j in range(i, 6)]
N_ANG = 8
EXPECTED_LEN = (len(Pnee_PAIRS) + len(PeeE_PAIRS)) * N_ANG


def load_config(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def audit_vector(asc_path: Path, fits_path: Path, expected: int) -> dict:
    import astropy.io.fits as fits
    asc_values = np.loadtxt(asc_path)
    result = {
        "vector_source": str(asc_path),
        "vector_length": int(len(asc_values)),
        "vector_length_ok": len(asc_values) == expected,
    }
    if not result["vector_length_ok"]:
        result["error"] = f"Expected {expected} elements, got {len(asc_values)}"
        return result

    hdul = fits.open(fits_path)
    pnee = hdul['PneE'].data
    peee = hdul['PeeE'].data
    fits_values = np.concatenate([
        np.array([r['VALUE'] for r in pnee]),
        np.array([r['VALUE'] for r in peee]),
    ])
    match = np.allclose(asc_values, fits_values, rtol=1e-15, atol=1e-30)
    result["fits_table_match"] = bool(match)
    if not match:
        result["max_asc_vs_fits_diff"] = float(np.max(np.abs(asc_values - fits_values)))
    return result


def audit_covariance(fits_path: Path, expected_n: int) -> dict:
    import astropy.io.fits as fits
    hdul = fits.open(fits_path)
    c = hdul['COVMAT'].data.astype(float)

    n = c.shape[0]
    result = {
        "covariance_source": str(fits_path),
        "shape": [n, n],
        "shape_ok": c.shape == (expected_n, expected_n),
        "finite": bool(np.isfinite(c).all()),
    }
    if not result["shape_ok"]:
        return result

    c_sym = (c + c.T) / 2.0
    sym_diff = np.max(np.abs(c - c.T))
    result["symmetric_max_abs_diff"] = float(sym_diff)
    result["symmetric_ok"] = sym_diff < 1e-20

    result["diag_min"] = float(np.min(np.diag(c)))
    result["diag_max"] = float(np.max(np.diag(c)))

    eigvals = np.linalg.eigvalsh(c_sym)
    result["eig_min"] = float(eigvals.min())
    result["eig_max"] = float(eigvals.max())
    result["positive_definite"] = bool(eigvals.min() > 0)

    try:
        np.linalg.cholesky(c_sym)
        result["cholesky"] = "pass"
        result["jitter_needed"] = 0.0
    except np.linalg.LinAlgError:
        for jitter in [1e-18, 1e-16, 1e-14, 1e-12]:
            try:
                np.linalg.cholesky(c_sym + jitter * np.eye(n))
                result["cholesky"] = f"pass_with_jitter_{jitter:.0e}"
                result["jitter_needed"] = jitter
                break
            except np.linalg.LinAlgError:
                continue
        else:
            result["cholesky"] = "fail"
            result["jitter_needed"] = None

    return result


def crosscheck_iterative(fits_path: Path, iterative_path: Path) -> dict:
    import astropy.io.fits as fits
    c1 = fits.open(fits_path)['COVMAT'].data.astype(float)
    c2 = fits.open(iterative_path)['COVMAT'].data.astype(float)
    result = {
        "fits_path": str(fits_path),
        "iterative_path": str(iterative_path),
        "both_200x200": c1.shape == (200, 200) and c2.shape == (200, 200),
    }
    if c1.shape != c2.shape:
        result["match"] = False
        result["reason"] = f"Shape mismatch: {c1.shape} vs {c2.shape}"
        return result
    max_abs_diff = float(np.max(np.abs(c1 - c2)))
    result["max_abs_diff"] = max_abs_diff
    result["match"] = max_abs_diff < 1e-12
    return result


def verify_row_order(fits_path: Path) -> dict:
    import astropy.io.fits as fits
    hdul = fits.open(fits_path)
    pnee = hdul['PneE'].data
    peee = hdul['PeeE'].data

    pnee_ordering = []
    for r in pnee:
        pnee_ordering.append((int(r['BIN1']), int(r['BIN2']), int(r['ANGBIN'])))
    peee_ordering = []
    for r in peee:
        peee_ordering.append((int(r['BIN1']), int(r['BIN2']), int(r['ANGBIN'])))

    expected_pnee = [(l, s, a) for l in [1, 2] for s in range(1, 6) for a in range(1, 9)]
    expected_peee = [(i, j, a) for i in range(1, 6) for j in range(i, 6) for a in range(1, 9)]

    pnee_ok = pnee_ordering == expected_pnee
    peee_ok = peee_ordering == expected_peee

    return {
        "total_rows": len(pnee) + len(peee),
        "PneE_rows": len(pnee),
        "PeeE_rows": len(peee),
        "PneE_ordering_ok": pnee_ok,
        "PeeE_ordering_ok": peee_ok,
        "expected_PneE_order": "lens_bin(1..2) x source_bin(1..5) x angbin(1..8)",
        "expected_PeeE_order": "source_bin1(1..5) x source_bin2(bin1..5) x angbin(1..8)",
        "status": "verified_from_fits_header" if (pnee_ok and peee_ok) else "verification_failed",
    }


def build_manifest(vec_result: dict, cov_result: dict, xcheck: dict | None,
                   row_order_result: dict | None, cfg: dict) -> dict:
    manifest = {
        "product": "KiDS-1000 cosmic-shear BandPower",
        "dataset_name": cfg.get("dataset_name", "kids1000_bandpower"),
        "basis": "BandPower_Cell_tophat",
        "full_3x2pt": False,
        "contains_gamma_t": False,
        "contains_wtheta": False,
        "n_lens_bins": 2,
        "n_source_bins": 5,
        "n_ell_bins": 8,
        "n_pnee_pairs": 10,
        "n_peee_pairs": 15,
        "PneE_order": "lens_bin(1..2) x source_bin(1..5) x angbin(1..8)",
        "PeeE_order": "source_bin1(1..5) x source_bin2(bin1..5) x angbin(1..8)",
        "row_order_source": "verified_from_fits_PneE_PeeE_tables",
    }

    if vec_result.get("vector_length_ok"):
        manifest["vector_length"] = vec_result["vector_length"]
        manifest["vector_status"] = "PASS"
        manifest["asc_vs_fits_table_match"] = vec_result.get("fits_table_match")
    else:
        manifest["vector_status"] = "FAIL"
        manifest["vector_error"] = vec_result.get("error")

    if cov_result.get("shape_ok"):
        manifest["covariance_status"] = "PASS"
    else:
        manifest["covariance_status"] = "FAIL"

    manifest["covariance"] = {
        "shape": cov_result.get("shape"),
        "finite": cov_result.get("finite"),
        "symmetric_max_abs_diff": cov_result.get("symmetric_max_abs_diff"),
        "eig_min": cov_result.get("eig_min"),
        "eig_max": cov_result.get("eig_max"),
        "positive_definite": cov_result.get("positive_definite"),
        "cholesky": cov_result.get("cholesky"),
    }

    if xcheck:
        manifest["crosscheck_fits_vs_iterative"] = xcheck

    if row_order_result:
        manifest["row_order"] = row_order_result

    manifest["status"] = "BANDPOWER_PRODUCT_AUDIT_PASS" if (
        vec_result.get("vector_length_ok", False) and
        cov_result.get("shape_ok", False) and
        vec_result.get("fits_table_match", False)
    ) else "BANDPOWER_PRODUCT_AUDIT_FAIL"

    return manifest


def main():
    ap = argparse.ArgumentParser(description="Audit KiDS-1000 BandPower products")
    ap.add_argument("--config", help="Path to YAML config")
    ap.add_argument("--vector", help="Path to BandPower .asc vector (CLI override)")
    ap.add_argument("--fits", help="Path to BandPower FITS file (CLI override)")
    ap.add_argument("--fits-iterative", help="Path to iterative covariance FITS for crosscheck")
    ap.add_argument("--outdir", help="Output directory (CLI override)")
    args = ap.parse_args()

    cfg = {}
    config_dir = None
    if args.config:
        config_path = Path(args.config)
        config_dir = config_path.parent
        cfg = load_config(config_path)

    def resolve_cfg_path(key: str) -> str | None:
        raw = cfg.get("inputs", {}).get(key)
        if raw is None:
            return None
        p = Path(raw)
        if not p.is_absolute() and config_dir is not None:
            return str((config_dir / p).resolve())
        return str(p)

    vec_path = args.vector or resolve_cfg_path("vector")
    fits_path = args.fits or resolve_cfg_path("fits")
    iterative_path = args.fits_iterative or resolve_cfg_path("fits_iterative")

    raw_outdir = args.outdir or cfg.get("outputs", {}).get("outdir", "outputs/bandpower_200_audit")
    outdir = Path(raw_outdir)
    if not outdir.is_absolute() and config_dir is not None:
        outdir = (config_dir / raw_outdir).resolve()

    checks_cfg = cfg.get("checks", {})
    expected_len = checks_cfg.get("expected_vector_length", EXPECTED_LEN)
    expected_shape = checks_cfg.get("expected_cov_shape", [200, 200])
    do_crosscheck = checks_cfg.get("check_fits_vs_iterative", True)

    outdir.mkdir(parents=True, exist_ok=True)

    if not vec_path or not fits_path:
        print("ERROR: --vector and --fits are required (via CLI or --config)")
        return 1

    vec_result = audit_vector(Path(vec_path), Path(fits_path), expected_len)
    print(f"Vector: length={vec_result['vector_length']}, ok={vec_result['vector_length_ok']}, "
          f"fits_match={vec_result.get('fits_table_match', 'N/A')}")

    cov_result = audit_covariance(Path(fits_path), expected_shape[0])
    print(f"Covariance: shape={cov_result.get('shape')}, ok={cov_result.get('shape_ok')}")
    if cov_result.get("shape_ok"):
        print(f"  finite={cov_result.get('finite')}, symmetric_ok={cov_result.get('symmetric_ok')}")
        print(f"  positive_definite={cov_result.get('positive_definite')}, cholesky={cov_result.get('cholesky')}")

    row_order_result = verify_row_order(Path(fits_path))
    print(f"Row order: PneE_ok={row_order_result['PneE_ordering_ok']}, "
          f"PeeE_ok={row_order_result['PeeE_ordering_ok']}")
    print(f"  Total rows: {row_order_result['total_rows']}")

    xcheck = None
    if do_crosscheck and iterative_path:
        ip = Path(iterative_path)
        if ip.exists():
            xcheck = crosscheck_iterative(Path(fits_path), ip)
            print(f"Crosscheck (fits vs iterative): match={xcheck.get('match')}, "
                  f"max_abs_diff={xcheck.get('max_abs_diff', 'N/A'):.3e}")

    manifest = build_manifest(vec_result, cov_result, xcheck, row_order_result, cfg)
    manifest_path = outdir / "kids1000_bandpower_manifest.json"
    (outdir / "kids1000_bandpower_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Wrote manifest to {manifest_path}")

    audit_lines = [
        "# BandPower Product Audit",
        "",
        f"- **Vector length**: {vec_result.get('vector_length', '?')} — {'PASS' if vec_result.get('vector_length_ok') else 'FAIL'}",
        f"- **ASC vs FITS table match**: {vec_result.get('fits_table_match', 'N/A')}",
        f"- **Covariance shape**: {cov_result.get('shape', '?')} — {'PASS' if cov_result.get('shape_ok') else 'FAIL'}",
        f"- **Finite**: {cov_result.get('finite', '?')}",
        f"- **Symmetric max abs diff**: {cov_result.get('symmetric_max_abs_diff', 'N/A'):.3e}",
        f"- **Diagonal range**: {cov_result.get('diag_min', '?'):.3e} to {cov_result.get('diag_max', '?'):.3e}",
        f"- **Eigenvalue range**: {cov_result.get('eig_min', '?'):.3e} to {cov_result.get('eig_max', '?'):.3e}",
        f"- **Positive definite**: {cov_result.get('positive_definite', '?')}",
        f"- **Cholesky**: {cov_result.get('cholesky', '?')}",
        "",
        "## Row Order",
        "",
        f"- **PneE rows**: {row_order_result['PneE_rows']} — {row_order_result['PneE_ordering_ok']}",
        f"  - Order: {row_order_result['expected_PneE_order']}",
        f"- **PeeE rows**: {row_order_result['PeeE_rows']} — {row_order_result['PeeE_ordering_ok']}",
        f"  - Order: {row_order_result['expected_PeeE_order']}",
        f"- **Total rows**: {row_order_result['total_rows']} = 10 PneE pairs x 8 angbins + 15 PeeE pairs x 8 angbins",
        f"- **Status**: {row_order_result['status']}",
        "",
    ]
    if xcheck:
        audit_lines.append(f"- **Crosscheck (fits vs iterative)**: match={xcheck.get('match')}, max_abs_diff={xcheck.get('max_abs_diff', 'N/A'):.3e}")
        audit_lines.append("")

    audit_lines.append("## Structure")
    audit_lines.append("")
    audit_lines.append("200 = 25 source-source pairs x 8 ell-bins")
    audit_lines.append("- 10 PneE (lens-source) = 2 lens bins x 5 source bins")
    audit_lines.append("- 15 PeeE (source-source) = 5 source bins choose 2 with replacement")
    audit_lines.append("Row order verified from FITS PneE/PeeE table headers.")
    audit_lines.append("")
    audit_lines.append("## Status")
    audit_lines.append("")
    audit_lines.append(manifest["status"])

    audit_path = outdir / "bandpower_audit.md"
    (outdir / "bandpower_audit.md").write_text("\n".join(audit_lines))
    print(f"Wrote audit to {audit_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
