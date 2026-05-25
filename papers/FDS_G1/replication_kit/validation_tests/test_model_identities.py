#!/usr/bin/env python3
"""
Validation tests for G1DE model identities and D7 Markov-screen toy.

Run: python -m pytest validation_tests/ -v
"""

import sys
sys.path.insert(0, "reference_impl")

import numpy as np


def test_model_identities():
    from models import verify_model_identities
    assert verify_model_identities()


def test_d7_toy():
    from d7_markov_toy import verify_d7_toy
    assert verify_d7_toy()


def test_prior_bounds():
    from models import BOUNDS, PARAM_NAMES
    for model, bounds in BOUNDS.items():
        nparams = len(PARAM_NAMES[model])
        assert len(bounds) == nparams, f"{model} bounds/names mismatch"
        for lo, hi in bounds:
            assert lo < hi, f"{model} bound not ordered: {lo} >= {hi}"


def test_no_free_amplitude():
    from models import PARAM_NAMES
    for model, names in PARAM_NAMES.items():
        assert "A" not in names, f"{model} has free amplitude!"
        assert "amplitude" not in [n.lower() for n in names]


def test_xhat_range():
    from models import Xhat_a
    x = Xhat_a(np.array([1.0]), 0.3, 2.5)
    # Xhat(1) = 4*Om*(1-Om) for Om=0.3: 0.84
    # Code uses Xhat directly; paper uses normalized R̂_H = Xhat/Xhat(1)
    assert 0.8 < x[0] < 0.9, f"Xhat(1)={x[0]} out of expected range"


def test_kappa_three_fourths():
    from d7_markov_toy import optical_projection
    kappa, dimU, dimOpt = optical_projection()
    assert abs(kappa - 0.75) < 1e-10
    assert dimU == 3 and dimOpt == 4


def test_two_state_eigenvalues():
    from d7_markov_toy import two_state_spectrum
    evals, _ = two_state_spectrum(2.0)
    assert abs(evals[0] - 0.0) < 1e-10
    assert abs(evals[1] - 4.0) < 1e-10


def test_rank_one_hankel():
    from d7_markov_toy import hankel_rank_one_test
    ok, det = hankel_rank_one_test()
    assert ok, f"Single-pole hankel_det != 0: {det}"


def test_two_pole_hankel_nonzero():
    """Two-pole Hankel determinant is positive."""
    Z1, G1 = 0.7, 0.01
    Z2, G2 = 0.3, 0.1
    m0 = Z1/G1 + Z2/G2
    m1 = Z1/G1**2 + Z2/G2**2
    m2 = Z1/G1**3 + Z2/G2**3
    det = m0 * m2 - m1 * m1
    assert det > 0, f"Two-pole hankel_det should be > 0: {det}"
