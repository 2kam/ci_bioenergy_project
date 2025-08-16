"""Configuration utilities for CI bioenergy scenarios.

Configuration defaults are stored in ``config/scenarios.yaml``.
``load_config`` returns the parsed dictionary and can handle YAML or JSON
files.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

# Default configuration shipped with the repository
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "config", "scenarios.yaml"
)


def load_config(path: str | None = None) -> Dict[str, Any]:
    """Load scenario configuration from a YAML or JSON file.

    Parameters
    ----------
    path : str, optional
        Path to the configuration file. If omitted, ``DEFAULT_CONFIG_PATH``
        is used.

    Returns
    -------
    dict
        Parsed configuration dictionary.
    """
    cfg_path = path or DEFAULT_CONFIG_PATH
    with open(cfg_path, "r", encoding="utf-8") as fh:
        if cfg_path.endswith(('.yaml', '.yml')):
            if yaml is None:
                raise RuntimeError(
                    "PyYAML is required to read YAML configuration files."
                )
            return yaml.safe_load(fh)
        if cfg_path.endswith('.json'):
            return json.load(fh)
        raise ValueError(f"Unsupported config format: {cfg_path}")


# Eagerly load default configuration for convenience
CONFIG = load_config()
