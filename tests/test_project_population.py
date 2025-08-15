import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from energy_demand_model import project_population


def test_project_population_valid():
    result = project_population(2020, 2025, 1000, 0.02)
    assert result == pytest.approx(1000 * (1 + 0.02) ** 5)


def test_project_population_equal_years():
    assert project_population(2020, 2020, 1000, 0.05) == 1000


def test_project_population_invalid_year():
    with pytest.raises(ValueError):
        project_population(2025, 2020, 1000, 0.02)


def test_project_population_negative_growth():
    with pytest.raises(ValueError):
        project_population(2020, 2025, 1000, -0.01)
