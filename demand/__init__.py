"""Demand package exposing demographic-based demand utilities."""

from __future__ import annotations

from .demographics import (
    URBAN_DEMAND_GJ_PER_HH,
    RURAL_DEMAND_GJ_PER_HH,
    load_demographics,
    demographics,
    regions,
    compute_demand_by_region_year,
    compute_urban_rural_hh_by_region_year,
    demand_by_region_year,
    urban_hh_by_region_year,
    rural_hh_by_region_year,
)


def get_demand(year: int) -> dict[str, float]:
    """Return regional demand (GJ) for ``year``.

    Parameters
    ----------
    year : int
        Target year.

    Returns
    -------
    dict
        Mapping of region names to cooking energy demand in gigajoules.
    """

    return demand_by_region_year.get(year, {})


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
    "get_demand",
]

