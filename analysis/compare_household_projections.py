"""Compare district-level household projections from multiple data sources.

This script searches for all files matching
``data/District-level_Household_Projections*.csv``, combines their
contents into a single tidy :class:`pandas.DataFrame`, and exports the
result to ``results/household_projections_comparison.csv``.

Optionally, a simple difference plot can be generated for quality
assurance by passing the ``--plot`` flag.
"""

from __future__ import annotations

import argparse
import os
from glob import glob
from typing import List

import pandas as pd


def load_projection_files(pattern: str) -> pd.DataFrame:
    """Load and combine household projection CSV files.

    Parameters
    ----------
    pattern:
        Glob pattern locating the projection CSV files.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns ``District``, ``Year``, ``SourceFile``,
        ``Urban_Households`` and ``Rural_Households``.
    """
    files: List[str] = sorted(glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matched pattern: {pattern}")

    frames: List[pd.DataFrame] = []
    required_cols = ["District", "Year", "Urban_Households", "Rural_Households"]
    for path in files:
        df = pd.read_csv(path)
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise ValueError(f"{path} missing columns: {', '.join(sorted(missing))}")

        df = df[required_cols].copy()
        df["SourceFile"] = os.path.basename(path)
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    return combined[["District", "Year", "SourceFile", "Urban_Households", "Rural_Households"]]


def plot_differences(df: pd.DataFrame, out_path: str) -> None:
    """Create a simple bar plot of max household differences across sources.

    The plot shows the maximum absolute difference for urban and rural
    households across source files for each district.
    """
    if df["SourceFile"].nunique() < 2:
        print("Not enough source files to plot differences.")
        return

    import matplotlib.pyplot as plt  # Imported here to avoid hard dependency

    index = ["District", "Year"]
    pivot_urban = df.pivot_table(index=index, columns="SourceFile", values="Urban_Households")
    pivot_rural = df.pivot_table(index=index, columns="SourceFile", values="Rural_Households")

    diff_urban = pivot_urban.max(axis=1) - pivot_urban.min(axis=1)
    diff_rural = pivot_rural.max(axis=1) - pivot_rural.min(axis=1)

    diff_urban_district = diff_urban.groupby(level=0).max().sort_values(ascending=False)
    diff_rural_district = diff_rural.groupby(level=0).max().sort_values(ascending=False)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    diff_urban_district.plot(kind="bar", ax=axes[0], color="tab:blue")
    axes[0].set_ylabel("Max diff urban households")
    axes[0].set_title("Urban households: max difference across sources")

    diff_rural_district.plot(kind="bar", ax=axes[1], color="tab:orange")
    axes[1].set_ylabel("Max diff rural households")
    axes[1].set_title("Rural households: max difference across sources")
    axes[1].set_xlabel("District")

    fig.tight_layout()
    plt.savefig(out_path)


def main(plot: bool = False) -> None:
    pattern = os.path.join("data", "District-level_Household_Projections*.csv")
    df = load_projection_files(pattern)

    os.makedirs("results", exist_ok=True)
    out_csv = os.path.join("results", "household_projections_comparison.csv")
    df.to_csv(out_csv, index=False)
    print(f"Combined data written to {out_csv}")

    if plot:
        out_plot = os.path.join("results", "household_projections_differences.png")
        plot_differences(df, out_plot)
        print(f"Difference plot saved to {out_plot}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare household projection sources.")
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Create a plot of differences across sources for QA.",
    )
    args = parser.parse_args()
    main(plot=args.plot)
