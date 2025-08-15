import importlib
import os
import sys
import types

import pytest


def test_empty_regions_raises_value_error(monkeypatch):
    """Ensure a clear error is raised when the regions list is empty."""

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    dummy_pd = types.ModuleType("pandas")
    monkeypatch.setitem(sys.modules, "pandas", dummy_pd)

    dummy_era5 = types.ModuleType("era5_profiles")
    dummy_era5.load_era5_series = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "era5_profiles", dummy_era5)

    dummy_spatial = types.ModuleType("spatial_config")
    dummy_spatial.regions = []
    dummy_spatial.URBAN_DEMAND_GJ_PER_HH = 0
    dummy_spatial.RURAL_DEMAND_GJ_PER_HH = 0
    dummy_spatial.urban_hh_by_region_year = {}
    dummy_spatial.rural_hh_by_region_year = {}
    monkeypatch.setitem(sys.modules, "spatial_config", dummy_spatial)

    with pytest.raises(ValueError, match="regions.*empty"):
        importlib.import_module("energy_demand_model")


import pandas as pd
import pytest
import sys
import types
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

# Provide stub modules required by energy_demand_model on import
spatial_config = types.ModuleType("spatial_config")
spatial_config.regions = []
spatial_config.URBAN_DEMAND_GJ_PER_HH = 0
spatial_config.RURAL_DEMAND_GJ_PER_HH = 0
sys.modules["spatial_config"] = spatial_config

data_input = types.ModuleType("data_input")
data_input.get_parameters = lambda: {
    "population_total_2025": 0,
    "population_growth_rate_annual": 0,
    "cooking_energy_demand_per_capita_GJ_yr": 0,
}
sys.modules["data_input"] = data_input

era5_profiles = types.ModuleType("era5_profiles")
era5_profiles.load_era5_series = lambda *args, **kwargs: None
sys.modules["era5_profiles"] = era5_profiles

import energy_demand_model as edm


def test_disaggregate_to_hourly_zero_profile(monkeypatch):
    series = pd.Series([0, 0, 0], index=pd.date_range("2020-01-01", periods=3, freq="h"))
    monkeypatch.setattr(edm, "load_era5_series", lambda *args, **kwargs: series)
    with pytest.raises(ValueError, match="profile sums to zero"):
        edm.disaggregate_to_hourly(10, "dummy", "t2m", None)


def test_disaggregate_to_hourly_nonzero_profile(monkeypatch):
    series = pd.Series([1, 2, 3], index=pd.date_range("2020-01-01", periods=3, freq="h"))
    monkeypatch.setattr(edm, "load_era5_series", lambda *args, **kwargs: series)
    result = edm.disaggregate_to_hourly(6, "dummy", "t2m", None)
    expected = pd.Series([1.0, 2.0, 3.0], index=series.index)
    pd.testing.assert_series_equal(result, expected)

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

