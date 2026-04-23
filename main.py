"""CLI entrypoint.

Usage:
    python main.py --blob-name "sample_msa.pdf"
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from config import configure_logging, get_settings
from src.services import ContractIntelligencePipeline, DependencyContainer


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Contract Intelligence & Risk Scoring")
    p.add_argument("--blob-name", required=True, help="Blob name in the contracts container.")
    return p.parse_args()

def main() -> int:
    args = _parse_args()
    settings = get_settings()
    configure_logging(settings.log_level)

    container = DependencyContainer(settings)
    pipeline = ContractIntelligencePipeline(container.build_orchestrator())

    contract = pipeline.process(args.blob_name, title=" Contract: " + args.blob_name)

    # Print human-readable summary
    print("=" * 80)
    print(f"Contract ID : {contract.contract_id}")
    print(f"Stage       : {contract.stage.value}")
    print(f"Risk Level  : {contract.overall_risk_level}")
    print(f"Risk Score  : {contract.overall_risk_score}")
    print(f"Clauses     : {len(contract.clauses)}")
    print(f"Compliance  : "
        f"{sum(1 for f in contract.compliance_findings if f.passed)}"
        f"/{len(contract.compliance_findings)} rules passed")

    if contract.executive_summary:
        print("\nExecutive Summary:\n" + contract.executive_summary)

    if contract.error:
        print(f"\nERROR: {contract.error}", file=sys.stderr)
        sys.exit(1)

    # -------------------------------
    # Save JSON to Output folder
    # -------------------------------

    # Create Output directory if it doesn't exist
    output_dir = "Output"
    os.makedirs(output_dir, exist_ok=True)

    # Create a safe filename
    file_name = f"{contract.contract_id}.json"
    file_path = os.path.join(output_dir, file_name)

    # Write JSON to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(contract.model_dump(mode="json"), f, indent=2, default=str)

    print(f"\n✅ JSON saved to: {file_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
