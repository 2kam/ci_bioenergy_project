"""
Cost optimisation pipeline for the CI bioenergy project.

Author: 2kam
License: MIT

This module performs a simplified least‑cost analysis of clean cooking
technology pathways at the district level. For each scenario and year,
it allocates regional cooking energy demand across the available
technologies according to the same adoption assumptions used in the
stock‑flow model. It then multiplies the energy delivered by an
approximate levelised cost per gigajoule to estimate total system
costs.

The resulting detailed and summary outputs are written to
``results/ci_bioenergy_techpathways.xlsx`` with two sheets: ``Details``
and ``Summary``.

Example usage::

    python main.py cost

to run the cost optimisation for all scenarios and years.
"""

from __future__ import annotations

import os
from typing import Dict, List, Tuple
import pandas as pd

from spatial_config import (
    regions,
    demand_by_region_year,
    urban_hh_by_region_year,
    rural_hh_by_region_year,
    URBAN_DEMAND_GJ_PER_HH,
    RURAL_DEMAND_GJ_PER_HH,
)
from technology_adoption_model import get_tech_mix_by_scenario
from model import run_cost_fixed_mix
from config import SCENARIOS, YEARS
DISCOUNT_RATE = 0.05
BASE_YEAR = 2025
 

def _load_levelised_costs(
    scenario: str | None = None, year: int | None = None
) -> Dict[str, float]:
    """Load levelised cost data from ``data/tech_specs.csv``.

    The CSV must contain ``Technology`` and ``Cost_per_GJ`` columns. If
    optional ``Scenario`` or ``Year`` columns are present, this function
    filters the table using the provided ``scenario`` and ``year``
    parameters.

    Parameters
    ----------
    scenario : str, optional
        Scenario name to filter on when a ``Scenario`` column exists.
    year : int, optional
        Year to filter on when a ``Year`` column exists.

    Returns
    -------
    dict
        Mapping of technology names to levelised cost per GJ (USD/GJ).
    """
    data_path = os.path.join(os.path.dirname(__file__), "data", "tech_specs.csv")
    df = pd.read_csv(data_path)

    if scenario is not None and "Scenario" in df.columns:
        df = df[df["Scenario"] == scenario]
    if year is not None and "Year" in df.columns:
        df = df[df["Year"] == year]

    return dict(zip(df["Technology"], df["Cost_per_GJ"]))


def _compute_levelised_costs(urban_hh: float, rural_hh: float) -> Dict[str, float]:
    """Derive an approximate cost per gigajoule for each technology.

    Parameters
    ----------
    urban_hh : float
        Number of urban households.
    rural_hh : float
        Number of rural households.

    Returns
    -------
    dict
        Mapping of technology names to levelised cost per GJ (USD/GJ).

    Notes
    -----
    CAPEX per household (USD) is amortised over 15 years and combined with
    fuel costs to estimate a levelised cost per gigajoule.
    """
    # CAPEX per household (USD) amortised over 15 years
    capex = {
        "firewood": 0,
        "charcoal": 0,
        "ics_firewood": 25,
        "ics_charcoal": 30,
        "biogas": 450,
        "ethanol": 75,
        "electricity": 100,
        "lpg": 60,
        "improved_biomass": 40,
    }
    # Fuel cost per GJ (USD)
    fuel = {
        "firewood": 2,
        "charcoal": 6,
        "ics_firewood": 2,
        "ics_charcoal": 6,
        "biogas": 1,
        "ethanol": 15,
        "electricity": 12,
        "lpg": 10,
        "improved_biomass": 4,
    }
    levelised: Dict[str, float] = {}
    years_lifetime = 15

    # Compute average household demand weighted by urban/rural counts
    total_hh = urban_hh + rural_hh
    if total_hh > 0:
        annual_energy_per_hh = (
            (URBAN_DEMAND_GJ_PER_HH * urban_hh)
            + (RURAL_DEMAND_GJ_PER_HH * rural_hh)
        ) / total_hh
    else:
        # Fallback to simple mean if household data is unavailable
        annual_energy_per_hh = (URBAN_DEMAND_GJ_PER_HH + RURAL_DEMAND_GJ_PER_HH) / 2

    for tech in fuel:
        capex_per_gj = 0.0
        if capex.get(tech, 0) > 0 and annual_energy_per_hh > 0:
            capex_per_gj = capex[tech] / (annual_energy_per_hh * years_lifetime)
        levelised[tech] = fuel[tech] + capex_per_gj

    return levelised



def run_all_scenarios(
    scenarios: List[str] | None = None, years: List[int] | None = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    """Execute the cost optimisation pipeline across all scenarios and years.

    Parameters
    ----------
    scenarios : list, optional
        Scenario names to evaluate. Defaults to :data:`config.SCENARIOS`.
    years : list, optional
        Model years to process. Defaults to :data:`config.YEARS`.

    Returns
    -------
    DataFrame, DataFrame
        A tuple containing the detailed results for each region and the
        summary of total costs by scenario and year.
    """
    scenarios = scenarios or SCENARIOS
    years = years or YEARS
    os.makedirs("results", exist_ok=True)
    all_rows: List[pd.DataFrame] = []
    summary_rows: List[Dict[str, float]] = []
    tech_costs = _load_levelised_costs()

    for scenario in SCENARIOS:
        for year in YEARS:
            tech_costs: Dict[str, float] = _load_levelised_costs(scenario, year)
            
    for scenario in scenarios:
        for year in years:

            tech_costs = _load_levelised_costs(scenario, year)



            for reg in regions:
                demand = demand_by_region_year.get(year, {}).get(reg, 0.0)
                urban_hh = urban_hh_by_region_year.get(year, {}).get(reg, 0.0)
                rural_hh = rural_hh_by_region_year.get(year, {}).get(reg, 0.0)
                if demand <= 0:
                    continue
                # Derive energy shares for the district using the adoption model
                _, energy_shares = get_tech_mix_by_scenario(
                    scenario,
                    year,
                    reg,
                    {},
                    demand,
                    urban_hh,
                    rural_hh,
                    {},
                )
                # Convert energy shares to fractional shares
                shares_fraction: Dict[str, float] = {}
                for tech, energy in energy_shares.items():
                    shares_fraction[tech] = energy / demand if demand > 0 else 0.0
                # Run cost calculation using the fixed mix function
                df_reg, cost = run_cost_fixed_mix(year, reg, demand, shares_fraction, tech_costs)
                df_reg["Scenario"] = scenario
                all_rows.append(df_reg)

                # Discounting: NPV-style
                discount_factor = 1 / ((1 + DISCOUNT_RATE) ** (year - BASE_YEAR))
                discounted_cost = cost * discount_factor
                summary_rows.append(
                    {
                        "Scenario": scenario,
                        "Year": year,
                        "Region": reg,
                        "Total_Cost_USD": round(cost, 2),
                        "Discounted_Cost_USD": round(discounted_cost, 2),
                    }
                )
    # Combine results into DataFrames
    df_full = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
    df_summary = pd.DataFrame(summary_rows)
    # Write outputs to Excel
    output_path = "results/ci_bioenergy_techpathways.xlsx"
    with pd.ExcelWriter(output_path) as writer:
        if not df_full.empty:
            df_full.to_excel(writer, sheet_name="Details", index=False)
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
    return df_full, df_summary
