"""Energy demand calculations for the CI bioenergy project."""

from __future__ import annotations

from numbers import Real

try:
    from spatial_config import (
        regions,
        URBAN_DEMAND_GJ_PER_HH,
        RURAL_DEMAND_GJ_PER_HH,
        urban_hh_by_region_year,
        rural_hh_by_region_year,
    )
except Exception:  # pragma: no cover - allow import in minimal environments
    regions = []
    URBAN_DEMAND_GJ_PER_HH = 0.0
    RURAL_DEMAND_GJ_PER_HH = 0.0
    urban_hh_by_region_year = {}
    rural_hh_by_region_year = {}

from data_input import get_parameters


def project_energy_demand(total_pop: float, cooking_demand_per_capita: float) -> float:
    """Return total annual cooking energy demand."""

    if not isinstance(total_pop, Real) or total_pop < 0:
        raise ValueError("total_pop must be a non-negative number")
    if not isinstance(cooking_demand_per_capita, Real) or cooking_demand_per_capita < 0:
        raise ValueError(
            "cooking_demand_per_capita must be a non-negative number"
        )
    return total_pop * cooking_demand_per_capita


def project_household_energy_demand(urban_hh: float, rural_hh: float) -> float:
    """Return total annual cooking energy demand given household counts."""

    if not isinstance(urban_hh, Real) or urban_hh < 0:
        raise ValueError("urban_hh must be a non-negative number")
    if not isinstance(rural_hh, Real) or rural_hh < 0:
        raise ValueError("rural_hh must be a non-negative number")
    return (
        urban_hh * URBAN_DEMAND_GJ_PER_HH + rural_hh * RURAL_DEMAND_GJ_PER_HH
    )


def disaggregate_to_hourly(
    annual_gj: float, cutout_path: str, variable: str, region_geom
) -> "pd.Series":
    """Disaggregate annual demand to an hourly series using ERA5 data."""

    import pandas as pd  # Imported lazily
    from era5_profiles import load_era5_series

    profile = load_era5_series(cutout_path, variable, region_geom)
    total = profile.sum()
    if total == 0:
        raise ValueError("ERA5 profile sums to zero; cannot disaggregate")
    weights = profile / total
    return weights * annual_gj


params = get_parameters()


def project_population(
    base_year: int,
    target_year: int,
    base_population: int,
    annual_growth_rate: float,
) -> float:
    """Compound population projection using exponential growth."""

    if target_year < base_year:
        raise ValueError("target_year must be greater than or equal to base_year")
    if annual_growth_rate < 0:
        raise ValueError("annual_growth_rate must be non-negative")

    years = target_year - base_year
    return base_population * ((1 + annual_growth_rate) ** years)


# Base assumptions (defaults enable importing without full parameter set)
base_year = 2025
base_population = params.get("population_total_2025", 0)
growth_rate = params.get("population_growth_rate_annual", 0)
per_capita_demand = params.get("cooking_energy_demand_per_capita_GJ_yr", 0)
hh_size_urban = params.get("household_size_urban", 1)
hh_size_rural = params.get("household_size_rural", 1)

# Model years and regional counts
years = [2030, 2040, 2050]
n_regions = len(regions) if regions else 1

# Project total population for each model year
total_population_by_year = {
    yr: project_population(base_year, yr, base_population, growth_rate) for yr in years
}

# Derive regional populations, falling back to a uniform split
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

