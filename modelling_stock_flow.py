"""
Stock-flow modelling pipeline for the CI bioenergy project.

This module orchestrates a high‑level simulation of future clean
cooking demand and associated greenhouse gas emissions across Côte
d'Ivoire. It follows the stock‑and‑flow philosophy, projecting
household numbers, estimating total cooking energy demand based on
household consumption intensities, allocating that demand across
different technologies under scenario assumptions and computing the
resulting emissions.

Scenarios are defined in ``SCENARIOS`` and currently include:

* ``bau`` – business as usual adoption trajectories
* ``clean_push`` – concerted push for clean alternatives
* ``biogas_incentive`` – strong incentives for biogas systems

The results are written to an Excel workbook at
``results/ci_bioenergy_scenarios.xlsx`` with a sheet per scenario.

Example usage::

    python main.py stockflow

to run all scenarios and produce the Excel output.
"""

from __future__ import annotations

import os
from typing import Dict, List
import pandas as pd

from data_input import get_parameters
from population_urbanization_model import calculate_population_urbanization
from energy_demand_model import project_household_energy_demand
from technology_adoption_model import get_tech_mix_by_scenario
from ghg_emissions_model import calculate_emissions

# Scenarios to evaluate
SCENARIOS: List[str] = ["bau", "clean_push", "biogas_incentive"]
# Model years
YEARS: List[int] = [2030, 2040, 2050]


def _map_energy_categories(energy_by_tech: Dict[str, float]) -> Dict[str, float]:
    """Convert high‑level technology categories into the keys expected by the
    emissions model.

    Parameters
    ----------
    energy_by_tech : dict
        Mapping of technology names (e.g. ``"firewood"``) to delivered
        energy in gigajoules.

    Returns
    -------
    dict
        Dictionary with keys matching the expected inputs for
        :func:`ghg_emissions_model.calculate_emissions`. Unknown
        technologies are passed through with a ``_GJ`` suffix.
    """
    mapped: Dict[str, float] = {}
    for tech, energy in energy_by_tech.items():
        if energy == 0:
            continue
        if tech == "firewood":
            mapped["traditional_firewood_GJ"] = mapped.get("traditional_firewood_GJ", 0) + energy
        elif tech == "charcoal":
            mapped["traditional_charcoal_GJ"] = mapped.get("traditional_charcoal_GJ", 0) + energy
        elif tech == "ics_firewood":
            mapped["ics_firewood_GJ"] = mapped.get("ics_firewood_GJ", 0) + energy
        elif tech == "ics_charcoal":
            mapped["ics_charcoal_GJ"] = mapped.get("ics_charcoal_GJ", 0) + energy
        elif tech == "biogas":
            mapped["biogas_GJ"] = mapped.get("biogas_GJ", 0) + energy
        elif tech == "ethanol":
            mapped["ethanol_GJ"] = mapped.get("ethanol_GJ", 0) + energy
        elif tech == "electricity":
            mapped["electricity_GJ"] = mapped.get("electricity_GJ", 0) + energy
        elif tech == "lpg":
            mapped["lpg_GJ"] = mapped.get("lpg_GJ", 0) + energy
        elif tech == "improved_biomass":
            mapped["improved_biomass_GJ"] = mapped.get("improved_biomass_GJ", 0) + energy
        else:
            # fall back to a generic category
            mapped[f"{tech}_GJ"] = mapped.get(f"{tech}_GJ", 0) + energy
    return mapped


def run_all_scenarios() -> Dict[str, pd.DataFrame]:
    """Execute all stock‑flow scenarios and write results to Excel.

    Returns
    -------
    dict
        Mapping of scenario names to data frames containing results for
        each year. Each data frame includes household counts, total
        energy demand, energy allocation by technology and detailed
        emission estimates.
    """
    params = get_parameters()
    os.makedirs("results", exist_ok=True)
    results_per_scenario: Dict[str, pd.DataFrame] = {}

    for scenario in SCENARIOS:
        scenario_results: List[Dict[str, float]] = []
        # Initialize grid emission factor CO₂; update each year
        grid_ef_CO2 = params["grid_emission_factor_CO2_kg_kWh"]
        for year in YEARS:
            # Project demographics
            pop = calculate_population_urbanization(
                year,
                params["population_total_2025"],
                params["urbanization_rate_2025"],
                params["population_growth_rate_annual"],
                params["urbanization_growth_rate_annual"],
                params["household_size_urban"],
                params["household_size_rural"],
            )
            urban_hh = pop["urban_households"]
            rural_hh = pop["rural_households"]
            # Compute total energy demand based on households
            total_demand = project_household_energy_demand(urban_hh, rural_hh)
            # Derive technology mix (energy by tech) for a national aggregate
            _, energy_by_tech = get_tech_mix_by_scenario(
                scenario,
                year,
                "National",
                params,
                total_demand,
                urban_hh,
                rural_hh,
                {},
            )
            # Map to emission categories
            energy_by_fuel = _map_energy_categories(energy_by_tech)
            # Apply grid decarbonisation: update the grid emission factor
            # for the current year before calculating emissions
            if year != YEARS[0]:
                grid_ef_CO2 *= (1 - params["grid_decarbonization_rate_annual"])
            # Compute emissions
            emissions = calculate_emissions(energy_by_fuel, params, grid_ef_CO2)
            # Prepare result row
            row: Dict[str, float] = {
                "Year": year,
                "Urban_Households": urban_hh,
                "Rural_Households": rural_hh,
                "Total_Demand_GJ": total_demand,
            }
            # Add energy allocation by technology for transparency
            for tech, energy in energy_by_tech.items():
                row[f"{tech}_GJ"] = energy
            # Append emissions
            row.update(emissions)
            scenario_results.append(row)
        # Convert to DataFrame
        results_per_scenario[scenario] = pd.DataFrame(scenario_results)

    # Write results to Excel workbook
    output_path = "results/ci_bioenergy_scenarios.xlsx"
    with pd.ExcelWriter(output_path) as writer:
        for scenario, df in results_per_scenario.items():
            df.to_excel(writer, sheet_name=scenario, index=False)
    return results_per_scenario