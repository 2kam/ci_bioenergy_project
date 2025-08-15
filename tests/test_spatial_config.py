import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
import importlib


@pytest.fixture
def spatial_config_module(monkeypatch):
    df = pd.DataFrame(
        {
            "District": ["A"],
            "Year": [2020],
            "Urban_Households": [1],
            "Rural_Households": [2],
        }
    )
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: df.copy())
    if "spatial_config" in sys.modules:
        del sys.modules["spatial_config"]
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    module = importlib.import_module("spatial_config")
    return module


@pytest.mark.parametrize("missing_col", ["Urban_Households", "Rural_Households"])
def test_compute_demand_by_region_year_missing_columns(spatial_config_module, monkeypatch, missing_col):
    df = pd.DataFrame(
        {
            "District": ["A"],
            "Year": [2020],
            "Urban_Households": [1],
            "Rural_Households": [2],
        }
    ).drop(columns=[missing_col])
    df.set_index(["District", "Year"], inplace=True)
    monkeypatch.setattr(spatial_config_module, "demographics", df)
    with pytest.raises(KeyError, match=missing_col):
        spatial_config_module.compute_demand_by_region_year()


def test_generate_buses_csv_only_when_run_as_script(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    csv_path = data_dir / "District-level_Household_Projections.csv"
    df = pd.DataFrame(
        {
            "District": ["A"],
            "Year": [2020],
            "Urban_Households": [1],
            "Rural_Households": [1],
        }
    )
    df.to_csv(csv_path, index=False)

    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root)

    results_file = tmp_path / "results" / "buses.csv"

    subprocess.run(
        [sys.executable, "-c", "import spatial_config"],
        cwd=tmp_path,
        env=env,
        check=True,
    )
    assert not results_file.exists()

    subprocess.run(
        [sys.executable, "-m", "spatial_config"],
        cwd=tmp_path,
        env=env,
        check=True,
    )
    assert results_file.exists()
