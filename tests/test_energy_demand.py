import importlib
import sys
from pathlib import Path
import types

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))


def _prepare_modules(monkeypatch):
    """Patch data loading and import target modules."""
    data_file = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "District-level_Household_Projections.csv"
    )
    real_read_csv = pd.read_csv

    def mock_read_csv(path, *args, **kwargs):
        if str(path).endswith("District-level_Household_Projections.csv"):
            return real_read_csv(data_file, *args, **kwargs)
        return real_read_csv(path, *args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", mock_read_csv)

    era5_stub = types.ModuleType("era5_profiles")
    era5_stub.load_era5_series = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "era5_profiles", era5_stub)

    monkeypatch.delitem(sys.modules, "demand", raising=False)
    monkeypatch.delitem(sys.modules, "demand.demographics", raising=False)
    monkeypatch.delitem(sys.modules, "energy_demand_model", raising=False)

    demand_module = importlib.import_module("demand")
    energy_demand_model = importlib.import_module("energy_demand_model")
    return demand_module, energy_demand_model


def test_cooking_demand_increases(monkeypatch):
    demand_module, energy_demand_model = _prepare_modules(monkeypatch)

    base_year = 2030
    later_years = [2040, 2050]

    demands = energy_demand_model.total_cooking_demand_GJ_by_year_and_region
    demand_by_year = demand_module.demand_by_region_year

    for region in demand_module.regions:
        base_total = demands[base_year][region]
        base_regional = demand_by_year[base_year][region]
        for year in later_years:
            assert demands[year][region] > base_total
            assert demand_by_year[year][region] > base_regional
