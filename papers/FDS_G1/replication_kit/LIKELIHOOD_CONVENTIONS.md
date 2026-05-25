# LIKELIHOOD_CONVENTIONS.md
# FDS-G1 Complete Series v1.0-rc

Machine-readable: spec/likelihood_conventions/*.yaml

## Overview

The joint likelihood combines four independent data blocks:

  chi2_total = chi2_SN + chi2_BAO + chi2_growth + chi2_EG

Each block is a Gaussian chi2 with full covariance (except E_G which uses
diagonal errors).

## SN: Pantheon+ full covariance

  chi2_SN = min_M (mu_obs - mu_pred(z) - M)^T C_{SN}^{-1} (mu_obs - mu_pred(z) - M)
          = A - B^2 / C

  with analytic marginalization over the absolute magnitude offset M.

## BAO: DESI DR2

  chi2_BAO = (obs - pred)^T C_{BAO}^{-1} (obs - pred)

  Observables: DM/rd, DH/rd, DV/rd
  q_BAO = rd * H0 / c absorbs the sound horizon and H0 into one parameter.

## Growth: curated RSD fsigma8

  chi2_growth = (fsigma8_obs - fsigma8_pred)^T C_{growth}^{-1} (fsigma8_obs - fsigma8_pred)

  fsigma8_pred = f(z) * sigma8(z) via numerical solution of growth equation.

## E_G: compressed lensing

  chi2_EG = sum_i (E_G_obs_i - E_G_pred_i)^2 / sigma_i^2

  E_G_pred = Omega_m * Sigma(z) / f(z)

## Normalization

  R̂_H(1) = 1 (normalized output shape)
  mu0 = 0 for all projection-locked models
  No free A(a,k) amplitude in any model

See spec/normalization/ for detailed rules.
