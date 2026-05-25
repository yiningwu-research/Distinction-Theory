#!/usr/bin/env python3
"""Cross-check prior bounds against model parameter counts."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reference_impl"))
from models import BOUNDS, PARAM_NAMES


def test_bounds_consistency():
    for model, bounds in BOUNDS.items():
        nparams = len(PARAM_NAMES[model])
        assert len(bounds) == nparams, f"{model}: {len(bounds)} bounds != {nparams} params"
        for lo, hi in bounds:
            assert lo < hi, f"{model} bound: {lo} >= {hi}"


def test_all_models_have_bounds():
    for model in PARAM_NAMES:
        assert model in BOUNDS, f"Missing bounds for {model}"
