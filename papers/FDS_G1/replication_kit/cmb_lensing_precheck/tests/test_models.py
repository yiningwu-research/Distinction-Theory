import numpy as np

from cmb_lensing_precheck.models import chi_h, response_shape, sigma_response


def test_present_normalization_is_one_today():
    value = response_shape(1.0, 0.3, 9e-5, 2.5, "present")
    assert np.isclose(value, 1.0)


def test_code_normalization_matches_replication_formula():
    a = np.array([0.2, 0.5, 1.0])
    chi = chi_h(a, 0.3, 9e-5, 2.5)
    assert np.allclose(response_shape(a, 0.3, 9e-5, 2.5, "code"), 4 * chi * (1 - chi))


def test_m34_lock():
    a = np.array([0.3, 0.7, 1.0])
    H = np.full_like(a, 70.0)
    k = np.full_like(a, 0.1)
    got = sigma_response(a, k, H, 0.3, 9e-5, "g1de_m34", 2.5, 0.2, "code")
    shape = response_shape(a, 0.3, 9e-5, 2.5, "code")
    assert np.allclose(got, 1 - 0.75 * 0.5 * shape)
