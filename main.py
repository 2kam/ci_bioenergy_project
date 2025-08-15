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
from config import SCENARIOS, YEARS


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
        "--scenarios",
        nargs="+",
        default=SCENARIOS,
        help="Scenarios to evaluate. Defaults to all configured scenarios.",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=YEARS,
        help="Model years to evaluate. Defaults to all configured years.",
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
    args = parser.parse_args()
    os.makedirs("results", exist_ok=True)
    if args.pipeline == "stockflow":
        msf.run_all_scenarios(args.scenarios, args.years)
        print(
            "✔ Stock‑flow scenarios have been generated and saved to the results directory."
        )
        if args.pypsa_export:
            print("⚠ PyPSA export is currently only supported for the cost pipeline.")
    elif args.pipeline == "cost":
        df_full, _ = mc.run_all_scenarios(
            args.scenarios, args.years, optimise=args.optimise
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
