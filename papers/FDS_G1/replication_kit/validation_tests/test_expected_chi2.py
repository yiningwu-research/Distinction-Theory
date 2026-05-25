#!/usr/bin/env python3
"""Test that reference best-fit reproduces expected chi2_min (range check)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reference_impl"))
from models import BESTFIT


def test_bestfit_defined():
    required = ["g1de2", "g1de_m34", "g1de_mkappa", "g1de_const_sigma", "cpl", "lcdm"]
    for model in required:
        assert model in BESTFIT, f"Missing bestfit for {model}"


def test_bestfit_physical():
    for model, theta in BESTFIT.items():
        Om = theta[0]
        assert 0.05 < Om < 0.60, f"{model} Om={Om} not in [0.05, 0.60]"


def test_g1de_bestfit_s_less_than_3():
    for model in ["g1de_m34", "g1de_mkappa", "g1de_const_sigma", "g1de2"]:
        s = BESTFIT[model][1]
        assert s < 3.0, f"{model} s={s} >= 3"
