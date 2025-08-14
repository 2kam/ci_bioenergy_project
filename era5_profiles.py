"""Utility helpers for working with ERA5 cutouts.

The path to the cutouts generated via ``scripts/prepare_era5_cutout.py``
is centralised here to keep data flow consistent across the project.
"""

from __future__ import annotations

from pathlib import Path

import atlite

CUTOUT_DIR = Path("data/era5")


def get_cutout_path(start_year: int, end_year: int) -> Path:
    """Return the file path for a cutout covering ``start_year`` to ``end_year``."""
    return CUTOUT_DIR / f"era5_{start_year}-{end_year}.nc"


def load_cutout(start_year: int, end_year: int) -> atlite.Cutout:
    """Load a prepared cutout from disk."""
    path = get_cutout_path(start_year, end_year)
    return atlite.Cutout.from_netcdf(path)

import pandas as pd
from typing import Any


def load_era5_series(cutout_path: str, variable: str, region_geom: Any) -> pd.Series:
    """Extract an hourly ERA5 series averaged over a region.

    Parameters
    ----------
    cutout_path : str
        Path to an atlite cutout NetCDF file.
    variable : str
        Name of the ERA5 variable, e.g. ``"t2m"`` for 2 m temperature.
    region_geom : shapely geometry or GeoPandas object
        Geometry describing the target region in WGS84 coordinates.

    Returns
    -------
    pandas.Series
        Hourly values of the requested ERA5 variable averaged over the
        region. The series index is a :class:`pandas.DatetimeIndex` in UTC.
    """
    import xarray as xr
    import geopandas as gpd

    ds = xr.open_dataset(cutout_path)

    # Normalise geometry to a shapely object and project to the dataset CRS
    if isinstance(region_geom, (gpd.GeoDataFrame, gpd.GeoSeries)):
        geom = region_geom.geometry.unary_union
        geom = gpd.GeoSeries([geom], crs=region_geom.crs or "EPSG:4326")
    else:
        geom = gpd.GeoSeries([region_geom], crs="EPSG:4326")

    if hasattr(ds, "rio") and ds.rio.crs:
        geom = geom.to_crs(ds.rio.crs)
    else:
        geom = geom.to_crs("EPSG:4326")

    minx, miny, maxx, maxy = geom.total_bounds

    # Slice the cutout to the bounding box of the region and average spatially
    arr = ds[variable].sel(x=slice(minx, maxx), y=slice(maxy, miny))
    series = arr.mean(dim=("x", "y")).to_series()
    series.name = variable
    return series
