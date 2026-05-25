# R̂_H(a) Normalization Rules
# FDS-G1 Complete Series normalization conventions

## 1. Response-shape definition

The normalized horizon-response output shape is:

  X_b(a) = R̂_H(a) = R̂_H(a)
  R̂_H(1) = 1

In production code, the function Xhat_a(a, Omega_m, s) is:

  chiH(a) = 1 / (1 + B * a^{-s})
    where B = 1/(1 - Omega_m) - 1

  Xhat(a) = 4 * chiH(a) * (1 - chiH(a))

This is a normalized shape function that peaks at intermediate a
and goes to 0 at a=0 and a=1.

## 2. Horizon response R_H(a)

  R_H(a) = R_0 * R̂_H(a)
  R_0 = R_H(1) = 3 - s

## 3. Weyl response

  Sigma(a, k) - 1 = -kappa * R_H(a)
  For M_{3/4}: kappa = 3/4, so Sigma(a,k) - 1 = -3/4 * (3-s) * R̂_H(a)

## 4. Growth response

  mu(a, k) = 1 + mu0 * Xhat(a)
  For M_{3/4}: mu0 = 0, so mu(a,k) = 1

## 5. Critical distinction

R̂_H(a) is the normalized output-response shape, NOT a uniquely identified
microscopic source-kernel factorization. The production code samples R_H(a)
as an output normal form; it does not uniquely determine K_H * J_H.

## 6. No free A(a,k) rule

No model in the G1DE evidence hierarchy includes a free A(a,k) amplitude
parameter. If independent A(a,k) is required by the data, the model leaves
the G1DE class and becomes a generic dark-stress model.
