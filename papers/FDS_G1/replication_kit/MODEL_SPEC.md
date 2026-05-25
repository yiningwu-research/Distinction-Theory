# Model Specification
# FDS-G1 Complete Series v1.0-rc

This document defines the six models in the G1fit-real evidence hierarchy.
The YAML model cards in spec/model_cards/ are the machine-readable authority;
this document provides the prose specification with equations.

Authoritative specification files:
  spec/model_cards/lcdm.yaml
  spec/model_cards/cpl.yaml
  spec/model_cards/g1de_m34.yaml
  spec/model_cards/g1de_mkappa.yaml
  spec/model_cards/g1de_const_sigma.yaml
  spec/model_cards/g1de2.yaml

## 1. Common background

All models assume a flat FLRW metric with Hubble rate H(z) = H0 * E(z).

### 1.1 LCDM

  E(z)^2 = Omega_m * (1+z)^3 + (1 - Omega_m)

### 1.2 CPL

  E(z)^2 = Omega_m * (1+z)^3 + (1-Om) * (1+z)^{3(1+w0+wa)} * e^{-3*wa*z/(1+z)}

### 1.3 G1DE background (all G1 models)

Define the background deviation fraction:

  chiH(a) = 1 / (1 + B * a^{-s})

  where  B = 1/(1-Om) - 1,  s = screen-index parameter

Then:

  E(z)^2 = Omega_m * (1+z)^3 / (1 - chiH(a))
         = Omega_m * (1+z)^3 + (1-Om) * (1+z)^(3-s)

  The second form shows G1DE reduces to w_0 = -1, w_a = -s/3 in CPL
  notation at linear level.

## 2. Response functions

### 2.1 Normalized output shape

  Xhat(a) = 4 * chiH(a) * (1 - chiH(a))

  This is the normalized horizon-response output shape R̂_H(a).
  Xhat(1) = 1.  Xhat(0) = 0.  It peaks at intermediate a.

  **Critical**: Xhat(a) is the output normal form, NOT a uniquely
  identified microscopic source-kernel factorization.

### 2.2 Growth response mu(a)

  mu(a) = 1 + mu0 * Xhat(a)

  mu0 = 0 for all projection-locked and control models (mu=1).
  mu0 is free only in G1DE-2.

### 2.3 Weyl response Sigma(a)

  Sigma(a) = 1 + Sigma0 * Xhat(a)

  Sigma0 is model-dependent:
    M_{3/4}:         Sigma0 = -3/4 * (3 - s)
    M_kappa:          Sigma0 = -kappa * (3 - s)
    const-Sigma:     Sigma(a) = 1 + Sigma_c  (no redshift evolution)
    G1DE-2:          Sigma0 is free

## 3. Model definitions

### M_{3/4} (g1dem34) — evidence-selected

  params:  Omega_m, s, q_BAO, sigma8_0
  mu(a) = 1
  Sigma(a) - 1 = -3/4 * (3-s) * Xhat(a)

### M_kappa (g1demk) — free-kappa control

  params:  Omega_m, s, q_BAO, sigma8_0, kappa
  mu(a) = 1
  Sigma(a) - 1 = -kappa * (3-s) * Xhat(a)

### const-Sigma (g1deconstsig) — constant Weyl offset

  params:  Omega_m, s, q_BAO, sigma8_0, Sigma_c
  mu(a) = 1
  Sigma(a) = 1 + Sigma_c

### G1DE-2 (g1de2) — free-response envelope

  params:  Omega_m, s, q_BAO, sigma8_0, mu0, Sigma0
  mu(a) = 1 + mu0 * Xhat(a)
  Sigma(a) = 1 + Sigma0 * Xhat(a)

### CPL (cpl) — phenomenological control

  params:  Omega_m, w0, wa, q_BAO, sigma8_0
  mu(a) = 1
  Sigma(a) = 1

### LCDM (lcdm) — baseline

  params:  Omega_m, q_BAO, sigma8_0
  mu(a) = 1
  Sigma(a) = 1

## 4. Growth equation

For all models:

  d^2 delta / dN^2 + (2 + d ln E / d ln a) * d delta / dN
    - 1.5 * Om(a) * mu(a) * delta = 0

  where N = ln(a),  Om(a) = Omega_m * a^{-3} / E(a)^2

  Initial condition: delta ~ a at a = 1e-3.
  Normalized: D(a) = delta(a) / delta(1).

  fsigma8(z) = f(z) * sigma8_0 * D(z)
    where f(z) = d ln D / d ln a

  E_G(z) = Omega_m * Sigma(z) / f(z)

## 5. No free A(a,k) rule

No model in the G1DE evidence hierarchy includes a free A(a,k) amplitude
parameter. This is enforced at the code level: if an independent amplitude
is required, the model leaves the G1DE class.

## 6. Parameter tables

See spec/model_cards/*.yaml for numeric bounds, starting values, and
best-fit parameters.
