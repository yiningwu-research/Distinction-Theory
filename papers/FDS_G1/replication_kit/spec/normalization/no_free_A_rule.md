# No-Free-A Guard Rule
# FDS-G1 Complete Series

## Rule

No model in the G1DE evidence hierarchy samples a free A(a,k) amplitude:

  A(a, k) NOT IN Theta_{G1DE}

## What A(a,k) would mean

A free A(a,k) would independently rescale the Weyl-port normalization,
breaking the projection-locked relationship between background and Weyl
response. This would reduce G1DE to a generic dark-stress parameterization.

## Verification in code

Any production likelihood code MUST assert:

  assert "A" not in parameter_names
  assert "amplitude" not in parameter_names

or equivalently, the parameter list must NOT contain a free-amplitude entry.

## Demotion

If data require A(a,k) != 1 (or equivalently, a free normalization parameter),
the G1DE observational branch is demoted to generic dark-stress status.
This is one of the six explicit failure/demotion paths.
