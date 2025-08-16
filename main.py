"""
Entry point for the CI bioenergy modelling suite.

Author: 2kam
License: MIT

This script acts as a dispatcher between the stock‑flow and cost
analysis pipelines. Invoke it with a single positional argument
specifying which pipeline to run. For example::

    python main.py stockflow

will execute the stock‑and‑flow model and produce scenario projections,
while::

    python main.py cost

will run the cost analysis across all scenarios and years.
"""

from __future__ import annotations

import argparse
import os

import modelling_stock_flow as msf
import modelling_cost as mc
from config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the CI bioenergy modelling pipelines.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "pipeline",
        choices=["stockflow", "cost"],
        help="Select which modelling pipeline to run: 'stockflow' or 'cost'.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a YAML/JSON configuration file. Defaults to built-in config.",
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=None,
        help="Scenarios to evaluate. Defaults to those in the configuration file.",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=None,
        help="Model years to evaluate. Defaults to the configuration file.",
    )
    parser.add_argument(
        "--optimise",
        action="store_true",
        help="Solve a least-cost optimisation (requires PuLP).",
    )
    parser.add_argument(
        "--pypsa-export",
        action="store_true",
        help="Write PyPSA-Earth compatible CSVs after running the pipeline.",
    )
    parser.add_argument(
        "--timeseries",
        choices=["none", "era5_4h"],
        default="none",
        help="Select demand output: annual only or 4-hour ERA5-based series.",
    )
    parser.add_argument(
        "--solver",
        choices=["cbc", "glpk", "gurobi"],
        default=None,
        help="Select optimisation solver when using --optimise. Defaults to config.",
    )
    parser.add_argument(
        "--min-clean-share",
        type=float,
        default=None,
        help="Override minimum clean-technology share (fraction).",
    )
    parser.add_argument(
        "--max-firewood-share",
        type=float,
        default=None,
        help="Override maximum traditional firewood share (fraction).",
    )
    args = parser.parse_args()
    cfg = load_config(args.config)
    scenarios = args.scenarios or cfg.get("scenarios", [])
    years = args.years or cfg.get("years", [])
    solver = args.solver or cfg.get("solver", "cbc")
    constraints = cfg.get("constraints", {})
    min_clean_share = args.min_clean_share
    if min_clean_share is None:
        min_clean_share = constraints.get("min_clean_share")
    max_firewood_share = args.max_firewood_share
    if max_firewood_share is None:
        max_firewood_share = constraints.get("max_firewood_share")
    os.makedirs("results", exist_ok=True)
    if args.pipeline == "stockflow":
        msf.run_all_scenarios(
            scenarios=scenarios, years=years, timeseries=args.timeseries, config=cfg
        )
        print(
            "✔ Stock‑flow scenarios have been generated and saved to the results directory."
        )
        if args.pypsa_export:
            print("⚠ PyPSA export is currently only supported for the cost pipeline.")
    elif args.pipeline == "cost":
        df_full, _ = mc.run_all_scenarios(
            scenarios=scenarios,
            years=years,
            optimise=args.optimise,
            timeseries=args.timeseries,
            solver=solver,
            config=cfg,
            min_clean_share=min_clean_share,
            max_firewood_share=max_firewood_share,
        )
        print(
            "✔ Cost analysis scenarios have been generated and saved to the results directory."
        )
        if args.pypsa_export and not df_full.empty:
            from pypsa_export import write_pypsa_generators, write_pypsa_loads

            for (scenario, year), df_subset in df_full.groupby(["Scenario", "Year"]):
                tech_costs = mc._load_levelised_costs(scenario, year)
                out_dir = os.path.join("results", "pypsa", scenario, str(year))
                write_pypsa_loads(df_subset, out_dir)
                write_pypsa_generators(df_subset, tech_costs, out_dir)
            print(
                "✔ PyPSA export files written under results/pypsa/<scenario>/<year>/"
            )


if __name__ == "__main__":
    main()
