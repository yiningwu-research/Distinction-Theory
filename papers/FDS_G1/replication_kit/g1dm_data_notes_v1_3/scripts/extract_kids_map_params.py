#!/usr/bin/env python3
"""Extract KiDS-1000 MAP parameters from the Multinest maxpost file.

Phase 4c-prep: reads the maximum-posterior parameter set that the KiDS pipeline
used and outputs a clean JSON or INI snippet for model-vector generation.
"""
from __future__ import annotations

import argparse
import json
import numpy as np
from pathlib import Path

# Column header from the KiDS BP chain output
HEADER = [
    "cosmological_parameters--omch2",
    "cosmological_parameters--ombh2",
    "cosmological_parameters--h0",
    "cosmological_parameters--n_s",
    "cosmological_parameters--s_8_input",
    "halo_model_parameters--a",
    "intrinsic_alignment_parameters--a",
    "nofz_shifts--uncorr_bias_1",
    "nofz_shifts--uncorr_bias_2",
    "nofz_shifts--uncorr_bias_3",
    "nofz_shifts--uncorr_bias_4",
    "nofz_shifts--uncorr_bias_5",
]

# Short keys for the values.ini format
INI_KEY_MAP = {
    "omch2": "omch2",
    "ombh2": "ombh2",
    "h0": "h0",
    "n_s": "n_s",
    "s_8_input": "s_8_input",
    "halo_a": "A",            # [halo_model_parameters]
    "ia_a": "A",              # [intrinsic_alignment_parameters]
    "bias_1": "uncorr_bias_1", # [nofz_shifts]
    "bias_2": "uncorr_bias_2",
    "bias_3": "uncorr_bias_3",
    "bias_4": "uncorr_bias_4",
    "bias_5": "uncorr_bias_5",
}

# Map from header column --> param dict key (used by format_values_ini)
COLUMN_TO_KEY = {
    "omch2": "omch2",
    "ombh2": "ombh2",
    "h0": "h0",
    "n_s": "n_s",
    "s_8_input": "s_8_input",
    "a": "halo_a",            # [halo_model_parameters]
    "a": "ia_a",              # ambiguous! use position-based mapping instead
    "uncorr_bias_1": "bias_1",
    "uncorr_bias_2": "bias_2",
    "uncorr_bias_3": "bias_3",
    "uncorr_bias_4": "bias_4",
    "uncorr_bias_5": "bias_5",
}

# Position-based key mapping for the first 12 columns
# These are the dict keys used by format_values_ini
POS_KEY_MAP = [
    "omch2",      # 0: cosmological_parameters--omch2
    "ombh2",      # 1: cosmological_parameters--ombh2
    "h0",         # 2: cosmological_parameters--h0
    "n_s",        # 3: cosmological_parameters--n_s
    "s_8_input",  # 4: cosmological_parameters--s_8_input
    "halo_a",     # 5: halo_model_parameters--a
    "ia_a",       # 6: intrinsic_alignment_parameters--a
    "bias_1",     # 7: nofz_shifts--uncorr_bias_1
    "bias_2",     # 8: nofz_shifts--uncorr_bias_2
    "bias_3",     # 9: nofz_shifts--uncorr_bias_3
    "bias_4",     # 10: nofz_shifts--uncorr_bias_4
    "bias_5",     # 11: nofz_shifts--uncorr_bias_5
]

# Planck 2018 TT,TE,EE+lowE baseline (Table 2)
PLANCK_BASELINE = {
    "omch2": 0.1200,
    "ombh2": 0.0224,
    "h0": 0.674,
    "n_s": 0.965,
    "s_8_input": None,  # computed from sigma8 * sqrt(omega_m / 0.3)
    "sigma8": 0.811,
}

# Default nuisance placeholders
NUISANCE_DEFAULTS = {
    "halo_a": 2.6,
    "ia_a": 1.0,
    "bias_1": 0.0,
    "bias_2": 0.0,
    "bias_3": 0.0,
    "bias_4": 0.0,
    "bias_5": 0.0,
}


def load_map_params(map_file: str) -> dict:
    """Load the KiDS MAP parameter set from a maxpost file.

    The MAP file may or may not have a comment header line.
    If present, it starts with '#'.  If not, data starts directly.
    We read only the first data line.
    """
    with open(map_file) as f:
        first_line = f.readline().strip()
        if first_line.startswith("#"):
            # Comment header present (like the chain file), space-separated
            header_line = first_line.lstrip("#").split()
            # Skip any additional comment lines, take first data line
            for line in f:
                line = line.strip()
                if not line.startswith("#"):
                    data_line = line
                    break
        else:
            # No header — first line is data; use known HEADER
            header_line = HEADER
            data_line = first_line

    values = list(map(float, data_line.split()))
    n = len(values)

    params = {}
    for i in range(min(len(POS_KEY_MAP), n)):
        params[POS_KEY_MAP[i]] = values[i]

    return params


def compute_planck_s8(params: dict) -> float:
    """Compute S8 = sigma8 * sqrt(omega_m / 0.3) from Planck baseline.

    Note: h0 in the KiDS pipeline is the dimensionless Hubble parameter
    h = H0/100.  Omega_m = (omch2 + ombh2) / h0^2.
    """
    omegac = params.get("omch2", 0.1200)
    omegab = params.get("ombh2", 0.0224)
    h0 = params.get("h0", 0.674)
    sigma8 = params.get("sigma8", 0.811)
    omegam = (omegac + omegab) / (h0 * h0)
    return sigma8 * np.sqrt(omegam / 0.3)


def build_planck_params() -> dict:
    """Build Planck baseline parameter set with computed S8."""
    params = dict(PLANCK_BASELINE)
    params["s_8_input"] = compute_planck_s8(params)
    del params["sigma8"]
    return params


def format_values_ini(params: dict) -> str:
    """Format parameter values as a values.ini snippet."""
    lines = []
    lines.append("[cosmological_parameters]")
    lines.append(f"omch2          = {params['omch2']}")
    lines.append(f"ombh2          = {params['ombh2']}")
    lines.append(f"h0             = {params['h0']}")
    lines.append(f"n_s            = {params['n_s']}")
    lines.append(f"s_8_input      = {params['s_8_input']:.4f}")
    lines.append("")
    lines.append("omega_k = 0.0")
    lines.append("w       = -1.0")
    lines.append("wa      = 0.0")
    lines.append("mnu = 0.06")
    lines.append("")
    lines.append("[halo_model_parameters]")
    lines.append(f"A = {params.get('halo_a', 2.6)}")
    lines.append("")
    lines.append("[intrinsic_alignment_parameters]")
    lines.append(f"A = {params.get('ia_a', 1.0)}")
    lines.append("")
    lines.append("[nofz_shifts]")
    for i in range(1, 6):
        lines.append(f"uncorr_bias_{i} = {params.get(f'bias_{i}', 0.0)}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map-file", required=True, help="Path to maxpost_multinest_start_C.txt")
    ap.add_argument("--out", default="outputs/phase4c_prep", help="Output directory")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    map_params = load_map_params(args.map_file)
    # Add nuisance defaults where missing
    for k, v in NUISANCE_DEFAULTS.items():
        if k not in map_params:
            map_params[k] = v

    print("KiDS MAP parameters:")
    for k, v in sorted(map_params.items()):
        print(f"  {k}: {v}")

    planck_params = build_planck_params()

    # Write JSON summaries
    with open(out / "kids_map_params.json", "w") as f:
        json.dump(map_params, f, indent=2)
    with open(out / "planck_baseline_params.json", "w") as f:
        json.dump(planck_params, f, indent=2)

    # Write values.ini snippets
    ini_kids = format_values_ini(map_params)
    ini_planck = format_values_ini(planck_params)

    with open(out / "values_kids.ini", "w") as f:
        f.write(ini_kids)
    with open(out / "values_planck.ini", "w") as f:
        f.write(ini_planck)

    print(f"\nGenerated config files in {out}/")
    print(f"  values_kids.ini  — KiDS MAP parameter set")
    print(f"  values_planck.ini — Planck 2018 baseline")

    # Print chi2 computation instructions
    print(f"""
Phase 4c-prep: To generate model vectors:

1. Copy values_kids.ini to the BP config directory (overwrite values.ini):
   cp {out}/values_kids.ini \\
     data/raw/kids_1000/cosmic_shear/KiDS1000_cosmis_shear_data_release/
     chains_and_config_files/main_chains_iterative_covariance/bp/config/values.ini

2. Update pipeline.ini KCAP_PATH and CSL_PATH to point to local installs.

3. Run evaluate-only:
   cosmosis pipeline.ini

4. The BandPower prediction vector is in the scale_cuts output section.
   Validate with: python scripts/validate_model_vector.py

5. Repeat with values_planck.ini for the Planck baseline vector.
""")


if __name__ == "__main__":
    main()
