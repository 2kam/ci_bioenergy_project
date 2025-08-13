
"""Global modelling configuration for CI bioenergy scenarios.

This module centralises scenario and evaluation year settings so
that all modelling pipelines use a consistent configuration.
"""

"""Shared configuration for modelling scenarios and years."""

from __future__ import annotations

from typing import List

# Scenarios to evaluate
SCENARIOS: List[str] = ["bau", "clean_push", "biogas_incentive"]

# Model years
YEARS: List[int] = [2030, 2040, 2050]
=======
# Default scenario names evaluated by the modelling pipelines
SCENARIOS: List[str] = ["bau", "clean_push", "biogas_incentive"]

# Default years evaluated by the modelling pipelines
YEARS: List[int] = [2030, 2040, 2050]

