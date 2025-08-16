"""Spatial configuration utilities.

This module now delegates demographic and demand calculations to the
``demand`` package but retains the helper for generating the
``results/buses.csv`` table used by PyPSA export utilities.
"""

from __future__ import annotations

import os
import pandas as pd

from demand import (
    regions,
    URBAN_DEMAND_GJ_PER_HH,
    RURAL_DEMAND_GJ_PER_HH,
    demand_by_region_year,
    urban_hh_by_region_year,
    rural_hh_by_region_year,
)


def generate_buses_csv(
    output_path: str = os.path.join("results", "buses.csv")
) -> pd.DataFrame:
    """Create a buses table with node metadata.

    The table contains one row per region and year with the number of
    urban and rural households. It is stored at ``results/buses.csv`` by
    default so that other modules (e.g. PyPSA export utilities) can join
    against it.

    Parameters
    ----------
    output_path : str, optional
        Location where the CSV should be written. Defaults to
        ``results/buses.csv``.

    Returns
    -------
    pandas.DataFrame
        Data frame containing the bus metadata.
    """

    rows = []
    for year, regions_dict in urban_hh_by_region_year.items():
        for region, urban_hh in regions_dict.items():
            rows.append(
                {
                    "region": region,
                    "year": year,
                    "urban_hh": urban_hh,
                    "rural_hh": rural_hh_by_region_year[year][region],
                }
            )
    buses_df = pd.DataFrame(rows).sort_values(["region", "year"])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    buses_df.to_csv(output_path, index=False)
    return buses_df


__all__ = [
    "regions",
    "URBAN_DEMAND_GJ_PER_HH",
    "RURAL_DEMAND_GJ_PER_HH",
    "demand_by_region_year",
    "urban_hh_by_region_year",
    "rural_hh_by_region_year",
    "generate_buses_csv",
]


if __name__ == "__main__":
    generate_buses_csv()

