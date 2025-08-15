"""
energy_demand_model.py

This module contains functions to translate demographic inputs into
energy demand metrics. It includes a function to project household
cooking energy demand from per-capita values, and precomputed lookup
tables for regional demand by year.
"""

from __future__ import annotations

try:
    from spatial_config import (
        regions,
        URBAN_DEMAND_GJ_PER_HH,
        RURAL_DEMAND_GJ_PER_HH,
        urban_hh_by_region_year,
        rural_hh_by_region_year,
    )
except Exception:  # pragma: no cover - fallback if data files are unavailable
    regions = []
    URBAN_DEMAND_GJ_PER_HH = 0.0
    RURAL_DEMAND_GJ_PER_HH = 0.0
    urban_hh_by_region_year = {}
    rural_hh_by_region_year = {}

from data_input import get_parameters
import pandas as pd
from numbers import Real


# -------------------------------------------------------
# Function: Total Cooking Energy Demand (GJ)
# -------------------------------------------------------


def project_energy_demand(total_pop: float, cooking_demand_per_capita: float) -> float:
    """Return total annual cooking energy demand.

    Energy demand is assumed to scale linearly with population. This
    function simply multiplies the total population by a per-capita
    energy demand (in gigajoules per person per year).

    Parameters
    ----------
    total_pop : float
        Total population in the year of interest.
    cooking_demand_per_capita : float
        Annual cooking energy demand per capita (GJ per person per year).

    Returns
    -------
    float
        Total annual cooking energy demand in gigajoules (GJ).
    """

    if not isinstance(total_pop, Real) or total_pop < 0:
        raise ValueError("total_pop must be a non-negative number")
    if not isinstance(cooking_demand_per_capita, Real) or cooking_demand_per_capita < 0:
        raise ValueError(
            "cooking_demand_per_capita must be a non-negative number"
        )
    return total_pop * cooking_demand_per_capita


def project_household_energy_demand(urban_hh: float, rural_hh: float) -> float:
    """Return total annual cooking energy demand given household counts.

    Multiplies the number of urban and rural households by their
    respective per‑household demand constants defined in
    :mod:`spatial_config`.

    Parameters
    ----------
    urban_hh : float
        Number of urban households in the year of interest.
    rural_hh : float
        Number of rural households in the year of interest.

    Returns
    -------
    float
        Total annual cooking energy demand in gigajoules (GJ).
    """

    if not isinstance(urban_hh, Real) or urban_hh < 0:
        raise ValueError("urban_hh must be a non-negative number")
    if not isinstance(rural_hh, Real) or rural_hh < 0:
        raise ValueError("rural_hh must be a non-negative number")
    return (
        urban_hh * URBAN_DEMAND_GJ_PER_HH + rural_hh * RURAL_DEMAND_GJ_PER_HH
    )


# -------------------------------------------------------
# Function: Disaggregate Annual Demand to Hourly Series
# -------------------------------------------------------


def disaggregate_to_hourly(
    annual_gj: float, cutout_path: str, variable: str, region_geom
) -> "pd.Series":
    """Disaggregate annual energy demand to an hourly series using ERA5 data.

    The ERA5 profile is averaged over the provided region and normalised to
    unit sum before weighting the annual total. If the profile sums to zero,
    a :class:`ValueError` is raised.

    Parameters
    ----------
    annual_gj : float
        Annual energy demand in gigajoules.
    cutout_path : str
        Path to an ERA5 cutout NetCDF file produced with :mod:`atlite`.
    variable : str
        Name of the variable inside the cutout, e.g. ``"t2m"`` for
        2 m temperature.
    region_geom : shapely geometry or GeoPandas object
        Geometry of the region for which the profile should be derived.

    Returns
    -------
    pandas.Series
        Hourly energy demand in gigajoules.
    """

    from era5_profiles import load_era5_series

    profile = load_era5_series(cutout_path, variable, region_geom)
    total = profile.sum()
    if total == 0:
        raise ValueError(
            "ERA5 profile sums to zero; cannot disaggregate to hourly series"
        )
    weights = profile / total
    return weights * annual_gj


# -------------------------------------------------------
# Parameters and Precomputed Demand Table
# -------------------------------------------------------


params = get_parameters()


def project_population(
    base_year: int,
    target_year: int,
    base_population: int,
    annual_growth_rate: float,
) -> float:
    """Compound population projection using exponential growth.

    Parameters
    ----------
    base_year : int
        The starting year for the projection.
    target_year : int
        The future year for which population should be estimated.
        Must be greater than or equal to ``base_year``.
    base_population : int
        Population in ``base_year``.
    annual_growth_rate : float
        Fractional annual population growth rate. Must be non‑negative.

    Returns
    -------
    float
        Projected population in ``target_year``. If ``target_year`` equals
        ``base_year``, the base population is returned (zero growth).

    Raises
    ------
    ValueError
        If ``target_year`` is before ``base_year`` or if
        ``annual_growth_rate`` is negative.
    """

    if target_year < base_year:
        raise ValueError("target_year must be greater than or equal to base_year")
    if annual_growth_rate < 0:
        raise ValueError("annual_growth_rate must be non-negative")

    years = target_year - base_year
    return base_population * ((1 + annual_growth_rate) ** years)


# Set base assumptions
base_year = 2025
base_population = params["population_total_2025"]
growth_rate = params["population_growth_rate_annual"]
per_capita_demand = params["cooking_energy_demand_per_capita_GJ_yr"]
hh_size_urban = params["household_size_urban"]
hh_size_rural = params["household_size_rural"]

# Define model years
years = [2030, 2040, 2050]

# Ensure regions are defined before computing populations
if not regions:
    raise ValueError("No regions provided; `regions` list is empty.")
n_regions = len(regions)

# Project total population for each model year
total_population_by_year = {
    yr: project_population(base_year, yr, base_population, growth_rate) for yr in years
}

# Derive regional populations from data when available; fall back to uniform split
population_by_year_and_region = {}
for yr in years:
    pops_for_year = {}
    for reg in regions:
        urban_hh = urban_hh_by_region_year.get(yr, {}).get(reg)
        rural_hh = rural_hh_by_region_year.get(yr, {}).get(reg)
        if urban_hh is not None and rural_hh is not None:
            pops_for_year[reg] = urban_hh * hh_size_urban + rural_hh * hh_size_rural
        else:
            pops_for_year[reg] = total_population_by_year[yr] / n_regions
    population_by_year_and_region[yr] = pops_for_year

# Total cooking energy demand by year and region (GJ)
total_cooking_demand_GJ_by_year_and_region = {
    yr: {
        reg: project_energy_demand(pop, per_capita_demand)
        for reg, pop in region_pops.items()
    }
    for yr, region_pops in population_by_year_and_region.items()
}

