"""Demographic data loading and cooking demand calculations.

This module centralises access to household projections and derived
regional demand figures.  It was previously part of
``spatial_config.py`` but now lives in the :mod:`demand` package to
provide a clearer API for other components.
"""

from __future__ import annotations

from functools import lru_cache
import pandas as pd

from paths import get_data_path


# Assumed cooking energy demand per household in GJ/year (source: IEA
# country brief for Côte d'Ivoire, 2024)
URBAN_DEMAND_GJ_PER_HH = 6.5  # IEA (2024), page 5
RURAL_DEMAND_GJ_PER_HH = 5.5  # IEA (2024), page 5


@lru_cache()
def load_demographics() -> pd.DataFrame:
    """Load district-level household projections.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by ``District`` and ``Year`` with columns for
        ``Urban_Households`` and ``Rural_Households``.
    """

    path = get_data_path("District-level_Household_Projections.csv")
    try:
        df = pd.read_csv(path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Demographic projection file not found: {path}"
        ) from exc
    df.columns = df.columns.str.strip()
    df.set_index(["District", "Year"], inplace=True)
    return df


# Load once for module-level calculations but keep loader for reuse
demographics = load_demographics()


# Extract regions (districts)
regions = sorted(demographics.index.get_level_values("District").unique())


def compute_demand_by_region_year(df: pd.DataFrame | None = None):
    """Return total household cooking demand for each region and year.

    Parameters
    ----------
    df : pandas.DataFrame, optional
        Alternative demographic data frame.  Must contain the columns
        ``Urban_Households`` and ``Rural_Households`` and be indexed by
        ``District`` and ``Year``.  If omitted, the preloaded
        :data:`demographics` table is used.

    Returns
    -------
    dict
        Nested mapping ``{year: {district: demand_GJ}}``.
    """

    df = df if df is not None else demographics
    required_cols = {"Urban_Households", "Rural_Households"}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    demand: dict[int, dict[str, float]] = {}
    for (district, year), row in df.iterrows():
        if year not in demand:
            demand[year] = {}
        urban_demand = row["Urban_Households"] * URBAN_DEMAND_GJ_PER_HH
        rural_demand = row["Rural_Households"] * RURAL_DEMAND_GJ_PER_HH
        total_demand = urban_demand + rural_demand
        demand[year][district] = total_demand
    return demand


def compute_urban_rural_hh_by_region_year(df: pd.DataFrame | None = None):
    """Return household counts split by urban/rural for each region/year."""

    df = df if df is not None else demographics
    urban: dict[int, dict[str, float]] = {}
    rural: dict[int, dict[str, float]] = {}
    for (district, year), row in df.iterrows():
        if year not in urban:
            urban[year] = {}
            rural[year] = {}
        urban[year][district] = row["Urban_Households"]
        rural[year][district] = row["Rural_Households"]
    return urban, rural


# Precompute values for use in optimisation and adoption models
demand_by_region_year = compute_demand_by_region_year()
urban_hh_by_region_year, rural_hh_by_region_year = compute_urban_rural_hh_by_region_year()


__all__ = [
    "URBAN_DEMAND_GJ_PER_HH",
    "RURAL_DEMAND_GJ_PER_HH",
    "load_demographics",
    "demographics",
    "regions",
    "compute_demand_by_region_year",
    "compute_urban_rural_hh_by_region_year",
    "demand_by_region_year",
    "urban_hh_by_region_year",
    "rural_hh_by_region_year",
]

