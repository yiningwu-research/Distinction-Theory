#!/usr/bin/env python3
"""
Run all three L0 MCMC model families:
- bg_only: κ = 0
- m34: κ = 0.75
- free_kappa: κ sampled

For both:
- act_baseline
- actplanck_baseline
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent.parent

variants = ['act_baseline', 'actplanck_baseline']
models = ['bg_only', 'm34', 'free_kappa']

n_walkers = 40
n_steps = 5000

print("=" * 70)
print("  L0 MCMC BATCH RUN")
print(f"  Variants: {variants}")
print(f"  Models: {models}")
print(f"  Walkers: {n_walkers}, Steps: {n_steps}")
print("=" * 70)
print()

for variant in variants:
    for model in models:
        print(f"\n{'=' * 70}")
        print(f"  Running: {variant} / {model}")
        print(f"{'=' * 70}")
        print()
        
        cmd = [
            sys.executable,
            str(script_dir / "scripts/run_phase3_mcmc_l0.py"),
            f"--variant={variant}",
            f"--model={model}",
            f"--n-walkers={n_walkers}",
            f"--n-steps={n_steps}",
        ]
        
        result = subprocess.run(cmd, cwd=script_dir)
        if result.returncode != 0:
            print(f"ERROR: {variant}/{model} failed with code {result.returncode}")

print()
print("=" * 70)
print("  ALL RUNS COMPLETE")
print("=" * 70)
