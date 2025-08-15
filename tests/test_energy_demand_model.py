import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from energy_demand_model import (
    project_energy_demand,
    project_household_energy_demand,
    URBAN_DEMAND_GJ_PER_HH,
    RURAL_DEMAND_GJ_PER_HH,
)


def test_project_energy_demand_valid():
    assert project_energy_demand(100, 0.5) == 50


def test_project_energy_demand_negative_total_pop():
    with pytest.raises(ValueError):
        project_energy_demand(-1, 0.5)


def test_project_energy_demand_negative_cooking():
    with pytest.raises(ValueError):
        project_energy_demand(100, -0.5)


def test_project_household_energy_demand_valid():
    expected = 10 * URBAN_DEMAND_GJ_PER_HH + 5 * RURAL_DEMAND_GJ_PER_HH
    assert project_household_energy_demand(10, 5) == expected


def test_project_household_energy_demand_negative_urban():
    with pytest.raises(ValueError):
        project_household_energy_demand(-1, 5)


def test_project_household_energy_demand_negative_rural():
    with pytest.raises(ValueError):
        project_household_energy_demand(10, -5)

