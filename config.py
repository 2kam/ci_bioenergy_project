"""Global modelling configuration for CI bioenergy scenarios.

This module centralises scenario and evaluation year settings so
that all modelling pipelines use a consistent configuration.

Shared configuration for modelling scenarios and years.
"""
from __future__ import annotations

from typing import List

# Scenarios to evaluate
SCENARIOS: List[str] = ["bau", "clean_push", "biogas_incentive"]

# Model years
YEARS: List[int] = [2030, 2040, 2050]

# Policy constraints for optimisation
# Minimum share of clean technologies (fraction of total demand)
MIN_CLEAN_SHARE: float = 0.4
# Maximum share of traditional firewood (fraction of total demand)
MAX_FIREWOOD_SHARE: float = 0.3

