import numpy as np

from cmb_lensing_precheck.background import Background
from cmb_lensing_precheck.growth import solve_growth


def test_background_normalized_today():
    bg_l = Background(67.4, 0.3, 9e-5, 3.0, "lcdm")
    bg_g = Background(67.4, 0.3, 9e-5, 2.5, "g1de")
    assert np.isclose(bg_l.e_a(1.0), 1.0)
    assert np.isclose(bg_g.e_a(1.0), 1.0)


def test_s3_matches_lcdm_background():
    a = np.geomspace(1e-3, 1.0, 30)
    bg_l = Background(67.4, 0.3, 9e-5, 3.0, "lcdm")
    bg_g = Background(67.4, 0.3, 9e-5, 3.0, "g1de")
    assert np.allclose(bg_l.e_a(a), bg_g.e_a(a), rtol=1e-12)


def test_growth_is_positive_and_monotone():
    bg = Background(67.4, 0.3, 9e-5, 3.0, "lcdm")
    sol = solve_growth(bg, 9e-4, n_a=500)
    assert np.all(sol.delta_grid > 0)
    assert np.all(np.diff(sol.delta_grid) > 0)
