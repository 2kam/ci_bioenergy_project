import os
import pandas as pd

from paths import get_data_path

# NOTE: Technology adoption is handled in the modelling modules; this
# configuration module does not import from the deprecated `scripts`
# package.

# Load demographic data (district-level household projections)
demographics = pd.read_csv(
    get_data_path("District-level_Household_Projections.csv")
)
demographics.columns = demographics.columns.str.strip()
demographics.set_index(['District', 'Year'], inplace=True)

# Extract regions (districts)
regions = sorted(demographics.index.get_level_values("District").unique())

# Assumed cooking energy demand per household in GJ/year (source: IEA country brief for Côte d'Ivoire, 2024)
URBAN_DEMAND_GJ_PER_HH = 6.5  # IEA (2024), page 5
RURAL_DEMAND_GJ_PER_HH = 5.5  # IEA (2024), page 5


def compute_demand_by_region_year():
    required_cols = {"Urban_Households", "Rural_Households"}
    missing = required_cols - set(demographics.columns)
    if missing:
        raise KeyError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    demand = {}
    for (district, year), row in demographics.iterrows():
        if year not in demand:
            demand[year] = {}
        urban_demand = row["Urban_Households"] * URBAN_DEMAND_GJ_PER_HH
        rural_demand = row["Rural_Households"] * RURAL_DEMAND_GJ_PER_HH
        total_demand = urban_demand + rural_demand
        demand[year][district] = total_demand
    return demand

def compute_urban_rural_hh_by_region_year():
    urban = {}
    rural = {}
    for (district, year), row in demographics.iterrows():
        if year not in urban:
            urban[year] = {}
            rural[year] = {}
        urban[year][district] = row["Urban_Households"]
        rural[year][district] = row["Rural_Households"]
    return urban, rural

# Precompute values for use in optimization and adoption models
demand_by_region_year = compute_demand_by_region_year()
urban_hh_by_region_year, rural_hh_by_region_year = compute_urban_rural_hh_by_region_year()


def generate_buses_csv(output_path: str = os.path.join("results", "buses.csv")) -> pd.DataFrame:
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


if __name__ == "__main__":
    buses_df = generate_buses_csv()

