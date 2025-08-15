"""Utility helpers for locating data files."""

from pathlib import Path


def get_data_path(name: str) -> Path:
    """Return the path to a file in the ``data`` directory.

    The search first checks the repository's ``data`` directory (based on this
    file's location) and falls back to ``./data`` relative to the current working
    directory. This allows scripts to be executed from arbitrary locations
    while still resolving data files correctly.
    """

    repo_data = Path(__file__).resolve().parent / "data" / name
    if repo_data.exists():
        return repo_data
    return Path.cwd() / "data" / name

