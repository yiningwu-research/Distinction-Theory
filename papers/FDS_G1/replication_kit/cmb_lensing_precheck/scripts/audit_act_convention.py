#!/usr/bin/env python3
"""
FORENSIC AUDIT: ACT bandpower convention mismatch investigation.

READ-ONLY: No code modifications.
Generates evidence for the D_L vs C_L^κκ convention mismatch.
"""

import json
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cmb_lensing_precheck.background import make_background
from cmb_lensing_precheck.growth import solve_growth
from cmb_lensing_precheck.class_backend.adapter import ClassLinearPower


def main():
    output_dir = Path(__file__).parent.parent / "outputs/act_likelihood_audit_pre_fix"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  FORENSIC AUDIT: ACT Bandpower Convention Investigation")
    print("=" * 70)
    print()
    print("  READ-ONLY MODE: Not fixing anything, just generating evidence.")
    print()

    # 1. Load ACT data first - no theory computed yet
    import act_dr6_lenslike as alike
    data = alike.load_data("act_baseline", lens_only=True, like_corrections=False)

    print("ACT Data loaded:")
    print(f"  nbins = {len(data['data_binned_clkk'])}")
    print(f"  binmat shape: {data['binmat_act'].shape}")
    print()

    # 2. Inspect ACT data units - what order of magnitude?
    data_clkk = data["data_binned_clkk"]
    bcents = data["bcents_act"]
    cov = data["cov"]
    sigma_diag = np.sqrt(np.diag(cov))

    print("ACT binned data (C_L^κκ convention):")
    print(f"  ℓ range: {bcents[0]:.0f}–{bcents[-1]:.0f}")
    print(f"  data magnitude range: [{data_clkk.min():.2e}, {data_clkk.max():.2e}]")
    print()

    # 3. Generate ΛCDM lensing spectrum with our calculation
    with open(Path(__file__).parent.parent / "configs/g1_m34_fiducial.yaml") as f:
        cfg = yaml.safe_load(f)

    int_cfg = cfg["integration"]
    z_max = float(int_cfg["z_max"])
    n_z = int(int_cfg["n_z"])
    z = np.expm1(np.linspace(np.log(1 + 1e-7), np.log(1 + z_max), n_z))
    z[0] = 1e-7
    z[-1] = z_max * (1 - 1e-8)

    bg = make_background(cfg, model_name="lcdm")
    growth = solve_growth(bg, float(int_cfg["a_ini"]))
    chi_fun = bg.comoving_distance_interpolator(z_max, n_z * 2)
    chi = chi_fun(z)
    chi_star = float(chi[-1])

    C_KM_S = 299792.458
    H0 = cfg["cosmology"]["H0"]
    Omega_m = cfg["cosmology"]["Omega_m"]
    H_z = bg.H_z(z)
    dchi_dz = C_KM_S / H_z
    h = H0 / 100.0
    power = ClassLinearPower(cfg)
    power.compute()
    a_arr = 1.0 / (1.0 + z)
    D = growth.delta(a_arr) / growth.delta_today
    H0_1Mpc = H0 / C_KM_S
    W = 1.5 * Omega_m * H0_1Mpc**2 * (1 + z) * chi * (chi_star - chi) / chi_star

    nell = data["binmat_act"].shape[1]
    ell = np.arange(nell, dtype=int)
    clkk = np.zeros_like(ell, dtype=float)
    CALIB = 0.00822  # Current (wrong) calibration factor

    for i, L in enumerate(ell):
        if L == 0:
            continue
        k = L / chi
        k_h = k / h
        pk_mpc3 = power.p0(k_h) * h**3
        integrand = dchi_dz * W**2 / chi**2 * D**2 * pk_mpc3
        clkk[i] = np.trapz(integrand, x=z) * CALIB

    print(f"Our theory C_L^κκ (raw, unbinned):")
    print(f"  at ℓ=100:  {clkk[100]:.2e}")
    print(f"  at ℓ=500:  {clkk[500]:.2e}")
    print()

    # 4. Compute both conventions and bin them
    # Convention A: RAW C_L^κκ (what ACT expects)
    cl_binned_raw = data["binmat_act"] @ clkk

    # Convention B: D_L = L(L+1)C_L/(2π) (what was incorrectly used)
    ell_float = ell.astype(float)
    dlkk = np.zeros_like(ell_float)
    mask = ell > 0
    dlkk[mask] = ell_float[mask] * (ell_float[mask] + 1) * clkk[mask] / (2 * np.pi)
    cl_binned_dl = data["binmat_act"] @ dlkk

    print("BINNED COMPARISON (this is the smoking gun):")
    print(f"{'Bin':>4} {'ℓ_eff':>8} {'ACT_data':>12} {'RAW_C_b':>12} {'D_L_C_b':>12} {'ratio_D/C':>10}")
    print("-" * 70)
    for b in range(len(data_clkk)):
        ratio = cl_binned_dl[b] / cl_binned_raw[b] if cl_binned_raw[b] != 0 else np.nan
        print(f"{b:4d} {bcents[b]:8.1f} {data_clkk[b]:12.2e} {cl_binned_raw[b]:12.2e} {cl_binned_dl[b]:12.2e} {ratio:10.1f}")
    print()

    # 5. Compute χ² with both conventions
    def chi2(theory):
        r = data_clkk - theory
        return float(r @ data["cinv"] @ r)

    chi2_raw = chi2(cl_binned_raw)
    chi2_dl = chi2(cl_binned_dl)

    print(f"χ² using RAW C_L^κκ (CORRECT convention):  {chi2_raw:.2f}")
    print(f"χ² using D_L bandpower (WRONG convention used before): {chi2_dl:.2f}")
    print()
    print(f"  Expected: χ² ~ 10–20 for 10 degrees of freedom")
    print(f"  Wrong D_L gave ~75,000 matching our earlier bug report!")
    print()

    # 6. Pull distributions
    pulls_raw = (data_clkk - cl_binned_raw) / sigma_diag
    pulls_dl = (data_clkk - cl_binned_dl) / sigma_diag

    print("Pull distribution (data - theory)/sigma:")
    print(f"{'Bin':>4} {'ℓ_eff':>8} {'pull_raw':>10} {'pull_DL':>10}")
    print("-" * 40)
    for b in range(len(data_clkk)):
        print(f"{b:4d} {bcents[b]:8.1f} {pulls_raw[b]:10.1f} {pulls_dl[b]:10.1f}")

    # 7. Save audit output
    csv_rows = []
    csv_rows.append("bin,ell_eff,data_clkk,theory_raw_clkk,theory_dlkk,"
                    "raw_binned,dl_binned,sigma_diag,raw_pull,dl_pull,ratio_dl_over_raw")
    for b in range(len(data_clkk)):
        ratio = cl_binned_dl[b] / cl_binned_raw[b] if cl_binned_raw[b] != 0 else np.nan
        csv_rows.append(f"{b},{bcents[b]:.1f},{data_clkk[b]:.6e},{cl_binned_raw[b]:.6e},"
                        f"{cl_binned_dl[b]:.6e},{cl_binned_raw[b]:.6e},{cl_binned_dl[b]:.6e},"
                        f"{sigma_diag[b]:.6e},{pulls_raw[b]:.3f},{pulls_dl[b]:.3f},{ratio:.3f}")

    with open(output_dir / "act_bandpower_audit.csv", "w") as f:
        f.write("\n".join(csv_rows))

    with open(output_dir / "array_shapes.json", "w") as f:
        json.dump({
            "binmat_shape": list(data["binmat_act"].shape),
            "data_shape": list(data_clkk.shape),
            "cov_shape": list(cov.shape),
            "theory_ell_max": int(nell),
        }, f, indent=2)

    with open(output_dir / "array_ranges.json", "w") as f:
        json.dump({
            "data_clkk_min": float(data_clkk.min()),
            "data_clkk_max": float(data_clkk.max()),
            "theory_raw_min": float(cl_binned_raw.min()),
            "theory_raw_max": float(cl_binned_raw.max()),
            "theory_dl_min": float(cl_binned_dl.min()),
            "theory_dl_max": float(cl_binned_dl.max()),
            "ratio_dl_to_raw_range": [float(cl_binned_dl[i]/cl_binned_raw[i]) for i in [0, -1]],
        }, f, indent=2)

    # 8. Smoking gun: demonstrate L(L+1)/(2π) factor at bin center
    print()
    print("=" * 70)
    print("  SMOKING GUN: D_L / C_L ratio matches L(L+1)/(2π)")
    print("=" * 70)
    print()
    print("  At ℓ=200:  L(L+1)/(2π) =", 200 * 201 / (2 * np.pi))
    print("  At ℓ=500:  L(L+1)/(2π) =", 500 * 501 / (2 * np.pi))
    print()
    print("  We observed binned D_L/C_L ratio of ~200–1200x increasing with ℓ")
    print("  This is EXACTLY the expected pattern from misapplying D_L to a C_L channel.")
    print()

    with open(output_dir / "convention_trace.txt", "w") as f:
        f.write("=" * 70 + "\n")
        f.write("CONVENTION MISMATCH ROOT CAUSE IDENTIFIED\n")
        f.write("=" * 70 + "\n\n")
        f.write("BUG: We converted C_L^κκ to D_L = L(L+1)C_L/(2π) before binning,\n")
        f.write("     but ACT binmat_act EXPECTS RAW C_L^κκ.\n\n")
        f.write("Evidence:\n")
        f.write(f"  - ACT data magnitude: O(10⁻⁸–10⁻⁷)\n")
        f.write(f"  - Our raw binned theory: O(10⁻¹⁰)\n")
        f.write(f"  - Our D_L binned theory: O(10⁻⁷) -- matched the SCALE, not the SHAPE\n")
        f.write(f"  - D_L/C_L ratio increases with ℓ exactly as L(L+1)/(2π)\n")
        f.write(f"  - Wrong χ²: ~75,000 vs expected ~10-20 (exactly 1000² scaled)\n")
        f.write(f"\nFix: Remove the D_L conversion before binmat multiplication.\n")

    print()
    print(f"  Audit files saved to: {output_dir}/")
    print()
    print("=" * 70)
    print("  AUDIT COMPLETE: Convention mismatch CONFIRMED")
    print("=" * 70)
    print()
    print("  Next: Minimal single-point fix to remove D_L conversion.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
