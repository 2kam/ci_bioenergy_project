# CI Bioenergy Modelling Suite

This project provides an end‑to‑end modelling framework for exploring
clean cooking transitions in Côte d'Ivoire. It contains two
independent pipelines:

* **Stock–flow model** (`stockflow`): projects household numbers,
  calculates cooking energy demand on a per‑household basis, allocates
  demand across fuel/technology options under different adoption
  scenarios and computes associated greenhouse gas emissions.

* **Cost analysis** (`cost`): estimates the total system cost of
  meeting regional cooking energy demand by applying the same
  adoption assumptions and multiplying the delivered energy by a
  levelised cost per gigajoule.

Both pipelines read from a single demographic dataset
(`data/District‑level_Household_Projections.csv`), share the same
assumptions about household energy consumption (6.5 GJ/year for urban
households and 5.5 GJ/year for rural households) and include a
harmonised list of technologies (`firewood`, `charcoal`,
`ics_firewood`, `ics_charcoal`, `biogas`, `ethanol`, `electricity`,
`lpg`, `improved_biomass`). Scenario names are normalised to lowercase
with underscores.

## Prerequisites

* Python 3.8 or later.
* The only required Python package is **pandas**. The model includes
  optional support for linear programming via **PuLP**; however, the
  provided cost analysis uses a fixed‑mix calculation and does not
  require PuLP. If you wish to run the `run_cost_minimise_cost` function
  in `model.py`, install PuLP via `pip install pulp`.

## Running the models

The `main.py` script acts as a dispatcher and must be provided with a
`pipeline` argument, either `stockflow` or `cost`. Run it with the
following format:

```bash
python main.py <pipeline>
```

The script automatically creates a `results/` directory where outputs
are stored. This folder is excluded from version control; regenerate the
Excel files using the commands below and store any published results
outside the repository (e.g. in a release asset or shared drive).

1. **Clone or download the repository** and navigate to its root
   directory.

2. **Install dependencies** (if not already available):

   ```bash
   pip install pandas
   # Optional: pip install pulp
   ```

3. **Run the stock–flow scenarios**. This produces an Excel workbook
   containing scenario projections for 2030, 2040 and 2050:

   ```bash
   python main.py stockflow
   ```

   The results will be saved to `results/ci_bioenergy_scenarios.xlsx`. The
   workbook contains one sheet per scenario (`bau`, `clean_push`,
   `biogas_incentive`) with columns for household numbers, total
   demand, energy allocation by technology and detailed emissions.

4. **Run the cost analysis**. This uses the same adoption scenarios
   and calculates levelised costs per technology (CAPEX amortised
   over 15 years divided by an average household demand plus fuel
   costs) to estimate total system costs:

   ```bash
   python main.py cost
   ```

   The results will be saved to `results/ci_bioenergy_techpathways.xlsx`.
   The workbook includes a `Details` sheet with cost breakdowns by
   technology and a `Summary` sheet with total costs by scenario and
   year.

5. **Inspect the outputs** using your preferred spreadsheet
   application. For example, the stock–flow model can be checked to
   verify that total demand for 2030 is nearly identical across
   scenarios (within ~1 %), technology lists match in both models and
   scenario names appear in lowercase.

## Aggregating technology pathway results

Running the cost analysis for multiple scenarios produces per‑scenario
CSV files in the `results/` directory (e.g.
`techpathways_<scenario>.csv` and `techpathways_summary_<scenario>.csv`).
Combine these into consolidated tables with a `Scenario` column by
running:

```bash
python results/aggregate_techpathways.py
```

This generates `techpathways_all.csv` and
`techpathways_summary_all.csv` in the same folder.

## Supply and demand comparison

Estimate the cooking energy demand for future targets and compare it
with available biomass supply using:

```bash
python analysis/compare_supply_demand.py --target-year 2030
```

The script scales 2023 district‑level demand by predefined multipliers
(`TARGET_MULTIPLIERS`) for 2030, 2040 and 2050, joins the values with
`regional_supply_full_corrected.csv` and reports the surplus or deficit
per district. Results are written to `results/supply_demand_<year>.csv`.

## Adoption metrics and PyPSA integration

Running the stock–flow pipeline writes two supplementary tables used for
spatial analyses and PyPSA‑Earth:

* `results/buses.csv` – node metadata with `region`, `year`, `urban_hh` and
  `rural_hh` columns.
* `results/adoption_<scenario>.csv` – technology adoption shares and
  delivered energy by region and year.

Join these tables on `region` and `year` to annotate PyPSA buses. The
`pypsa_export` helper attaches the data directly to a loaded PyPSA
`Network`:

```python
import pypsa
import pypsa_export as pe
n = pypsa.Network("path/to/network.nc")
pe.attach_adoption_data(n, "bau", 2030)
```

The merged `network.buses` DataFrame then includes household counts and
adoption metrics for downstream energy system analyses.

## Reproducibility notes

* Both pipelines read the same demographic data file stored in the
  `data` folder. Ensure that `District‑level_Household_Projections.csv`
  is present; it should contain rows for `National` with household
  projections for 2030, 2040 and 2050.

* The stock–flow model updates the grid emission factor each decade
  according to the decarbonisation rate specified in
  `data_input.py` and propagates this into the emissions
  calculations.

* Technology names are case–insensitive. They are converted to
  lowercase and whitespace is replaced with underscores internally.

* If you wish to modify the adoption shares or add new scenarios,
  edit the `base_shares` dictionary in `technology_adoption_model.py`.

## Acknowledgements

This framework harmonises previously divergent stock–flow and cost
optimisation pipelines into a single, coherent codebase. It
incorporates fixes for parameter drift, unified technology lists and
scenario name normalisation and reads all household projections from a
single CSV. The readme provides a step‑by‑step guide to running both
models and verifying the outputs.

## Author

Created by [2kam](https://github.com/2kam).

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.

