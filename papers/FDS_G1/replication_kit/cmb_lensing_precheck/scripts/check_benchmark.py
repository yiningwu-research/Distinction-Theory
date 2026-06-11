#!/usr/bin/env python3
"""Benchmark regression checker for CMB-lensing precheck.

Compares a new run summary against the canonical benchmark and
fails if differences exceed registered tolerance levels.

Usage:
    python scripts/check_benchmark.py \
        benchmarks/g1_m34_fiducial/summary.json \
        outputs/g1_m34_fiducial/summary.json

Tolerances:
    Growth ratio: rtol=1e-10, atol=1e-12  (should be near exact)
    CL mean ratios: rtol=1e-8, atol=1e-12  (platform/version numerical diffs)

Returns:
    0 on success, 1 on failure
"""
import argparse
import json
import sys


def compare_scalar(ref, new, key, rtol, atol):
    r = float(ref)
    n = float(new)
    if abs(n - r) > atol + rtol * abs(r):
        print(f"  FAIL: {key}: ref={r:.12g}, new={n:.12g}, diff={abs(n-r):.2e}")
        return False
    print(f"  OK:   {key}: ref={r:.12g}, new={n:.12g}")
    return True


def main():
    p = argparse.ArgumentParser(description="CMB-lensing benchmark regression checker")
    p.add_argument("ref_json", help="Reference benchmark summary.json")
    p.add_argument("new_json", help="New run summary.json")
    p.add_argument("--rtol", type=float, default=1e-8, help="Relative tolerance")
    p.add_argument("--atol", type=float, default=1e-12, help="Absolute tolerance")
    args = p.parse_args()

    with open(args.ref_json) as f:
        ref = json.load(f)
    with open(args.new_json) as f:
        new = json.load(f)

    print(f"Reference: {args.ref_json}")
    print(f"New run:   {args.new_json}")
    print()
    print(f"Tolerances: rtol={args.rtol:.2e}, atol={args.atol:.2e}")
    print()
    print("=== Growth ratio ===")
    key = "growth_delta_today_ratio_model_over_lcdm"
    ok = compare_scalar(ref[key], new[key], key, rtol=1e-10, atol=1e-12)

    print()
    print("=== CL mean ratios ===")
    for i, (r_ref, r_new) in enumerate(zip(ref["clpp_ratio_ranges"], new["clpp_ratio_ranges"])):
        lo, hi = r_ref["ell_min"], r_ref["ell_max"]
        ok = compare_scalar(
            r_ref["mean_ratio"],
            r_new["mean_ratio"],
            f"L={lo}-{hi} mean",
            rtol=args.rtol,
            atol=args.atol,
        ) and ok

    print()
    if ok:
        print("✅ All benchmark values match within tolerance!")
        return 0
    else:
        print("❌ Some values differ beyond tolerance!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
