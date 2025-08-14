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
    args = parser.parse_args()
    os.makedirs("results", exist_ok=True)
    if args.pipeline == "stockflow":
        msf.run_all_scenarios(args.scenarios, args.years)
        print(
            "✔ Stock‑flow scenarios have been generated and saved to the results directory."
        )
    elif args.pipeline == "cost":
        mc.run_all_scenarios(args.scenarios, args.years, optimise=args.optimise)
        print(
            "✔ Cost analysis scenarios have been generated and saved to the results directory."
        )


if __name__ == "__main__":
    main()
