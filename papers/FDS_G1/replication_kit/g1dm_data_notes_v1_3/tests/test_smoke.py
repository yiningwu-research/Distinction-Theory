"""Smoke tests for g1dm_data_notes toolkit.

Verify that all core utilities and demo runs work without external data.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from g1dm.io import read_yaml, read_cosmomc_paramnames, find_parameter, weighted_quantile
from g1dm.stats import (
    gaussian_loglike,
    chi2_value,
    bic,
    aic,
    gaussian_linear_fit,
    summarize_samples,
)
from g1dm.io import load_chain_columns


def test_yaml_loads(desi_yaml_path, sro_yaml_path):
    """Both compressed YAML fixtures load with expected keys."""
    desi = read_yaml(desi_yaml_path)
    assert "parameters" in desi
    assert "mean" in desi
    assert "sigma" in desi
    assert len(desi["parameters"]) == 2
    assert len(desi["mean"]) == 2
    assert len(desi["sigma"]) == 2

    sro = read_yaml(sro_yaml_path)
    assert "observables" in sro
    assert "components" in sro
    assert len(sro["observables"]) >= 3
    assert len(sro["components"]) == 3


def test_cov_positive_def(desi_yaml_path):
    """DESI compressed covariance is positive definite."""
    cfg = read_yaml(desi_yaml_path)
    sig = np.asarray(cfg["sigma"], dtype=float)
    corr = float(cfg.get("corr", 0.0))
    cov = np.array([[sig[0]**2, corr*sig[0]*sig[1]], [corr*sig[0]*sig[1], sig[1]**2]])
    eigvals = np.linalg.eigvalsh(cov)
    assert np.all(eigvals > 0), f"Non-positive eigenvalues: {eigvals}"


def run_note(script_rel: str, extra_args: list[str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a note script with PYTHONPATH=src and return the result."""
    if cwd is None:
        cwd = Path(__file__).resolve().parent.parent
    cmd = [sys.executable, str(cwd / script_rel)]
    if extra_args:
        cmd.extend(extra_args)
    env = dict(os.environ)
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = "src" + (":" + existing_path if existing_path else "")
    env.setdefault("MPLBACKEND", "Agg")
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), env=env)


def test_note1_demo_end_to_end(tmp_path, project_root):
    """Note 1 runs with --allow-demo and produces outputs."""
    out = tmp_path / "note1"
    result = run_note("notes/note1_carrier_floor.py", ["--allow-demo", f"--out={out}"], cwd=project_root)
    assert result.returncode == 0, f"Note 1 failed:\n{result.stderr}"
    assert (out / "carrier_floor_summary.json").exists()
    assert (out / "carrier_floor_posterior.png").exists()

    with open(out / "carrier_floor_summary.json") as f:
        summary = json.load(f)
    assert float(summary["z_exclusion_of_zero"]) > 0


def test_note2_demo_end_to_end(tmp_path, project_root):
    """Note 2 runs with default constraints and produces outputs."""
    out = tmp_path / "note2"
    result = run_note("notes/note2_mu_growth_leakage.py", [f"--out={out}"], cwd=project_root)
    assert result.returncode == 0, f"Note 2 failed:\n{result.stderr}"
    assert (out / "mu_growth_leakage_summary.csv").exists()
    assert (out / "mu0_gr_consistency.png").exists()

    df = pd.read_csv(out / "mu_growth_leakage_summary.csv")
    assert len(df) == 1
    assert "z_null" in df.columns


def test_note3_demo_end_to_end(tmp_path, project_root):
    """Note 3 runs with default constraints and produces model comparison CSV."""
    out = tmp_path / "note3"
    result = run_note("notes/note3_lensing_growth_split.py", [f"--out={out}"], cwd=project_root)
    assert result.returncode == 0, f"Note 3 failed:\n{result.stderr}"
    assert (out / "lensing_growth_split_model_compare.csv").exists()

    df = pd.read_csv(out / "lensing_growth_split_model_compare.csv")
    assert len(df) == 4
    assert "model" in df.columns
    assert "delta_BIC" in df.columns


def test_note4_demo_end_to_end(tmp_path, project_root):
    """Note 4 runs with default observables and produces model comparison CSV."""
    out = tmp_path / "note4"
    result = run_note("notes/note4_sro_sparse_audit.py", [f"--out={out}"], cwd=project_root)
    assert result.returncode == 0, f"Note 4 failed:\n{result.stderr}"
    assert (out / "sro_sparse_model_compare.csv").exists()

    df = pd.read_csv(out / "sro_sparse_model_compare.csv")
    assert len(df) >= 3
    assert "model" in df.columns
    assert "delta_BIC" in df.columns


def test_note4_r_value_option(tmp_path, project_root):
    """Note 4 runs with --r-value 0.5 and produces output."""
    out = tmp_path / "note4_r"
    result = run_note("notes/note4_sro_sparse_audit.py",
                      [f"--out={out}", "--r-value", "0.5", "--scenario-label", "test_r50"],
                      cwd=project_root)
    assert result.returncode == 0, f"Note 4 with --r-value failed:\n{result.stderr}"
    assert (out / "sro_sparse_model_compare_test_r50.csv").exists()


def test_note4a_kids_validation(tmp_path, project_root):
    """Note 4a runs without local data and passes compressed check."""
    out = tmp_path / "note4a"
    result = run_note("notes/note4a_kids_s8_validation.py", [f"--out={out}"], cwd=project_root)
    assert result.returncode == 0, f"Note 4a failed:\n{result.stderr}"
    assert (out / "phase4a_validation.json").exists()
    assert "PASSED" in result.stdout or "pass" in result.stdout.lower()


def test_note4b_covariance_ready(tmp_path, project_root):
    """Note 4b-lite runs and reports BLOCKED or PASSED status."""
    out = tmp_path / "note4b"
    result = run_note("notes/note4b_kids_bandpower_covariance_ready.py", [f"--out={out}"], cwd=project_root)
    assert result.returncode == 0, f"Note 4b failed:\n{result.stderr}"


def test_extract_map_params(tmp_path, project_root):
    """MAP parameter extraction runs and produces output files."""
    map_file = project_root / "data/raw/kids_1000/cosmic_shear/KiDS1000_cosmis_shear_data_release/chains_and_config_files/main_chains_iterative_covariance/bp/chain/maxpost_multinest_start_C.txt"
    if not map_file.exists():
        pytest.skip("KiDS MAP file not available")
    out = tmp_path / "phase4c"
    result = run_note("scripts/extract_kids_map_params.py", [f"--map-file={map_file}", f"--out={out}"], cwd=project_root)
    assert result.returncode == 0, f"MAP extraction failed:\n{result.stderr}"
    assert (out / "kids_map_params.json").exists()
    assert (out / "planck_baseline_params.json").exists()
    assert (out / "values_kids.ini").exists()
    assert (out / "values_planck.ini").exists()
    import json
    with open(out / "kids_map_params.json") as f:
        params = json.load(f)
    assert "omch2" in params
    assert "s_8_input" in params


def test_stats_finite():
    """All stats helpers return finite floats."""
    x = np.array([1.0, 2.0])
    mean = np.array([1.0, 1.0])
    cov = np.array([[1.0, 0.3], [0.3, 1.0]])

    ll = gaussian_loglike(x, mean, cov)
    assert np.isfinite(ll)

    ch2 = chi2_value(x, mean, cov)
    assert np.isfinite(ch2)

    assert np.isfinite(bic(-10.0, 2, 100))
    assert np.isfinite(aic(-10.0, 2))

    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    theta, cov_t, ll2, ch2_2 = gaussian_linear_fit(x, cov, X)
    assert np.isfinite(ll2)
    assert np.isfinite(ch2_2)
    assert theta.shape == (2,)
    assert cov_t.shape == (2, 2)


def test_summarize_samples_no_weights():
    """summarize_samples works without a weight column (uniform weights)."""
    rng = np.random.default_rng(42)
    a = rng.normal(0.0, 1.0, 500)
    b = 0.5 * a + rng.normal(0.0, 0.3, 500)
    df = pd.DataFrame({"mu0": a, "Sigma0": b})
    mean, cov = summarize_samples(df)
    assert mean.shape == (2,)
    assert cov.shape == (2, 2)
    eigvals = np.linalg.eigvalsh(cov)
    assert np.all(eigvals > 0)


def test_summarize_samples_with_weights():
    """summarize_samples uses weight column when present."""
    rng = np.random.default_rng(42)
    a = rng.normal(0.0, 1.0, 500)
    b = 0.5 * a + rng.normal(0.0, 0.3, 500)
    w = rng.uniform(0.5, 1.5, 500)
    df = pd.DataFrame({"mu0": a, "Sigma0": b, "weight": w})
    mean, cov = summarize_samples(df, weight_col="weight")
    assert mean.shape == (2,)
    assert cov.shape == (2, 2)
    eigvals = np.linalg.eigvalsh(cov)
    assert np.all(eigvals > 0)


def test_cosmomc_paramnames(tmp_path):
    """read_cosmomc_paramnames parses a minimal .paramnames file."""
    pfile = tmp_path / "test.paramnames"
    pfile.write_text("a\tLabel A\nb*\tLabel B (derived)\n# comment\nc\tLabel C\n")
    names = read_cosmomc_paramnames(pfile)
    assert names == ["a", "b", "c"]


def test_find_parameter_flexibility():
    """find_parameter handles exact, case-insensitive, and regex matching."""
    df = pd.DataFrame(columns=["weight", "mu0", "Sigma0", "omega_cdm"])
    assert find_parameter(df, ["mu0"]) == "mu0"
    assert find_parameter(df, ["SIGMA0"]) == "Sigma0"
    assert find_parameter(df, [r"omega.*c"]) == "omega_cdm"

    import pytest as pt
    with pt.raises(KeyError):
        find_parameter(df, ["nonexistent"])


def test_weighted_quantile():
    """weighted_quantile returns quantiles within the data range."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    w = np.ones_like(x)
    q50 = weighted_quantile(x, 0.5, w)
    assert 1.0 <= q50.item() <= 5.0

    x2 = np.array([0.0, 1.0, 2.0])
    w2 = np.array([1.0, 0.0, 1.0])  # only zero-weighted endpoints matter
    q50b = weighted_quantile(x2, 0.5, w2)
    assert 0.0 <= q50b.item() <= 2.0


def test_load_chain_columns_demo(tmp_path):
    """load_chain_columns reads minimal chain files produced by synthetic data."""
    chain_dir = tmp_path / "chains"
    chain_dir.mkdir()
    arr = np.column_stack([
        np.ones(100),
        -np.ones(100) * 5.0,
        np.random.normal(0.05, 0.22, 100),
        np.random.normal(0.008, 0.045, 100),
    ])
    np.savetxt(chain_dir / "chain_1.txt", arr)
    param_file = chain_dir / "test.paramnames"
    param_file.write_text("mu0\tmu_0\nSigma0\tSigma_0\n")

    df = load_chain_columns(chain_dir, ["mu0", "Sigma0"])
    assert len(df) == 100
    assert "mu0" in df.columns
    assert "Sigma0" in df.columns
    assert "weight" in df.columns
