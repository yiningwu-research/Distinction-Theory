#!/usr/bin/env python3
"""
D7 finite Markov-screen toy model.

This is a minimal reference implementation for the D7 toy construction:
a finite detailed-balance Markov-screen prototype whose optical symmetry
gives kappa_BW = 3/4, whose slow horizon flip gives a rank-one output
response, and whose Ricci stiffness suppresses leakage.

This is an existence / sanity-check prototype, not unique spacetime
microphysics.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ToyParameters:
    """Parameters for the D7 Markov-screen toy model."""
    r_opt: float = 1.0       # symmetric flip rate for optical ports
    r_h: float = 1.0         # base horizon flip rate
    epsilon: float = 0.02    # horizon slow-mode suppression
    r_ricci: float = 8.0     # Ricci relaxation rate
    z_h: float = 1.0         # horizon response residue


def two_state_generator(rate: float) -> np.ndarray:
    """
    Return the continuous-time Markov generator Q for a symmetric two-state flip.

    States are {-1, +1}. With rate r for each direction:
        Q = [[-r, r],
             [ r,-r]]

    The positive relaxation generator is L = -Q, with eigenvalues {0, 2r}.
    """
    if rate < 0:
        raise ValueError("rate must be nonnegative")
    return np.array([[-rate, rate], [rate, -rate]], dtype=float)


def positive_relaxation_eigenvalues(rate: float) -> np.ndarray:
    """
    Positive eigenvalues of L=-Q for a symmetric two-state flip.
    """
    Q = two_state_generator(rate)
    L = -Q
    vals = np.linalg.eigvalsh(L)
    vals[np.abs(vals) < 1e-14] = 0.0
    return np.sort(vals)


def optical_kappa(epsilon_aniso: float = 0.0) -> float:
    """
    Compute the optical Weyl-active fraction.

    Exact isotropic optical block:
        ports = A, S1, S2, T
        Weyl-active = S1, S2, T
        kappa = 3/4

    If epsilon_aniso is supplied, this function uses a simple diagonal
    anisotropic perturbation as a toy diagnostic.
    """
    # compliance weights for A, S1, S2, T
    weights = np.array([
        1.0 + epsilon_aniso,
        1.0,
        1.0,
        1.0 - epsilon_aniso,
    ], dtype=float)
    total = weights.sum()
    weyl_active = weights[1:].sum()
    return float(weyl_active / total)


def horizon_gamma(params: ToyParameters) -> float:
    """
    Slow horizon relaxation eigenvalue Gamma_H = 2 * epsilon * r_H.
    """
    return 2.0 * params.epsilon * params.r_h


def optical_gamma(params: ToyParameters) -> float:
    """
    Optical relaxation eigenvalue gamma_opt = 2 * r_opt.
    """
    return 2.0 * params.r_opt


def ricci_gamma(params: ToyParameters, lambda_ricci: float = 0.0) -> float:
    """
    Ricci relaxation/stiffness scale.

    The Markov flip contribution gives 2*r_ricci. A separate stiffness
    penalty lambda_ricci may be used as a toy representation of Ward
    conditioning.
    """
    return 2.0 * params.r_ricci + lambda_ricci


def stieltjes_rank_one_chi(s: float | np.ndarray, gamma: float, residue: float = 1.0) -> float | np.ndarray:
    """
    Rank-one Stieltjes response chi(s)=Z/(s+gamma).
    """
    if gamma <= 0:
        raise ValueError("gamma must be positive")
    return residue / (np.asarray(s) + gamma)


def rank_one_moment(n: int, gamma: float, residue: float = 1.0) -> float:
    """
    Moment m_n for a single positive Stieltjes pole Z/(s+gamma):

        m_n = Z / gamma^(n+1).

    This convention is useful for the Hankel diagnostic m0*m2 - m1^2.
    """
    if n < 0:
        raise ValueError("moment index n must be nonnegative")
    if gamma <= 0:
        raise ValueError("gamma must be positive")
    return float(residue / (gamma ** (n + 1)))


def rank_one_hankel_diagnostic(gamma: float, residue: float = 1.0) -> float:
    """
    Compute m0*m2 - m1^2. It vanishes for a single-pole response.
    """
    m0 = rank_one_moment(0, gamma, residue)
    m1 = rank_one_moment(1, gamma, residue)
    m2 = rank_one_moment(2, gamma, residue)
    return float(m0 * m2 - m1 * m1)


def ricci_leakage_proxy(k_ww: float = 1.0, k_rr: float = 100.0, k_wr: float = 1.0) -> float:
    """
    Simple Schur-complement-inspired Ricci leakage proxy.

    Larger Ricci stiffness k_rr suppresses leakage approximately as k_wr^2/k_rr.
    This is a toy algebraic proxy only. The explicit H^2/k^2 scaling used in
    the cosmological production model is a Ward-to-Boltzmann scalar-sector
    bridge, not derived directly from this finite Markov chain.
    """
    if k_rr <= 0:
        raise ValueError("k_rr must be positive")
    return float((k_wr * k_wr) / (k_ww * k_rr))


def summarize(params: ToyParameters) -> dict[str, float]:
    """
    Return main D7 toy quantities.
    """
    gamma_opt = optical_gamma(params)
    gamma_h = horizon_gamma(params)
    gamma_r = ricci_gamma(params)
    kappa = optical_kappa()
    hankel = rank_one_hankel_diagnostic(gamma_h, params.z_h)
    return {
        "kappa_BW": kappa,
        "gamma_opt": gamma_opt,
        "Gamma_H": gamma_h,
        "gamma_R": gamma_r,
        "rank_one_hankel_m0m2_minus_m1sq": hankel,
        "ricci_leakage_proxy_KRR_10": ricci_leakage_proxy(k_rr=10.0),
        "ricci_leakage_proxy_KRR_100": ricci_leakage_proxy(k_rr=100.0),
        "ricci_leakage_proxy_KRR_1000": ricci_leakage_proxy(k_rr=1000.0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D7 finite Markov-screen toy checks.")
    parser.add_argument("--r-opt", type=float, default=1.0, help="optical flip rate")
    parser.add_argument("--r-h", type=float, default=1.0, help="base horizon flip rate")
    parser.add_argument("--epsilon", type=float, default=0.02, help="horizon slow-mode suppression")
    parser.add_argument("--r-ricci", type=float, default=8.0, help="Ricci relaxation rate")
    parser.add_argument("--z-h", type=float, default=1.0, help="horizon Stieltjes pole residue")
    args = parser.parse_args()

    params = ToyParameters(
        r_opt=args.r_opt,
        r_h=args.r_h,
        epsilon=args.epsilon,
        r_ricci=args.r_ricci,
        z_h=args.z_h,
    )

    print("D7 finite Markov-screen toy model")
    print("---------------------------------")
    print(f"parameters = {params}")
    print()

    print("Two-state flip spectra:")
    print(f"  optical L spectrum = {positive_relaxation_eigenvalues(params.r_opt)}")
    print(f"  horizon L spectrum = {positive_relaxation_eigenvalues(params.epsilon * params.r_h)}")
    print(f"  Ricci L spectrum   = {positive_relaxation_eigenvalues(params.r_ricci)}")
    print()

    results = summarize(params)
    for key, value in results.items():
        print(f"{key:40s} = {value:.12g}")

    print()
    print("Interpretation:")
    print("  kappa_BW = 3/4 follows from the exact isotropic A,S1,S2,T optical block.")
    print("  Gamma_H = 2*epsilon*r_H is the slow horizon eigenvalue.")
    print("  rank_one_hankel = 0 is the single-pole Stieltjes diagnostic.")
    print("  Ricci leakage proxy decreases as the Ricci stiffness K_RR increases.")


if __name__ == "__main__":
    main()
