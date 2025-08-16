"""Build a lightweight report summarising methodology and data lineage."""

from __future__ import annotations

import json
import os
from glob import glob


def gather_metadata(results_dir: str = "results") -> list[tuple[str, str, dict]]:
    """Return list of tuples ``(stage, data_file, metadata)``."""

    records = []
    stages = ["demand", "adoption", "cost", "supply_comparison"]
    for stage in stages:
        stage_dir = os.path.join(results_dir, stage)
        if not os.path.isdir(stage_dir):
            continue
        for meta_path in glob(os.path.join(stage_dir, "*_metadata.json")):
            with open(meta_path) as f:
                meta = json.load(f)
            data_file = os.path.basename(meta_path).replace("_metadata.json", "")
            records.append((stage, data_file, meta))
    return records


def build_report(output_path: str = os.path.join("docs", "report.md")) -> None:
    """Generate a Markdown report from collected metadata."""

    meta_records = gather_metadata()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    lines = ["# Methodology and Data Lineage", ""]
    for stage, data_file, meta in meta_records:
        lines.append(f"## {stage.replace('_', ' ').title()} – {data_file}")
        lines.append(f"- Timestamp: {meta.get('timestamp', 'n/a')}")
        params = meta.get("parameters", {})
        if params:
            lines.append("- Parameters:")
            for key, value in params.items():
                lines.append(f"  - {key}: {value}")
        lines.append("")
    with open(output_path, "w") as fh:
        fh.write("\n".join(lines))
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    build_report()

