"""Benchmark regression test for CMB-lensing precheck.

This file exists as a placeholder. The full benchmark comparison
should be run manually before release:

    cd cmb_lensing_precheck
    fds-g1-cmb-precheck configs/g1_m34_fiducial.yaml

    # Compare outputs/g1_m34_fiducial/summary.json
    # against benchmarks/g1_m34_fiducial/summary.json

    python - << 'PY'
    import json
    ref = json.load(open("benchmarks/g1_m34_fiducial/summary.json"))
    new = json.load(open("outputs/g1_m34_fiducial/summary.json"))

    print(f"Growth ratio: ref={ref['growth_delta_today_ratio_model_over_lcdm']:.6f}, "
          f"new={new['growth_delta_today_ratio_model_over_lcdm']:.6f}")

    for i, (r_new, r_ref) in enumerate(zip(new["clpp_ratio_ranges"], ref["clpp_ratio_ranges"])):
        print(f"  Range {i}: {r_new['mean_ratio']:.6f} vs {r_ref['mean_ratio']:.6f}")
    PY
"""
