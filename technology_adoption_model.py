import os
import pandas as pd

# Load household projections once
household_df = pd.read_csv("data/District-level_Household_Projections.csv")
household_df.columns = household_df.columns.str.strip()
household_df.set_index(["District", "Year"], inplace=True)

# Base shares can be scenario-dependent later
base_shares = {
    "bau": {
        "urban": {
            "firewood": 0.2,
            "charcoal": 0.4,
            "ics_firewood": 0.1,
            "ics_charcoal": 0.05,
            "biogas": 0.05,
            "ethanol": 0.05,
            "electricity": 0.1,
            "lpg": 0.05,
            "improved_biomass": 0.0
        },
        "rural": {
            "firewood": 0.5,
            "charcoal": 0.15,
            "ics_firewood": 0.15,
            "ics_charcoal": 0.05,
            "biogas": 0.05,
            "ethanol": 0.0,
            "electricity": 0.05,
            "lpg": 0.05,
            "improved_biomass": 0.0
        }
    },
    "clean_push": {
        "urban": {
            "firewood": 0.1,
            "charcoal": 0.1,
            "ics_firewood": 0.05,
            "ics_charcoal": 0.05,
            "biogas": 0.1,
            "ethanol": 0.15,
            "electricity": 0.3,
            "lpg": 0.1,
            "improved_biomass": 0.05
        },
        "rural": {
            "firewood": 0.2,
            "charcoal": 0.1,
            "ics_firewood": 0.15,
            "ics_charcoal": 0.1,
            "biogas": 0.15,
            "ethanol": 0.05,
            "electricity": 0.15,
            "lpg": 0.05,
            "improved_biomass": 0.05
        }
    },
    "biogas_incentive": {
        "urban": {
            "firewood": 0.05,
            "charcoal": 0.05,
            "ics_firewood": 0.05,
            "ics_charcoal": 0.05,
            "biogas": 0.4,
            "ethanol": 0.05,
            "electricity": 0.2,
            "lpg": 0.1,
            "improved_biomass": 0.05
        },
        "rural": {
            "firewood": 0.15,
            "charcoal": 0.05,
            "ics_firewood": 0.1,
            "ics_charcoal": 0.05,
            "biogas": 0.35,
            "ethanol": 0.05,
            "electricity": 0.15,
            "lpg": 0.05,
            "improved_biomass": 0.05
        }
    }
}

def get_tech_mix_by_scenario(scenario, year, district, params, demand, urban_hh, rural_hh, prev_shares):
    # normalise scenario name: lower-case and replace spaces with underscores
    scenario_key = scenario.lower().replace(" ", "_")
    if scenario_key not in base_shares:
        raise ValueError(f"Scenario '{scenario}' not recognised")

    try:
        urban_count = household_df.loc[(district, year), "Urban_Households"]
        rural_count = household_df.loc[(district, year), "Rural_Households"]
    except KeyError:
        urban_count = urban_hh
        rural_count = rural_hh

    tech_mix = {}
    shares = {}

    for tech in base_shares[scenario_key]["urban"]:
        urban_share = base_shares[scenario_key]["urban"][tech]
        rural_share = base_shares[scenario_key]["rural"][tech]
        weighted_share = (urban_share * urban_count + rural_share * rural_count) / (urban_count + rural_count + 1e-6)
        energy = demand * weighted_share
        shares[tech] = round(energy, 4)

    return list(shares.keys()), shares
