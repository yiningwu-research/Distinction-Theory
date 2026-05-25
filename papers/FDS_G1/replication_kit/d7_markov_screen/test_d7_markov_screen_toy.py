#!/usr/bin/env python3
"""
Minimal tests for d7_markov_screen_toy.py.

Run:
    python test_d7_markov_screen_toy.py
"""

import math
import numpy as np

from d7_markov_screen_toy import (
    ToyParameters,
    positive_relaxation_eigenvalues,
    optical_kappa,
    optical_gamma,
    horizon_gamma,
    ricci_gamma,
    rank_one_hankel_diagnostic,
    ricci_leakage_proxy,
)


def assert_close(x, y, tol=1e-12, msg=""):
    if abs(x - y) > tol:
        raise AssertionError(f"{msg} Expected {y}, got {x}")


def test_two_state_spectrum():
    vals = positive_relaxation_eigenvalues(3.0)
    assert_close(vals[0], 0.0, msg="zero eigenvalue")
    assert_close(vals[1], 6.0, msg="two-state flip eigenvalue")


def test_optical_kappa():
    assert_close(optical_kappa(), 0.75, msg="kappa=3/4")


def test_gamma_relations():
    p = ToyParameters(r_opt=2.0, r_h=5.0, epsilon=0.01, r_ricci=7.0)
    assert_close(optical_gamma(p), 4.0, msg="gamma_opt=2*r_opt")
    assert_close(horizon_gamma(p), 0.1, msg="Gamma_H=2*epsilon*r_H")
    assert_close(ricci_gamma(p), 14.0, msg="gamma_R=2*r_R")


def test_rank_one_hankel():
    h = rank_one_hankel_diagnostic(gamma=0.25, residue=2.0)
    assert_close(h, 0.0, tol=1e-10, msg="rank-one Hankel diagnostic")


def test_ricci_leakage_decreases():
    l10 = ricci_leakage_proxy(k_rr=10.0)
    l100 = ricci_leakage_proxy(k_rr=100.0)
    l1000 = ricci_leakage_proxy(k_rr=1000.0)
    assert l10 > l100 > l1000, "Ricci leakage proxy should decrease with stiffness"


if __name__ == "__main__":
    test_two_state_spectrum()
    test_optical_kappa()
    test_gamma_relations()
    test_rank_one_hankel()
    test_ricci_leakage_decreases()
    print("All D7 Markov-screen toy tests passed.")
