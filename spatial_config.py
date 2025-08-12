import os
import pandas as pd

# NOTE: Technology adoption is handled in the modelling modules; this
# configuration module does not import from the deprecated `scripts`
# package.

# Load demographic data (district-level household projections)
demographics = pd.read_csv("data/District-level_Household_Projections.csv")
demographics.columns = demographics.columns.str.strip()
demographics.set_index(['District', 'Year'], inplace=True)

# Extract regions (districts)
regions = sorted(demographics.index.get_level_values("District").unique())

# Assumed cooking energy demand per household in GJ/year (source: IEA country brief for Côte d'Ivoire, 2024)
URBAN_DEMAND_GJ_PER_HH = 6.5  # IEA (2024), page 5
RURAL_DEMAND_GJ_PER_HH = 5.5  # IEA (2024), page 5

def compute_demand_by_region_year():
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
