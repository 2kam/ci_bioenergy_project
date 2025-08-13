"""Shared configuration for modelling scenarios and years."""
from __future__ import annotations

from typing import List

# Default scenario names evaluated by the modelling pipelines
SCENARIOS: List[str] = ["bau", "clean_push", "biogas_incentive"]

# Default years evaluated by the modelling pipelines
YEARS: List[int] = [2030, 2040, 2050]

