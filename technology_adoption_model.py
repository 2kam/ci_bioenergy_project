
import os
import json
from datetime import datetime
from functools import lru_cache

from typing import List, Tuple

import pandas as pd



@lru_cache()
def load_household_df() -> pd.DataFrame:
    """Read household projections from disk.

    Returns
    -------
    pandas.DataFrame
        Data indexed by ``District`` and ``Year`` with household counts.
    """

    path = os.path.join("data", "District-level_Household_Projections.csv")
    try:
        df = pd.read_csv(path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Household projection file not found: {path}"
        ) from exc
    df.columns = df.columns.str.strip()
    df.set_index(["District", "Year"], inplace=True)
    return df

from paths import get_data_path

# Load household projections once
household_df = pd.read_csv(
    get_data_path("District-level_Household_Projections.csv")
)
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

def get_tech_mix_by_scenario(
    scenario: str,
    year: int,
    district: str,
    params: dict,
    demand: float,
    urban_hh: float,
    rural_hh: float,
    prev_shares: dict,
) -> Tuple[pd.DataFrame, dict]:
    """Return technology adoption shares and energy by technology.

    Parameters
    ----------
    scenario : str
        Scenario name.
    year : int
        Evaluation year.
    district : str
        Region for which to compute the mix.
    params : dict
        Model parameters (unused, maintained for backward compatibility).
    demand : float
        Total cooking energy demand for the region and year in GJ.
    urban_hh : float
        Number of urban households (used if the projection table lacks the
        region/year combination).
    rural_hh : float
        Number of rural households (used if the projection table lacks the
        region/year combination).
    prev_shares : dict
        Previous year shares (unused but retained for compatibility).

    Returns
    -------
    tuple
        ``(df, energy_by_tech)`` where ``df`` is indexed by ``region`` and
        ``year`` with columns ``technology``, ``share`` and ``energy_GJ``.
        ``energy_by_tech`` is a simple mapping used by legacy code paths.
    """

    # normalise scenario name: lower-case and replace spaces with underscores
    scenario_key = scenario.lower().replace(" ", "_")
    if scenario_key not in base_shares:
        raise ValueError(f"Scenario '{scenario}' not recognised")

    hh_df = load_household_df()
    try:
        urban_count = hh_df.loc[(district, year), "Urban_Households"]
        rural_count = hh_df.loc[(district, year), "Rural_Households"]
    except KeyError:
        urban_count = urban_hh
        rural_count = rural_hh

    rows = []
    energy_by_tech: dict = {}

    for tech in base_shares[scenario_key]["urban"]:
        urban_share = base_shares[scenario_key]["urban"][tech]
        rural_share = base_shares[scenario_key]["rural"][tech]
        weighted_share = (urban_share * urban_count + rural_share * rural_count) / (
            urban_count + rural_count + 1e-6
        )
        energy = demand * weighted_share
        energy_by_tech[tech] = round(energy, 4)
        rows.append(
            {
                "region": district,
                "year": year,
                "technology": tech,
                "share": round(weighted_share, 4),
                "energy_GJ": round(energy, 4),
            }
        )

    df = pd.DataFrame(rows).set_index(["region", "year"])
    return df, energy_by_tech


def generate_adoption_tables(
    scenario: str, years: List[int], districts: List[str] | None = None
) -> pd.DataFrame:
    """Generate adoption tables for a scenario and persist to CSV.

    Parameters
    ----------
    scenario : str
        Scenario name to evaluate.
    years : list
        Years to include.
    districts : list, optional
        Districts to process. Defaults to all districts in the household
        projection table.

    Returns
    -------
    pandas.DataFrame
        Adoption data indexed by region and year with technology, share and
        energy columns.
    """

    hh_df = load_household_df()
    districts = districts or sorted(hh_df.index.get_level_values(0).unique())
    records: List[pd.DataFrame] = []
    params = {}
    for year in years:
        for district in districts:
            try:
                hh = hh_df.loc[(district, year)]
                urban_hh = hh["Urban_Households"]
                rural_hh = hh["Rural_Households"]
            except KeyError:
                continue
            demand = (urban_hh * 6.5) + (rural_hh * 5.5)
            df, _ = get_tech_mix_by_scenario(
                scenario, year, district, params, demand, urban_hh, rural_hh, {}
            )
            records.append(df)

    result = pd.concat(records)
    out_dir = os.path.join("results", "adoption")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{scenario}.csv")
    result.to_csv(out_path)

    meta = {
        "timestamp": datetime.utcnow().isoformat(),
        "scenario": scenario,
        "years": years,
        "parameters": params,
    }
    with open(os.path.join(out_dir, f"{scenario}_metadata.json"), "w") as f:
        json.dump(meta, f)
    return result

