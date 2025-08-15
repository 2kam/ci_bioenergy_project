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

