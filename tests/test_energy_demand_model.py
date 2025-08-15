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
