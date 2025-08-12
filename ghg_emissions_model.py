"""Greenhouse gas emissions submodel.

This module translates energy demand by fuel into greenhouse gas (GHG)
emissions. It accounts for carbon dioxide (CO₂), methane (CH₄) and
nitrous oxide (N₂O) emissions from different cooking fuels and
technologies as well as emissions from grid electricity and a simple
land-use change estimate associated with unsustainable biomass use.

Emissions are returned both on a species basis (kilotonnes or tonnes)
and aggregated into total GHG emissions in million tonnes of CO₂-
equivalent (MtCO₂e) using 100‑year global warming potentials from the
IPCC AR6 report.
"""

from __future__ import annotations

from typing import Dict


def calculate_emissions(
    energy_by_fuel: Dict[str, float],
    params: Dict[str, float],
    grid_ef_CO2: float,
) -> Dict[str, float]:
    """Compute greenhouse gas emissions for a given energy breakdown.

    Parameters
    ----------
    energy_by_fuel : dict
        Dictionary mapping fuel categories (e.g. ``"traditional_firewood_GJ"``)
        to delivered energy demand in gigajoules.
    params : dict
        Global model parameters including emission factors and GWPs.
    grid_ef_CO2 : float
        The effective CO₂ emission factor of the electricity grid in kg/kWh
        for the current year, after applying decarbonisation.

    Returns
    -------
    dict
        A dictionary of emissions by species and source. Units are
        kilogram CO₂‑equivalent unless otherwise specified; the total
        GHG metric is returned in million tonnes CO₂e.
    """
    emissions: Dict[str, float] = {}

    # Helper to convert from energy and emission factors to tCO2e or t
    def co2e(gj: float, kg_per_gj: float, gwp: float = 1.0) -> float:
        return gj * kg_per_gj * gwp / 1000.0  # convert kg to tonnes

    # Firewood emissions
    g_fw = energy_by_fuel.get("traditional_firewood_GJ", 0.0)
    emissions["CO2_firewood"] = co2e(g_fw, params["emission_factor_CO2_firewood_kg_GJ"])
    emissions["CH4_firewood"] = co2e(g_fw, params["emission_factor_CH4_firewood_kg_GJ"], params["GWP_CH4"])
    emissions["N2O_firewood"] = co2e(g_fw, params["emission_factor_N2O_firewood_kg_GJ"], params["GWP_N2O"])

    # Charcoal emissions (production + use)
    g_ch = energy_by_fuel.get("traditional_charcoal_GJ", 0.0)
    emissions["CO2_charcoal"] = co2e(g_ch, params["emission_factor_CO2_charcoal_kg_GJ"])
    emissions["CH4_charcoal"] = co2e(g_ch, params["emission_factor_CH4_charcoal_kg_GJ"], params["GWP_CH4"])
    emissions["N2O_charcoal"] = co2e(g_ch, params["emission_factor_N2O_charcoal_kg_GJ"], params["GWP_N2O"])

    # Improved cookstoves: apply emission reduction factors
    for fuel in ("firewood", "charcoal"):
        g = energy_by_fuel.get(f"ics_{fuel}_GJ", 0.0)
        ef_CO2 = params[f"emission_factor_CO2_{fuel}_kg_GJ"]
        ef_CH4 = params[f"emission_factor_CH4_{fuel}_kg_GJ"] * (1 - params["emission_reduction_factor_ics_ch4"])
        ef_N2O = params[f"emission_factor_N2O_{fuel}_kg_GJ"] * (1 - params["emission_reduction_factor_ics_n2o"])
        emissions[f"CO2_ics_{fuel}"] = co2e(g, ef_CO2)
        emissions[f"CH4_ics_{fuel}"] = co2e(g, ef_CH4, params["GWP_CH4"])
        emissions[f"N2O_ics_{fuel}"] = co2e(g, ef_N2O, params["GWP_N2O"])

    # Biogas emissions: assume zero CO2 emissions from combustion but account for CH4 and N2O
    g_bg = energy_by_fuel.get("biogas_GJ", 0.0)
    emissions["CO2_biogas"] = 0.0
    emissions["CH4_biogas"] = co2e(g_bg, params["emission_factor_CH4_biogas_kg_GJ"], params["GWP_CH4"])
    emissions["N2O_biogas"] = co2e(g_bg, params["emission_factor_N2O_biogas_kg_GJ"], params["GWP_N2O"])

    # Ethanol emissions
    g_et = energy_by_fuel.get("ethanol_GJ", 0.0)
    emissions["CO2_ethanol"] = co2e(g_et, params["emission_factor_CO2_ethanol_kg_GJ"])
    emissions["CH4_ethanol"] = co2e(g_et, params["emission_factor_CH4_ethanol_kg_GJ"], params["GWP_CH4"])
    emissions["N2O_ethanol"] = co2e(g_et, params["emission_factor_N2O_ethanol_kg_GJ"], params["GWP_N2O"])

    # Electricity emissions: convert GJ to kWh and apply grid emission factors
    g_el = energy_by_fuel.get("electricity_GJ", 0.0)
    kwh = g_el * 277.778  # 1 GJ = 277.778 kWh
    emissions["CO2_electricity"] = kwh * grid_ef_CO2 / 1000.0
    emissions["CH4_electricity"] = kwh * params["grid_emission_factor_CH4_kg_kWh"] * params["GWP_CH4"] / 1000.0
    emissions["N2O_electricity"] = kwh * params["grid_emission_factor_N2O_kg_kWh"] * params["GWP_N2O"] / 1000.0

    # Land-use change: estimate unsustainable biomass share and multiply by emission factor
    uns_Mtoe = (
        (energy_by_fuel.get("traditional_firewood_GJ", 0.0) + energy_by_fuel.get("traditional_charcoal_GJ", 0.0))
        / 41_868_000
        * params.get("unsustainable_biomass_share_bau", 0.8)
    )
    emissions["LUC_tCO2e"] = uns_Mtoe * params["deforestation_emission_factor_tCO2e_Mtoe_unsustainable"]

    # Sum GHGs (tonnes) into MtCO2e
    total_ghg_tonnes = 0.0
    for key, value in emissions.items():
        # include only climate-relevant species (CO2, CH4, N2O)
        if any(sp in key for sp in ("CO2", "CH4", "N2O")):
            total_ghg_tonnes += value
    emissions["Total_GHG_MtCO2e"] = total_ghg_tonnes / 1_000_000.0

    # Improved biomass emissions: treat as improved cookstoves using firewood
    g_ib = energy_by_fuel.get("improved_biomass_GJ", 0.0)
    if g_ib > 0:
        ef_CO2_ib = params.get("emission_factor_CO2_firewood_kg_GJ")
        ef_CH4_ib = params.get("emission_factor_CH4_firewood_kg_GJ") * (
            1 - params.get("emission_reduction_factor_ics_ch4", 0)
        )
        ef_N2O_ib = params.get("emission_factor_N2O_firewood_kg_GJ") * (
            1 - params.get("emission_reduction_factor_ics_n2o", 0)
        )
        emissions["CO2_improved_biomass"] = co2e(g_ib, ef_CO2_ib)
        emissions["CH4_improved_biomass"] = co2e(g_ib, ef_CH4_ib, params.get("GWP_CH4"))
        emissions["N2O_improved_biomass"] = co2e(g_ib, ef_N2O_ib, params.get("GWP_N2O"))

    # LPG emissions: use explicit emission factors if provided
    g_lpg = energy_by_fuel.get("lpg_GJ", 0.0)
    if g_lpg > 0:
        ef_CO2_lpg = params.get("emission_factor_CO2_lpg_kg_GJ", 0.0)
        ef_CH4_lpg = params.get("emission_factor_CH4_lpg_kg_GJ", 0.0)
        ef_N2O_lpg = params.get("emission_factor_N2O_lpg_kg_GJ", 0.0)
        emissions["CO2_lpg"] = co2e(g_lpg, ef_CO2_lpg)
        emissions["CH4_lpg"] = co2e(g_lpg, ef_CH4_lpg, params.get("GWP_CH4"))
        emissions["N2O_lpg"] = co2e(g_lpg, ef_N2O_lpg, params.get("GWP_N2O"))

    return emissions