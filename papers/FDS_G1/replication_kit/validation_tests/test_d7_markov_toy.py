#!/usr/bin/env python3
"""Dedicated D7 Markov-screen toy tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reference_impl"))
from d7_markov_toy import (
    two_state_spectrum,
    toy_spectrum,
    optical_projection,
    hankel_rank_one_test,
    verify_d7_toy,
)


def test_two_state_flip():
    evals, evecs = two_state_spectrum(2.0)
    assert abs(evals[0] - 0.0) < 1e-10
    assert abs(evals[1] - 4.0) < 1e-10


def test_toy_spectrum():
    r = toy_spectrum(2.0, 1.0, 0.05, 10.0)
    assert abs(r["gamma_opt"] - 4.0) < 1e-10
    assert abs(r["Gamma_H"] - 0.1) < 1e-10
    assert abs(r["gamma_R"] - 20.0) < 1e-10
    assert abs(r["kappa"] - 0.75) < 1e-10
    assert abs(r["hankel_det"]) < 1e-10


def test_projection():
    kappa, dimU, dimOpt = optical_projection()
    assert abs(kappa - 0.75) < 1e-10
    assert dimU == 3 and dimOpt == 4


def test_hankel_single_pole():
    ok, det = hankel_rank_one_test()
    assert ok


def test_hankel_two_pole():
    Z1, G1 = 0.7, 0.01
    Z2, G2 = 0.3, 0.1
    m0 = Z1/G1 + Z2/G2
    m1 = Z1/G1**2 + Z2/G2**2
    m2 = Z1/G1**3 + Z2/G2**3
    det = m0 * m2 - m1 * m1
    assert det > 0


def test_full_verification():
    assert verify_d7_toy()
