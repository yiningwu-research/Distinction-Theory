# D7 Finite Markov-Screen Toy Model

This is a minimal reference implementation for the toy construction in

**D7: Finite Markov-Screen Realization of the G1DE-M_{3/4} Normal Form**

It is an existence / sanity-check prototype, not a proposal for unique spacetime microphysics.

## What it verifies

The script checks the minimal detailed-balance Markov-screen toy:

- Optical four-port symmetry:
  \[
  A,\ S_1,\ S_2,\ T
  \]
  gives
  \[
  \kappa_{BW}=3/4.
  \]

- A symmetric two-state flip process with rate \(r\) has positive relaxation eigenvalue:
  \[
  \gamma=2r.
  \]

- The slow horizon flip mode has
  \[
  \Gamma_H=2\epsilon r_H.
  \]

- A rank-one Stieltjes response
  \[
  \chi_H(s)=\frac{Z_H}{s+\Gamma_H}
  \]
  has moments
  \[
  m_n=\frac{Z_H}{\Gamma_H^{n+1}},
  \]
  and satisfies the rank-one Hankel diagnostic:
  \[
  m_0m_2-m_1^2=0.
  \]

- Ricci leakage is suppressed by increasing stiffness in the toy model.

## Install

Requires Python 3.9+ and NumPy.

```bash
pip install numpy
```

## Run

```bash
python d7_markov_screen_toy.py
```

Optional parameters:

```bash
python d7_markov_screen_toy.py --r-opt 1.0 --r-h 1.0 --epsilon 0.02 --r-ricci 8.0 --z-h 1.0
```

## Run tests

```bash
python test_d7_markov_screen_toy.py
```

## Expected output

You should see:

- `kappa = 0.75`
- `gamma_opt = 2*r_opt`
- `Gamma_H = 2*epsilon*r_H`
- `rank_one_hankel = approximately 0`
- all tests passed
