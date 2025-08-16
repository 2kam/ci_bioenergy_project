import os
import subprocess
import sys
from pathlib import Path

import pandas as pd


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

