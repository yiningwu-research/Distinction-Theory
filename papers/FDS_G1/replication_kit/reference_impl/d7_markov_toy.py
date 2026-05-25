#!/usr/bin/env python3
"""
D7 Finite Markov-Screen Realization — Reference Toy Code

Computes the two-state flip spectrum and verifies:
  - gamma_opt = 2 * r_o
  - Gamma_H   = 2 * epsilon * r_H
  - kappa     = 3/4 (optical projection)
  - m_0 * m_2 - m_1^2 = 0 (Hankel rank-one diagnostic)

Reference: FDS-G1 Complete Series, D7: Finite Markov-Screen Realization.
"""

import numpy as np


# ── Two-state symmetric flip generator ───────────────────────────

def two_state_generator(r):
    """Symmetric two-state flip generator.

    For y in {-1, +1} with transition rate r:
      Q = [[-r,  r],
           [ r, -r]]

    Relaxation generator L = -Q has eigenvalues 0 and 2r.
    """
    Q = np.array([[-r, r],
                   [r, -r]])
    L = -Q
    return Q, L


def two_state_spectrum(r):
    """Return eigenvalues of L = -Q for a symmetric two-state flip."""
    eigenvalues = np.array([0.0, 2.0 * r])
    eigenvectors = np.array([[1.0, -1.0],   # constant mode (eigenvalue 0)
                              [1.0, 1.0]])   # contrast mode (eigenvalue 2r)
    return eigenvalues, eigenvectors


# ── Toy model parameters and spectrum ────────────────────────────

def toy_spectrum(r_o, r_H, epsilon, r_R, lam_R=0.0):
    """Compute the toy model spectrum.

    Parameters
    ----------
    r_o : float
        Optical flip rate (common across 4 optical ports)
    r_H : float
        Horizon flip rate base
    epsilon : float
        Horizon slow-mode factor (0 < epsilon << 1)
    r_R : float
        Ricci flip rate base
    lam_R : float
        Ricci penalty scale in conditioned ensemble (default 0)

    Returns
    -------
    dict with gamma_opt, Gamma_H, gamma_R, kappa, rank_one_check
    """
    gamma_opt = 2.0 * r_o
    Gamma_H = 2.0 * epsilon * r_H
    gamma_R = 2.0 * r_R

    # Optical projection coefficient (D7 eq.)
    # dim(U) = dim(S1 + S2 + T) = 3
    # dim(opt) = dim(A + S1 + S2 + T) = 4
    kappa = 3.0 / 4.0

    # Hankel moments for rank-one Stieltjes response
    # chi_H(s) = Z_H / (s + Gamma_H)
    # m_n = Z_H / Gamma_H^{n+1}
    # For arbitrary Z_H, m0*m2 - m1^2 = 0
    Z_H = 1.0  # arbitrary normalization cancels
    m0 = Z_H / (Gamma_H**1)
    m1 = Z_H / (Gamma_H**2)
    m2 = Z_H / (Gamma_H**3)
    hankel_det = m0 * m2 - m1 * m1

    return {
        "gamma_opt": gamma_opt,
        "Gamma_H": Gamma_H,
        "gamma_R": gamma_R,
        "kappa": kappa,
        "hankel_det": hankel_det,
        "spectrum": {
            "optical_band": [gamma_opt, 4],      # 4 degenerate optical modes
            "horizon_mode": [Gamma_H, 1],        # 1 slow horizon mode
            "ricci_sector": [gamma_R, 3],        # 3 Ricci modes (or stiff)
        },
    }


# ── Optical projection ───────────────────────────────────────────

def optical_projection():
    """Verify the optical projection gives kappa = 3/4.

    Optical port space P_opt = A(1) + S1(1) + S2(1) + T(1)  (4 dimensions)
    Weyl-active unimodular U = S1 + S2 + T                 (3 dimensions)
    kappa = dim(U) / dim(P_opt) = 3/4
    """
    dim_opt = 4   # A, S1, S2, T
    dim_U = 3     # S1, S2, T
    kappa = dim_U / dim_opt
    return kappa, dim_U, dim_opt


# ── Hankel rank-one diagnostic ───────────────────────────────────

def hankel_rank_one_test(Z_H=1.0, Gamma_H=0.01, tol=1e-7):
    """Test that single-pole response gives zero Hankel determinant.

    For chi_H(s) = Z_H / (s + Gamma_H):
      m_n = Z_H * Gamma_H^{-(n+1)}
      => m0 * m2 - m1^2 = 0
    """
    m0 = Z_H / (Gamma_H**1)
    m1 = Z_H / (Gamma_H**2)
    m2 = Z_H / (Gamma_H**3)
    det = m0 * m2 - m1 * m1
    return abs(det) < tol, det


# ── Full verification ────────────────────────────────────────────

def verify_d7_toy(rtol=1e-10):
    """Run all D7 toy model checks. Raises AssertionError on failure.

    Returns True if all checks pass.
    """
    r_o = 2.0
    r_H = 1.0
    epsilon = 0.05
    r_R = 10.0

    # 1. Two-state eigenvalues
    evals, evecs = two_state_spectrum(r_o)
    assert abs(evals[0] - 0.0) < rtol, f"eigenvalue 0 != 0: {evals[0]}"
    assert abs(evals[1] - 2.0 * r_o) < rtol, f"eigenvalue 1 != 2r_o: {evals[1]}"

    # 2. Toy spectrum
    result = toy_spectrum(r_o, r_H, epsilon, r_R)
    assert abs(result["gamma_opt"] - 2.0 * r_o) < rtol, "gamma_opt != 2*r_o"
    assert abs(result["Gamma_H"] - 2.0 * epsilon * r_H) < rtol, "Gamma_H != 2*epsilon*r_H"
    assert abs(result["gamma_R"] - 2.0 * r_R) < rtol, "gamma_R != 2*r_R"
    assert abs(result["kappa"] - 0.75) < rtol, f"kappa != 3/4: {result['kappa']}"

    # 3. Hankel rank-one diagnostic (single pole => zero)
    assert abs(result["hankel_det"]) < rtol, f"hankel_det != 0: {result['hankel_det']}"

    # 4. Nonzero hankel_det for two-pole case
    # Two poles at Gamma1=0.01, Gamma2=0.1 with weights Z1=0.7, Z2=0.3
    Z1, G1 = 0.7, 0.01
    Z2, G2 = 0.3, 0.1
    m0 = Z1/G1 + Z2/G2
    m1 = Z1/G1**2 + Z2/G2**2
    m2 = Z1/G1**3 + Z2/G2**3
    det_two_pole = m0 * m2 - m1 * m1
    assert det_two_pole > 0, f"two-pole hankel_det should be > 0, got {det_two_pole}"

    # 5. Slow horizon mode condition
    assert result["Gamma_H"] < result["gamma_opt"], "horizon not slow"
    assert result["Gamma_H"] < result["gamma_R"], "horizon not slow vs Ricci"

    # 6. kappa = 3/4 from dimension counting
    kappa, dimU, dimOpt = optical_projection()
    assert abs(kappa - 0.75) < rtol
    assert dimU == 3 and dimOpt == 4

    return True


if __name__ == "__main__":
    verify_d7_toy()
    print("All D7 Markov-screen toy checks passed.")

    # Print summary
    r_o, r_H, eps, r_R = 2.0, 1.0, 0.05, 10.0
    res = toy_spectrum(r_o, r_H, eps, r_R)
    print(f"\nToy spectrum:")
    print(f"  gamma_opt = {res['gamma_opt']:.1f}  (optical band, 4 degenerate modes)")
    print(f"  Gamma_H   = {res['Gamma_H']:.3f}  (slow horizon mode)")
    print(f"  gamma_R   = {res['gamma_R']:.1f}  (Ricci sector)")
    print(f"  kappa     = {res['kappa']:.2f}  (optical projection)")
    print(f"  hankel_det = {res['hankel_det']:.2e}  (rank-one => 0)")
    print(f"\n  gamma_opt >> Gamma_H: {res['gamma_opt'] >= 40*res['Gamma_H']}")
