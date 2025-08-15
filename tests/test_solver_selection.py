import pathlib
import sys
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import model

pulp = model.pulp

@pytest.mark.skipif(pulp is None, reason="PuLP not installed")
def test_run_cost_minimise_cost_cbc():
    tech_costs = {
        "firewood": 2,
        "charcoal": 3,
        "biogas": 1,
        "ethanol": 4,
        "electricity": 5,
        "lpg": 6,
        "improved_biomass": 2,
    }
    df, cost = model.run_cost_minimise_cost(
        2025, "reg", 10, 0, 1, tech_costs, solver="cbc"
    )
    assert pytest.approx(df["Energy_GJ"].sum()) == 10
    assert cost >= 0

@pytest.mark.skipif(pulp is None, reason="PuLP not installed")
def test_run_cost_minimise_cost_glpk():
    tech_costs = {
        "firewood": 2,
        "charcoal": 3,
        "biogas": 1,
        "ethanol": 4,
        "electricity": 5,
        "lpg": 6,
        "improved_biomass": 2,
    }
    if pulp.GLPK_CMD().available():
        df, _ = model.run_cost_minimise_cost(
            2025, "reg", 10, 0, 1, tech_costs, solver="glpk"
        )
        assert pytest.approx(df["Energy_GJ"].sum()) == 10
    else:
        with pytest.raises(RuntimeError):
            model.run_cost_minimise_cost(
                2025, "reg", 10, 0, 1, tech_costs, solver="glpk"
            )
