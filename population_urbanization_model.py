"""Population and urbanisation submodel.

This module encapsulates a simple demographic projection that scales
baseline population and urbanisation rates into future years. It
calculates the total, urban and rural populations as well as the
corresponding number of households for a given year. Household
numbers are derived from region-specific household sizes.
"""

from __future__ import annotations

from typing import Dict


def calculate_population_urbanization(
    year: int,
    initial_pop: float,
    initial_urban_rate: float,
    pop_growth_rate: float,
    urban_growth_rate: float,
    household_size_urban: float,
    household_size_rural: float,
) -> Dict[str, float]:
    """Project population, urbanisation and households to a future year.

    Parameters
    ----------
    year : int
        Calendar year for which to perform the projection.
    initial_pop : float
        Total population in the base year (2025).
    initial_urban_rate : float
        Urbanisation fraction in the base year (0 ≤ rate ≤ 1).
    pop_growth_rate : float
        Annual fractional growth rate of the total population.
    urban_growth_rate : float
        Annual change in the urban share (positive for increasing urbanisation).
    household_size_urban : float
        Average number of people per household in urban areas.
    household_size_rural : float
        Average number of people per household in rural areas.

    Returns
    -------
    Dict[str, float]
        A dictionary with keys ``total_population``, ``urban_population``,
        ``rural_population``, ``urban_households`` and ``rural_households``.
    """
    delta = year - 2025
    # project total population using compound growth
    total_pop = initial_pop * (1 + pop_growth_rate) ** delta
    # update urbanisation rate; constrain to 90 % to avoid unrealistic values
    urban_rate = min(initial_urban_rate + urban_growth_rate * delta, 0.9)
    urban_pop = total_pop * urban_rate
    rural_pop = total_pop - urban_pop
    # compute households by dividing population by household size
    urban_hh = urban_pop / household_size_urban
    rural_hh = rural_pop / household_size_rural
    return {
        "total_population": total_pop,
        "urban_population": urban_pop,
        "rural_population": rural_pop,
        "urban_households": urban_hh,
        "rural_households": rural_hh,
    }