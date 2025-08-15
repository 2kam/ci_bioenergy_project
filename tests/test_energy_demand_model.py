import importlib
import pathlib
import sys
import types

import pandas as pd
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))


def _import_edm(monkeypatch, series):
    spatial = types.ModuleType("spatial_config")
    spatial.regions = ["dummy"]
    spatial.URBAN_DEMAND_GJ_PER_HH = 0
    spatial.RURAL_DEMAND_GJ_PER_HH = 0
    spatial.urban_hh_by_region_year = {}
    spatial.rural_hh_by_region_year = {}
    monkeypatch.setitem(sys.modules, "spatial_config", spatial)

    era5 = types.ModuleType("era5_profiles")
    era5.load_era5_series = lambda *a, **k: series
    monkeypatch.setitem(sys.modules, "era5_profiles", era5)

    monkeypatch.delitem(sys.modules, "energy_demand_model", raising=False)
    return importlib.import_module("energy_demand_model")


def test_disaggregate_to_hourly_zero_profile(monkeypatch):
    series = pd.Series([0, 0, 0], index=pd.date_range("2020-01-01", periods=3, freq="h"))
    edm = _import_edm(monkeypatch, series)

    with pytest.raises(ValueError):
        edm.disaggregate_to_hourly(10, "dummy", "t2m", None)


def test_disaggregate_to_hourly_nonzero_profile(monkeypatch):
    series = pd.Series([1, 2, 3], index=pd.date_range("2020-01-01", periods=3, freq="h"))
    edm = _import_edm(monkeypatch, series)

    result = edm.disaggregate_to_hourly(6, "dummy", "t2m", None)
    expected = pd.Series([1.0, 2.0, 3.0], index=series.index)
    pd.testing.assert_series_equal(result, expected)


def test_empty_regions_raises_value_error(monkeypatch):
    spatial = types.ModuleType("spatial_config")
    spatial.regions = []
    spatial.URBAN_DEMAND_GJ_PER_HH = 0
    spatial.RURAL_DEMAND_GJ_PER_HH = 0
    spatial.urban_hh_by_region_year = {}
    spatial.rural_hh_by_region_year = {}

    sys.modules.pop("energy_demand_model", None)
    sys.modules.pop("spatial_config", None)
    monkeypatch.setitem(sys.modules, "spatial_config", spatial)

    with pytest.raises(ValueError):
        importlib.import_module("energy_demand_model")

