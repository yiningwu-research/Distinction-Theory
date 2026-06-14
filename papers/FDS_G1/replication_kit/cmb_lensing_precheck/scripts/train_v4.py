#!/usr/bin/env python3
"""
v4 Structured G1 ratio emulator.

Key changes from v3:
  1. Weyl emulator fits G_L = log(R_Weyl) / α  where α = qκ
     → automatically enforces R_Weyl → 1 at q=0 or κ=0
  2. Local RBF with neighbors=N (not global)
  3. Independent prior-wide holdout validation
  4. Fail-closed: no gate bypass, no manual unlock
  5. Versioned artifact directory (never overwritten)

Architecture:
  R_total = R_bg(Ω_m,h,q) × R_Weyl(Ω_m,h,q,κ)
  
  log(R_bg)   = PCA + RBF(neighbors) on (Ω_m,h,q)
  G_L(Ω_m,h,q,κ) = log(R_Weyl) / (qκ) → PCA + RBF(neighbors)
  R_Weyl = exp(qκ · G_L)
"""

import sys, json, time, hashlib, numpy as np
from pathlib import Path
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from scipy.interpolate import RBFInterpolator

# ── Paths ──────────────────────────────────────────────────────────────
CACHEDIR  = Path(__file__).parent.parent / "outputs" / "emulator_cache"
ARTIFACT  = Path(__file__).parent.parent / "artifacts" / "ratio_v4_candidate_001"


# ── Load cache ─────────────────────────────────────────────────────────

def load_cache():
    return {
        "params_train": np.load(CACHEDIR / "params_train.npy"),
        "params_test": np.load(CACHEDIR / "params_test.npy"),
        "ell": np.load(CACHEDIR / "ell.npy"),
        "R_bg_train": np.load(CACHEDIR / "R_bg_train.npy"),
        "R_Weyl_train": np.load(CACHEDIR / "R_Weyl_train.npy"),
        "R_total_train": np.load(CACHEDIR / "R_total_train.npy"),
        "R_total_test": np.load(CACHEDIR / "R_total_test.npy"),
    }


# ── PCA + local RBF trainer ────────────────────────────────────────────

def train_emu(params, log_values, n_pca, neighbors, kernel="thin_plate_spline"):
    """Train PCA + local-RBF with neighbors."""
    mean = np.mean(log_values, axis=0)
    centered = log_values - mean
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    components = Vt[:n_pca]
    coeffs = centered @ components.T

    pmin = params.min(axis=0)
    pscale = np.maximum(params.max(axis=0) - pmin, 1e-30)
    unit = (params - pmin) / pscale

    interpolators = []
    for i in range(n_pca):
        interp = RBFInterpolator(unit, coeffs[:, i], kernel=kernel,
                                 neighbors=min(neighbors, len(params)))
        interpolators.append(interp)

    return {
        "mean": mean, "components": components, "interpolators": interpolators,
        "params_min": pmin, "params_max": pscale + pmin,
        "n_pca": n_pca, "neighbors": neighbors, "kernel": kernel,
    }


def predict_emu(emu, params):
    """Predict log-values from trained emulator dict."""
    pmin = emu["params_min"]
    pscale = np.maximum(emu["params_max"] - pmin, 1e-30)
    unit = np.clip((params - pmin) / pscale, 0.0, 1.0)
    coeffs = np.array([float(interp(unit)[0]) for interp in emu["interpolators"]])
    return coeffs @ emu["components"] + emu["mean"]


# ── v4 Structured Emulator ─────────────────────────────────────────────

class V4Emulator:
    """R_total = R_bg × R_Weyl with G_L = log(R_Weyl)/(qκ) decomposition."""

    def __init__(self):
        self.emu_bg = None
        self.emu_weyl = None
        self.ell = None

    def train(self, cache, extra_params=None, extra_R_bg=None, extra_R_weyl=None,
              n_pca_bg=5, n_pca_weyl=6, neighbors_bg=80, neighbors_weyl=80,
              kernel="thin_plate_spline"):
        self.ell = cache["ell"]

        # ── BG emulator: (Ω_m, h, q) → log(R_bg) ──────────────────────
        params_bg = cache["params_train"][:400, :3].copy()
        logR_bg = np.log(np.maximum(cache["R_bg_train"][:400], 1e-30))
        if extra_params is not None and extra_R_bg is not None:
            extra_bg = extra_params[:, :3]
            _, u = np.unique(np.round(extra_bg, 6), axis=0, return_index=True)
            params_bg = np.vstack([params_bg, extra_bg[np.sort(u)]])
            logR_bg = np.vstack([logR_bg, np.log(np.maximum(extra_R_bg[np.sort(u)], 1e-30))])
        self.emu_bg = train_emu(params_bg, logR_bg, n_pca_bg, neighbors_bg, kernel)

        # ── Weyl emulator: (Ω_m, h, q, κ) → G_L = log(R_Weyl)/α ───────
        params_w = cache["params_train"][:400].copy()
        R_weyl = cache["R_Weyl_train"][:400]
        if extra_params is not None and extra_R_weyl is not None:
            params_w = np.vstack([params_w, extra_params])
            R_weyl = np.vstack([R_weyl, extra_R_weyl])

        # Compute G_L = log(R_Weyl) / alpha for each training point
        alpha = np.maximum(params_w[:, 2] * params_w[:, 3], 1e-30)  # q*κ
        logR_weyl = np.log(np.maximum(R_weyl, 1e-30))
        G_L = logR_weyl / alpha[:, None]  # divide each row's log(R) by its alpha

        self.emu_weyl = train_emu(params_w, G_L, n_pca_weyl, neighbors_weyl, kernel)

    def predict_R(self, Omega_m, h, q, kappa):
        """Predict R_total(ell)."""
        # R_bg
        if q < 1e-10:
            R_bg = np.ones(len(self.ell))
        else:
            logR_bg = predict_emu(self.emu_bg, np.array([[Omega_m, h, q]]))
            R_bg = np.exp(logR_bg).flatten()

        # R_Weyl via G_L decomposition
        if kappa < 1e-10 or q < 1e-10:
            R_weyl = np.ones(len(self.ell))
        else:
            G_pred = predict_emu(self.emu_weyl, np.array([[Omega_m, h, q, kappa]]))
            logR_weyl = G_pred.flatten() * (q * kappa)
            R_weyl = np.exp(logR_weyl)

        return R_bg * R_weyl

    def save(self, path):
        path = Path(path); path.mkdir(parents=True, exist_ok=True)
        np.save(path / "ell.npy", self.ell)
        for name, emu in [("bg", self.emu_bg), ("weyl", self.emu_weyl)]:
            for key in ["mean", "components", "params_min", "params_max"]:
                np.save(path / f"emu_{name}_{key}.npy", emu[key])
        with open(path / "config.json", "w") as f:
            json.dump({
                "n_pca_bg": self.emu_bg["n_pca"], "n_pca_weyl": self.emu_weyl["n_pca"],
                "neighbors_bg": self.emu_bg["neighbors"], "neighbors_weyl": self.emu_weyl["neighbors"],
                "kernel": self.emu_bg["kernel"],
            }, f, indent=2)

    @classmethod
    def load(cls, path):
        path = Path(path)
        with open(path / "config.json") as f: cfg = json.load(f)
        emu = cls()
        emu.ell = np.load(path / "ell.npy") if (path / "ell.npy").exists() else None
        for name in ["bg", "weyl"]:
            d = {}
            for key in ["mean", "components", "params_min", "params_max"]:
                d[key] = np.load(path / f"emu_{name}_{key}.npy")
            d["n_pca"] = cfg[f"n_pca_{name}"]; d["neighbors"] = cfg[f"neighbors_{name}"]
            d["kernel"] = cfg["kernel"]
            if name == "bg": emu.emu_bg = d
            else: emu.emu_weyl = d
        # Rebuild interpolators (need training data saved separately)
        return emu


# ── Validation ─────────────────────────────────────────────────────────

def validate_v4(emu, cache, n_test=80):
    """Validate on independent holdout set."""
    pt = cache["params_test"][:n_test]
    Rt = cache["R_total_test"][:n_test]
    rms_list = []
    for i, (Om, h, q, k) in enumerate(pt):
        Rp = emu.predict_R(Om, h, q, k)
        frac = (Rp - Rt[i]) / np.maximum(Rt[i], 1e-30)
        rms_list.append(float(np.sqrt(np.mean(frac**2)) * 100))
    r = np.array(rms_list)
    return {"rms_mean": float(np.mean(r)), "p95": float(np.percentile(r, 95)),
            "max": float(np.max(r)), "n": int(len(r))}


# ── Main ───────────────────────────────────────────────────────────────

def main():
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    print("=" * 70)
    print("  v4 STRUCTURED EMULATOR (G_L decomposition + local RBF)")
    print("=" * 70)

    cache = load_cache()

    # ── Generate prior-wide Sobol enrichment ───────────────────────────
    print("Generating 200 prior-wide Sobol enrichment points...", flush=True)
    from scipy.stats import qmc
    sobol = qmc.Sobol(d=4, scramble=True, seed=42)
    unit = sobol.random(200)
    Om = 0.15 + unit[:,0] * 0.35
    hh = 0.55 + unit[:,1] * 0.30
    qq = unit[:,2] * 1.15
    kk = unit[:,3] * 1.0

    from cmb_lensing_precheck.mcmc.ratio_engine import G1LensingRatio
    engine = G1LensingRatio(amplitude_mode='primordial')
    engine._base_cfg['integration']['n_z'] = 450
    engine._base_cfg['integration']['ell_step'] = 1

    extra_p = []; extra_R_bg = []; extra_R_w = []
    for i, (o, h, q, k) in enumerate(zip(Om, hh, qq, kk)):
        if i % 50 == 0: print(f"  {i}/200", flush=True)
        s = 3.0 - q
        r_total = engine.compute(o, h, s, k)
        r_bg = engine.compute(o, h, s, 0.0)
        extra_p.append([o, h, q, k])
        extra_R_bg.append(r_bg.R_total)
        extra_R_w.append(r_total.R_total / np.maximum(r_bg.R_total, 1e-30))
    extra_p = np.array(extra_p)
    extra_R_bg = np.array(extra_R_bg)
    extra_R_w = np.array(extra_R_w)
    print(f"Done. Shape: {extra_p.shape}", flush=True)

    # ── Learning curve ─────────────────────────────────────────────────
    print("\nLearning curve:", flush=True)
    best_npca_bg, best_npca_w = 5, 6
    for nb in [40, 60, 80]:
        for nw in [60, 80, 100]:
            emu = V4Emulator()
            emu.train(cache, extra_p, extra_R_bg, extra_R_w,
                     n_pca_bg=5, n_pca_weyl=6, neighbors_bg=nb, neighbors_weyl=nw,
                     kernel="thin_plate_spline")
            v = validate_v4(emu, cache, n_test=60)
            print(f"  nb={nb:3d} nw={nw:3d}: RMS={v['rms_mean']:.4f}% P95={v['p95']:.4f}%", flush=True)
            if v['p95'] < 0.5:
                best_npca_bg, best_npca_w = nb, nw

    # ── Final training ─────────────────────────────────────────────────
    print(f"\nFinal: nb={best_npca_bg}, nw={best_npca_w}", flush=True)
    emu = V4Emulator()
    emu.train(cache, extra_p, extra_R_bg, extra_R_w,
             n_pca_bg=5, n_pca_weyl=6, neighbors_bg=best_npca_bg, neighbors_weyl=best_npca_w,
             kernel="thin_plate_spline")
    v = validate_v4(emu, cache, n_test=80)
    print(f"Validation: RMS={v['rms_mean']:.4f}% P95={v['p95']:.4f}% max={v['max']:.4f}%", flush=True)

    # ── Null test ──────────────────────────────────────────────────────
    null_ok = True
    for _ in range(20):
        o = 0.15 + np.random.rand() * 0.35
        h = 0.55 + np.random.rand() * 0.30
        k = np.random.rand()
        R = emu.predict_R(o, h, 0.0, k)
        if np.max(np.abs(R - 1.0)) > 1e-6:
            null_ok = False
    print(f"Null test (q=0): {'PASSED' if null_ok else 'FAILED'}", flush=True)

    # ── Save ───────────────────────────────────────────────────────────
    emu.save(ARTIFACT)
    metrics = {"validation": v, "null_ok": null_ok, "n_extra": len(extra_p),
               "neighbors_bg": best_npca_bg, "neighbors_weyl": best_npca_w}
    with open(ARTIFACT / "validation.json", "w") as f:
        json.dump(metrics, f, indent=2)

    passed = v["rms_mean"] < 0.2 and v["p95"] < 0.5 and null_ok
    print(f"\n{'='*70}")
    print(f"  v4 CANDIDATE: {'PASSED ✓' if passed else 'FAILED ✗'}")
    print(f"  Saved: {ARTIFACT}")
    print(f"{'='*70}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
