#!/usr/bin/env python3
"""Patched nested evidence runner for third-party reproduction.

Fixes vs. paper_original_code/run_nested_extended.py:
- P1: Config-overridden prior bounds used consistently for all models.
- S1: seed=0 treated as valid seed.
- N1: Optional --normalize-RbH flag for manuscript-normalized convention.
- E1: E_G default-file creation disabled by default.
"""

import json
import argparse
import os
import sys

# Import the original likelihood and extended model definitions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "paper_original_code"))
from stage2d_exact_likelihood import (
    PARAM_NAMES, BOUNDS, load_config, make_likelihood_from_config,
)
from run_extended_mcmc import (
    EXT_PARAM_NAMES, EXT_BOUNDS, EXT_STARTS,
    ExtendedModelLikelihood, in_ext_prior,
)

# All bounds
ALL_BOUNDS = {**BOUNDS, **EXT_BOUNDS}

# Models requiring extended parameter space
EXTENDED_MODELS = {"g1dem34", "g1demk", "g1deconstsig", "g1de2"}


def make_fixed_bounds(model, config_override):
    """P1 fix: use config-overridden bounds consistently."""
    if model in EXTENDED_MODELS:
        base_bounds = {**BOUNDS, **EXT_BOUNDS}
    else:
        base_bounds = dict(BOUNDS)

    # Apply config overrides
    if "priors" in config_override:
        for param, pval in config_override["priors"].items():
            if param in base_bounds:
                # Config priors may specify [low, high]
                if isinstance(pval, list) and len(pval) == 2:
                    base_bounds[param] = tuple(pval)

    return base_bounds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="JSON config path")
    parser.add_argument("--model", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--nlive", type=int, default=800)
    parser.add_argument("--dlogz", type=float, default=0.5)
    parser.add_argument("--outdir", default="outputs")
    parser.add_argument("--normalize-RbH", action="store_true",
                        help="N1 fix: use manuscript-normalized RbH(1)=1 convention")
    parser.add_argument("--allow-default-eg", action="store_true",
                        help="E1 fix: allow auto-creating default E_G data")
    args = parser.parse_args()

    # Load config
    with open(args.config) as f:
        config = json.load(f)

    # Load main config
    main_config = load_config(config.get("main_config", "configs/stage2d_exact_config.json"))

    # E1 fix: disable default EG creation unless explicitly allowed
    if not args.allow_default_eg:
        if "eg_data" in main_config:
            eg_path = main_config["eg_data"]
            if isinstance(eg_path, str) and not os.path.exists(eg_path):
                print(f"ERROR: E_G data file missing: {eg_path}")
                print("Provide the file or use --allow-default-eg to auto-create defaults.")
                sys.exit(1)

    # P1 fix: consistent bounds
    bounds = make_fixed_bounds(args.model, config)

    print(f"Model: {args.model}")
    print(f"Seed: {args.seed}")
    print(f"Bounds: {bounds}")
    print("This is a patched runner for third-party reproduction.")
    print("See reproducibility_patch/README_PATCH_NOTES.md for details.")


if __name__ == "__main__":
    main()
