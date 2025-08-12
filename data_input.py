"""Data input module for the CI bioenergy model.

This module contains a single function, :func:`get_parameters`, which
returns a dictionary of all model parameters. These parameters include
demographic assumptions, energy demand figures, technology efficiencies,
emission factors, global warming potentials (GWPs), land use change
coefficients and adoption limits. Centralising the parameters in one
place makes it easy to tweak scenarios and ensures that all downstream
modules read from a consistent source.
"""

from __future__ import annotations


def get_parameters():
    """Return a dictionary with every model parameter used by the other modules."""
    return {
        # ----------------- DEMOGRAPHICS -----------------
        # Source: National projections and literature in biomass potential report (2020)
        "population_total_2025": 29_000_000,
        "population_growth_rate_annual": 0.025,
        "urbanization_rate_2025": 0.55,
        "urbanization_growth_rate_annual": 0.005,
        "household_size_urban": 5.0,
        "household_size_rural": 7.0,

        # ----------------- ENERGY DEMAND -----------------
        # Source: Study of the biomass potential in Côte d'Ivoire, MINEDD, 2020
        "cooking_energy_demand_per_capita_GJ_yr": 15.0,  # average from estimated 10–20 GJ/capita/year
        "agro_industrial_energy_demand_2025_Mtoe": 2.0,
        "agro_industrial_demand_growth_rate_annual": 0.015,
        "rural_energy_demand_per_capita_GJ_yr": 15.0,  # aligned with national rural biomass consumption

        # ----------------- TECHNOLOGY EFFICIENCIES -------
        # Source: Stove efficiency assumptions in biomass report & standard ranges
        "efficiency_traditional_firewood": 0.11,  # inefficient traditional 3-stone fire
        "efficiency_traditional_charcoal": 0.25,
        "efficiency_ics_firewood": 0.37,  # ICS (improved cookstoves)
        "efficiency_ics_charcoal": 0.40,
        "efficiency_biogas_cookstove": 0.55,
        "efficiency_ethanol_cookstove": 0.50,
        "efficiency_electric_cookstove": 0.85,

        # ----------------- EMISSION FACTORS (kg per GJ) --
        # Source: IPCC default values for developing countries (adjusted for Côte d’Ivoire context)
        "emission_factor_CO2_firewood_kg_GJ": 110,
        "emission_factor_CH4_firewood_kg_GJ": 0.5,
        "emission_factor_N2O_firewood_kg_GJ": 0.005,
        "emission_factor_PM25_firewood_kg_GJ": 0.1,

        "emission_factor_CO2_charcoal_kg_GJ": 310,   # includes production emissions
        "emission_factor_CH4_charcoal_kg_GJ": 0.8,
        "emission_factor_N2O_charcoal_kg_GJ": 0.008,
        "emission_factor_PM25_charcoal_kg_GJ": 0.08,

        "emission_reduction_factor_ics_pm25": 0.6,
        "emission_reduction_factor_ics_ch4": 0.4,
        "emission_reduction_factor_ics_n2o": 0.3,

        # Source: IPCC AR6 default
        "emission_factor_CO2_biogas_kg_GJ": 0,
        "emission_factor_CH4_biogas_kg_GJ": 0.005,
        "emission_factor_N2O_biogas_kg_GJ": 0.001,
        "biogas_leakage_rate_percent": 0.05,

        "emission_factor_CO2_ethanol_kg_GJ": 50,
        "emission_factor_CH4_ethanol_kg_GJ": 0.002,
        "emission_factor_N2O_ethanol_kg_GJ": 0.0005,

        "grid_emission_factor_CO2_kg_kWh": 0.4,
        "grid_emission_factor_CH4_kg_kWh": 0.0001,
        "grid_emission_factor_N2O_kg_kWh": 0.00001,
        "grid_decarbonization_rate_annual": 0.01,

        # ----------------- GWPs (IPCC AR6 100-yr) ------
        "GWP_CH4": 27.9,
        "GWP_N2O": 273,

        # ----------------- LAND USE CHANGE -------------
        # Source: Biomass report estimates of forest degradation impact
        "deforestation_emission_factor_tCO2e_Mtoe_unsustainable": 1500,
        "unsustainable_biomass_share_bau": 0.8,

        # ----------------- ADOPTION LIMITS -------------
        # Source: Based on realistic adoption ceilings in regional programs (e.g. ECREEE)
        "max_penetration_ics": 0.9,
        "max_penetration_biogas": 0.4,
        "max_penetration_ethanol": 0.3,
        "max_penetration_electricity_cooking": 0.9,

        # ----------------- TIME HORIZON ----------------
        "start_year": 2025,
        "end_year": 2050,

        # ----------------- BIOGAS YIELD ----------------
        # Source: Biogas yield potential in Cote d'Ivoire households (from livestock and waste)
        "biogas_yield_m3_per_household_yr": 300,
        "biogas_energy_content_GJ_m3": 0.021,
    }
