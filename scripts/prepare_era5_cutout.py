"""Download an ERA5 cutout using atlite.

This helper script wraps :class:`atlite.Cutout` and stores the
resulting NetCDF file under ``data/era5``.  The cutout can then be
used by other modules (see ``era5_profiles.py``).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import atlite

# Ensure the project root is importable when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from era5_profiles import get_cutout_path  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare an ERA5 cutout and store hourly variables as a NetCDF file.",
    )
    parser.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        metavar=("MIN_LON", "MIN_LAT", "MAX_LON", "MAX_LAT"),
        required=True,
        help="Bounding box specified as min_lon min_lat max_lon max_lat",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        required=True,
        help="First year to include (e.g. 2018)",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        required=True,
        help="Last year to include (inclusive)",
    )
    args = parser.parse_args()

    lon_min, lat_min, lon_max, lat_max = args.bbox
    cutout_path = get_cutout_path(args.start_year, args.end_year)
    cutout_path.parent.mkdir(parents=True, exist_ok=True)

    cutout = atlite.Cutout(
        path=cutout_path,
        module="era5",
        x=slice(lon_min, lon_max),
        y=slice(lat_min, lat_max),
        time=slice(f"{args.start_year}-01-01", f"{args.end_year}-12-31"),
    )
    # Download a standard set of hourly variables
    cutout.prepare(features=["temperature", "wind", "influx"], overwrite=True)
    print(f"Cutout written to {cutout_path}")


if __name__ == "__main__":
    main()
