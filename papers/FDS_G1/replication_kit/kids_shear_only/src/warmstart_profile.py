#!/usr/bin/env python3
"""
Warm-start local optimization for m+dz nuisance.
Starts from m-only bestfit + dz_i=0.
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).parent))
from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood

ap = argparse.ArgumentParser()
ap.add_argument("model", nargs="?", default="m34")
ap.add_argument("monly_file", nargs="?", default=None)
ap.add_argument("--config", default="stage3_kids1000_xipm_270/stage3_kids1000_xipm_270_config_cuts_mdz.yaml")
ap.add_argument("--s-max", type=float, default=3.0)
ap.add_argument("--om-max", type=float, default=None)
ap.add_argument("--inject", action="append", default=[], help="Inject param=value (e.g. --inject Sigma0=0)")
ap.add_argument("--out", default=None, help="Output JSON path (default: auto-named)")
args = ap.parse_args()
MODEL = args.model
MONLY_FILE = args.monly_file or f"monly_seed2_{MODEL}.json"
CONFIG = args.config
S_MAX = args.s_max
OM_MAX = args.om_max

# Load m-only bestfit
monly = json.load(open(MONLY_FILE))
like = Stage3Lensing3x2ptLikelihood(CONFIG, theory_backend="class", class_nk=128, class_nz=64)
names_all = like.param_names(MODEL)
bounds_all = like.bounds(MODEL)
fixed = {"h": 0.68, "Omega_b": 0.049, "n_s": 0.965}

# Build theta0 from m-only bestfit + dz=0
theta0 = []
opt_names = []
opt_bounds = []
for name, (lo, hi) in zip(names_all, bounds_all):
    if name in fixed:
        continue
    if name in monly["params"]:
        x0 = monly["params"][name]
    elif name.startswith("dz_"):
        x0 = 0.0
    else:
        # Check --inject override
        for inj in args.inject:
            k, v = inj.split("=")
            if k == name:
                x0 = float(v)
                break
        else:
            x0 = 0.5 * (lo + hi)
    # Apply s bound
    if name == "s":
        hi = min(hi, S_MAX)
    # Apply Omega_m bound expansion
    if name == "Omega_m" and OM_MAX is not None:
        hi = max(hi, OM_MAX)
    theta0.append(x0)
    opt_names.append(name)
    opt_bounds.append((lo, hi))

theta0 = np.array(theta0, dtype=float)
print(f"Warm-start: {len(opt_names)}D, starting point χ²={like.chi2(MODEL, like.prior_transform(MODEL, [0.5]*len(names_all))):.2f} (dummy)", flush=True)

# Evaluate at starting point
def full_theta(theta_opt):
    th = list(theta_opt)
    for name, val in fixed.items():
        idx = names_all.index(name)
        th.insert(idx, val)
    return th

# Get starting chi2 - need to insert fixed params
def chi2_at(theta_opt):
    th = full_theta(theta_opt)
    return float(like.chi2(MODEL, th))

chi2_start = chi2_at(theta0)
print(f"Starting χ²(bestfit_monly, dz=0) = {chi2_start:.10f}")
print(f"  expected = {monly['chi2_min']:.10f}")
print(f"  diff = {chi2_start - monly['chi2_min']:.2e}")

# Run local optimizer
t0 = time.time()
res = minimize(
    lambda t: like.chi2(MODEL, full_theta(t)),
    theta0,
    method="L-BFGS-B",
    bounds=opt_bounds,
    options={"maxiter": 50, "maxfun": 200, "ftol": 1e-10, "gtol": 1e-6},
)
elapsed = time.time() - t0

chi2_best = float(res.fun)
theta_best = full_theta(res.x)
pars_best = like.theta_to_dict(MODEL, theta_best)

# Check at_bounds
at_bnd = {}
for name, x in pars_best.items():
    idx = names_all.index(name)
    lo, hi = bounds_all[idx]
    at_bnd[name] = bool(abs(x - lo) < 1e-6 or abs(x - hi) < 1e-6)

# Derived
Om = pars_best.get("Omega_m", 0.3)
s8 = pars_best.get("sigma8", 0.8)
S8 = s8 * np.sqrt(Om / 0.3)
derived = {"S8": float(S8)}
if MODEL == "m34":
    derived["A_eff"] = float(0.75 * (3.0 - pars_best.get("s", 2.55)))

result = {
    "model": MODEL,
    "method": "L-BFGS-B warm-start",
    "starting_chi2": float(chi2_start),
    "chi2_min": float(chi2_best),
    "delta_chi2_from_start": float(chi2_best - chi2_start),
    "params": pars_best,
    "at_bounds": at_bnd,
    "derived": derived,
    "n_evals": int(res.nfev),
    "n_iters": int(res.nit),
    "success": bool(res.success),
    "runtime_seconds": round(elapsed, 2),
}
print()
print(json.dumps(result, indent=2))
if args.out:
    out_path = Path(args.out)
else:
    src_stem = Path(MONLY_FILE).stem
    out_path = Path(f"warmstart_{src_stem}_to_{MODEL}.json")
out_path.write_text(json.dumps(result, indent=2))
print(f"\nSaved to {out_path}")
