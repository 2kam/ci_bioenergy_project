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
* The only required Python package is **pandas**. The cost pipeline can
  optionally solve a least‑cost optimisation using **PuLP**. Install it
  with `pip install pulp` if you intend to run the optimisation mode.

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
   # or solve an optimisation with policy constraints (requires PuLP)
   python main.py cost --optimise
   ```

   The results will be saved to `results/ci_bioenergy_techpathways.xlsx`.
   The workbook includes a `Details` sheet with cost breakdowns by
   technology and a `Summary` sheet with total costs by scenario and
   year. When optimisation is enabled, policy constraints for the
   minimum clean share and maximum firewood share are taken from
   `config.py`.

   Append ``--pypsa-export`` to additionally produce CSV files
   compatible with `PyPSA‑Earth <https://pypsa-earth.readthedocs.io/>`_:

   ```bash
   python main.py cost --pypsa-export
   ```

   For each scenario and year, the command writes
   ``results/pypsa/<scenario>/<year>/load.csv`` and
   ``generators.csv``. ``load.csv`` contains regional
   cooking‑electricity demand while ``generators.csv`` provides
   dispatchable biomass, biogas and LPG supply.

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

## Exporting to PyPSA‑Earth

The CSVs generated with ``--pypsa-export`` can be referenced from a
PyPSA‑Earth configuration to include clean‑cooking demand and fuel
supplies. Example snippet:

```yaml
custom_data:
  load: results/pypsa/bau/2030/load.csv
  generators: results/pypsa/bau/2030/generators.csv
```

Adjust the paths, scenario (``bau``) and year (``2030``) as needed for
your analysis.

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

## Hourly demand with ERA5

Hourly demand profiles can be derived from ERA5 reanalysis data. Use
[atlite](https://github.com/PyPSA/atlite) to prepare a cutout covering
Côte d'Ivoire and store the resulting NetCDF file under
``data/era5/``::

    import atlite
    cutout = atlite.Cutout(
        path="data/era5/civ-2019.nc",
        module="era5",
        x=slice(-8.5, -2.5),
        y=slice(4, 11),
        time="2019",
    )
    cutout.write()

The :mod:`era5_profiles` module loads these cutouts and exposes
:func:`era5_profiles.load_era5_series` for extracting hourly variables.
Annual demand values can be distributed to an hourly series by weighting
with the ERA5-derived profile::

    from energy_demand_model import disaggregate_to_hourly
    hourly = disaggregate_to_hourly(
        annual_gj,
        "data/era5/civ-2019.nc",
        "t2m",
        region_geom,
    )

The returned series contains hourly demand in gigajoules indexed by
UTC timestamps.

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

