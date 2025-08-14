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
