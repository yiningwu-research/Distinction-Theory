# NORMALIZATION_RULES.md
# FDS-G1 Complete Series v1.0-rc

Detailed rules in: spec/normalization/RbH_definition.md, spec/normalization/no_free_A_rule.md

## R̂_H(a) normalization

  X_b(a) ≡ R̂_H(a) is the normalized horizon-response output shape.
  R̂_H(1) = 1  (normalized at present)

  Production code implementation:
    chiH(a) = 1 / (1 + B * a^{-s})   where B = 1/(1-Om) - 1
    Xhat(a)  = 4 * chiH(a) * (1 - chiH(a))

    Note: Xhat(1) = 4*Om*(1-Om) ≈ 0.84 for Om≈0.3.
    The production code uses Xhat(a) directly and absorbs the
    normalization constant into the amplitude parameters (Sigma0, mu0).
    The prose convention R̂_H(1)=1 is equivalent to defining
    R̂_H(a) = Xhat(a) / Xhat(1) and absorbing Xhat(1) into Sigma0.

## Horizon response

  R_H(a) = R_0 * R̂_H(a)
  R_0 = R_H(1) = 3 - s

## Weyl response

  Sigma(a) - 1 = -kappa * R_H(a)

  For M_{3/4}: kappa = 3/4

## Growth response

  mu(a) = 1 + mu0 * Xhat(a)

  For M_{3/4}: mu0 = 0 (Ward-stiff Ricci leakage)

## No free A(a,k)

  No model includes a free amplitude parameter A(a,k).
  If data require A(a,k) != 1, the G1DE branch is demoted.
