#!/usr/bin/env python3
"""Make a synthetic LCDM-centered NPZ likelihood for smoke testing only."""

from pathlib import Path
import numpy as np

source = Path("outputs/g1_m34_fiducial/clpp.csv")
if not source.exists():
    raise SystemExit("Run the fiducial precheck first: fds-g1-cmb-precheck configs/g1_m34_fiducial.yaml")
table = np.loadtxt(source, delimiter=",", skiprows=1)
ell_full, clkk = table[:, 0], table[:, 3]
ell = np.geomspace(20, 1200, 18).astype(int)
data = np.interp(ell, ell_full, clkk)
sigma = 0.025 * np.maximum(np.abs(data), np.max(np.abs(data)) * 1e-3)
cov = np.diag(sigma**2)
out = Path("data")
out.mkdir(exist_ok=True)
np.savez(out / "synthetic_lcdm_clkk.npz", data=data, cov=cov, ell=ell, quantity=np.array("clkk"))
print(out / "synthetic_lcdm_clkk.npz")
