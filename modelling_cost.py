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
)
from technology_adoption_model import get_tech_mix_by_scenario
from model import run_cost_fixed_mix

# Scenarios and years to evaluate
SCENARIOS: List[str] = ["bau", "clean_push", "biogas_incentive"]
YEARS: List[int] = [2030, 2040, 2050]
DISCOUNT_RATE = 0.05
BASE_YEAR = 2025

def _compute_levelised_costs() -> Dict[str, float]:
    """Derive an approximate cost per gigajoule for each technology.

    The original cost optimisation model separates capital expenditure
    (CAPEX) and fuel costs. CAPEX is specified per household and
    amortised over a 15‑year stove lifetime. To convert this to a
    gigajoule basis, we assume an average urban household consumption
    of ``URBAN_DEMAND_GJ_PER_HH`` GJ/year and use the amortisation
    period. The resulting cost per GJ is the sum of the amortised
    CAPEX and the fuel cost.

    Returns
    -------
    dict
        Mapping of technology names to levelised cost per GJ (USD/GJ).
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
    # Use average urban household demand to convert capex to USD/GJ
    annual_energy_per_hh = URBAN_DEMAND_GJ_PER_HH
    for tech in fuel.keys():
        capex_per_gj = 0.0
        if capex.get(tech, 0) > 0:
            capex_per_gj = capex[tech] / (annual_energy_per_hh * years_lifetime)
        levelised[tech] = fuel[tech] + capex_per_gj
    return levelised


def run_all_scenarios() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Execute the cost optimisation pipeline across all scenarios and years.

    Returns
    -------
    DataFrame, DataFrame
        A tuple containing the detailed results for each region and the
        summary of total costs by scenario and year.
    """
    os.makedirs("results", exist_ok=True)
    tech_costs: Dict[str, float] = _compute_levelised_costs()
    all_rows: List[pd.DataFrame] = []
    summary_rows: List[Dict[str, float]] = []

    for scenario in SCENARIOS:
        for year in YEARS:
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
