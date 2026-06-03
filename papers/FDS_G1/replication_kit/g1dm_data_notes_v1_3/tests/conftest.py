"""Shared fixtures for g1dm_data_notes test suite."""
from __future__ import annotations

from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def desi_yaml_path(project_root: Path) -> Path:
    p = project_root / "data" / "compressed_constraints" / "desi_mg_2024_mu_sigma.yml"
    assert p.exists(), f"Missing: {p}"
    return p


@pytest.fixture(scope="session")
def sro_yaml_path(project_root: Path) -> Path:
    p = project_root / "data" / "templates" / "sro_observables_template.yml"
    assert p.exists(), f"Missing: {p}"
    return p
