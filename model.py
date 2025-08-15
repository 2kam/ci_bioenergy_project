# model.py  (v2)
from __future__ import annotations
import pandas as pd

# Import PuLP lazily to avoid a hard dependency when optimisation is not used.
try:
    import pulp  # type: ignore
except ImportError:
    pulp = None  # PuLP is optional; some functions will check for its presence
from typing import Dict

# Expose public API
__all__ = ["run_cost_fixed_mix", "run_cost_minimise_cost"]

# ------------------------------------------------------------------
# Helper: common result formatting
# ------------------------------------------------------------------
def _format_result(year: int,
                   region: str,
                   demand_GJ: float,
                   tech_costs: Dict[str, float],
                   variables: Dict[str, pulp.LpVariable]) -> tuple[pd.DataFrame, float]:
    rows = []
    total_cost = 0.0
    for tech, var in variables.items():
        gj = var.varValue
        cost = gj * tech_costs[tech]
        total_cost += cost
        rows.append({
            "Year": year,
            "Region": region,
            "Technology": tech,
            "Share": gj / demand_GJ,
            "Energy_GJ": gj,
            "Cost_USD": cost,
        })
    return pd.DataFrame(rows), total_cost

# ------------------------------------------------------------------
# 1. Fixed-mix calculator (original intent)
# ------------------------------------------------------------------
def run_cost_fixed_mix(year: int,
                       region: str,
                       demand_GJ: float,
                       shares: Dict[str, float],
                       tech_costs: Dict[str, float]) -> tuple[pd.DataFrame, float]:
    """
    Compute system cost for a *given* technology mix (no optimisation).
    """
    df = pd.DataFrame({
        "Year": year,
        "Region": region,
        "Technology": list(shares.keys()),
        "Share": list(shares.values()),
        "Energy_GJ": [demand_GJ * s for s in shares.values()],
        "Cost_USD": [demand_GJ * s * tech_costs[t]
                     for t, s in shares.items()],
    })
    total_cost = df["Cost_USD"].sum()
    return df, total_cost

# ------------------------------------------------------------------
# 2. Least-cost optimisation with policy constraints
# ------------------------------------------------------------------
def run_cost_minimise_cost(year: int,
                           region: str,
                           demand_GJ: float,
                           min_clean_share: float,
                           max_firewood_share: float,
                           tech_costs: Dict[str, float],
                           solver: str = "cbc") -> tuple[pd.DataFrame, float]:
    """
    LP that chooses the cheapest technology mix subject to:
      - Σ GJ == demand_GJ
      - clean_tech_share >= min_clean_share
      - firewood_tech_share <= max_firewood_share

    Parameters
    ----------
    solver : str, optional
        Optimisation solver to use (``"cbc"``, ``"glpk"`` or ``"gurobi"``).
    """
    clean_techs = {"biogas", "ethanol", "electricity", "lpg", "improved_biomass"}
    firewood_techs = {"firewood", "charcoal"}

    if pulp is None:
        raise RuntimeError(
            "PuLP is not installed. The cost minimisation optimisation cannot be performed."
        )
    model = pulp.LpProblem(f"CleanCooking_{region}_{year}", pulp.LpMinimize)

    # Decision variables: GJ allocated to each tech
    techs = list(tech_costs.keys())
    gj_vars = {t: pulp.LpVariable(f"gj_{t}", lowBound=0) for t in techs}

    # Objective: minimise total cost
    model += pulp.lpSum([gj_vars[t] * tech_costs[t] for t in techs])

    # Constraint 1: meet demand
    model += pulp.lpSum([gj_vars[t] for t in techs]) == demand_GJ

    # Constraint 2: clean-cooking minimum
    model += pulp.lpSum([gj_vars[t] for t in clean_techs]) >= min_clean_share * demand_GJ

    # Constraint 3: firewood cap
    model += pulp.lpSum([gj_vars[t] for t in firewood_techs]) <= max_firewood_share * demand_GJ

    # Solve
    solver_map = {
        "cbc": pulp.PULP_CBC_CMD,
        "glpk": pulp.GLPK_CMD,
        "gurobi": pulp.GUROBI_CMD,
    }
    if solver not in solver_map:
        raise ValueError(f"Unknown solver '{solver}'.")
    solver_cmd = solver_map[solver](msg=0)
    if hasattr(solver_cmd, "available") and not solver_cmd.available():
        raise RuntimeError(f"Requested solver '{solver}' is not available.")
    model.solve(solver_cmd)
    if pulp.LpStatus[model.status] != "Optimal":
        raise RuntimeError(f"No optimal solution for {region} in {year}.")

    return _format_result(year, region, demand_GJ, tech_costs, gj_vars)
