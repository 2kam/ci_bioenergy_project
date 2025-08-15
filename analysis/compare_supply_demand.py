import argparse
import os
import sys
from pathlib import Path

import pandas as pd

# Ensure project root is on the Python path when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from spatial_config import compute_demand_by_region_year
from paths import get_data_path

TARGET_MULTIPLIERS = {2030: 0.58, 2040: 0.20, 2050: 0.05}
BASE_DEMAND_YEAR = 2023


def load_supply():
    """Load available biomass supply per district in GJ."""
    supply_df = pd.read_csv(
        get_data_path("regional_supply_full_corrected.csv")
    )
    supply = supply_df.groupby("District")["Available_GJ"].sum()
    supply.name = "supply_gj"
    return supply


def compute_scaled_demand(target_year: int) -> pd.Series:
    """Return scaled demand for ``target_year`` based on 2023 demand."""
    demand_by_year = compute_demand_by_region_year()
    base_year = BASE_DEMAND_YEAR
    if base_year not in demand_by_year:
        base_year = min(demand_by_year)
    base_demand = pd.Series(demand_by_year[base_year], name=f"demand_{base_year}")
    multiplier = TARGET_MULTIPLIERS.get(target_year)
    if multiplier is None:
        raise ValueError(f"Unsupported target year: {target_year}")
    scaled = base_demand * multiplier
    scaled.name = f"demand_{target_year}"
    return scaled


def compare_supply_demand(target_year: int) -> pd.DataFrame:
    supply = load_supply()
    demand = compute_scaled_demand(target_year)
    df = pd.concat([supply, demand], axis=1)
    df["surplus_deficit_gj"] = df["supply_gj"] - df[demand.name]
    return df


def main():
    parser = argparse.ArgumentParser(description="Compare biomass supply with scaled demand for a target year.")
    parser.add_argument("--target-year", type=int, choices=TARGET_MULTIPLIERS.keys(), default=2030,
                        help="Year for demand scaling (default: 2030)")
    args = parser.parse_args()

    df = compare_supply_demand(args.target_year)
    out_dir = "results"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"supply_demand_{args.target_year}.csv")
    df.to_csv(out_path)
    print(df.sort_values("surplus_deficit_gj", ascending=False).to_string())
    print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    main()
