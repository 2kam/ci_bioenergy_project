import importlib
import sys
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def demographics_module(monkeypatch):
    df = pd.DataFrame(
        {
            "District": ["A"],
            "Year": [2020],
            "Urban_Households": [1],
            "Rural_Households": [2],
        }
    )
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: df.copy())
    if "demand.demographics" in sys.modules:
        del sys.modules["demand.demographics"]
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    module = importlib.import_module("demand.demographics")
    return module


@pytest.mark.parametrize("missing_col", ["Urban_Households", "Rural_Households"])
def test_compute_demand_by_region_year_missing_columns(demographics_module, monkeypatch, missing_col):
    df = pd.DataFrame(
        {
            "District": ["A"],
            "Year": [2020],
            "Urban_Households": [1],
            "Rural_Households": [2],
        }
    ).drop(columns=[missing_col])
    df.set_index(["District", "Year"], inplace=True)
    monkeypatch.setattr(demographics_module, "demographics", df)
    with pytest.raises(KeyError, match=missing_col):
        demographics_module.compute_demand_by_region_year()

