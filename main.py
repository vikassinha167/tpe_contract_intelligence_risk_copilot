"""CLI entrypoint.

Usage:
    python main.py --blob-name "sample_msa.pdf"
"""
from __future__ import annotations

import argparse
import json
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

    contract = pipeline.process(args.blob_name, title=args.title)

    # Print a concise human-readable result + a JSON dump for tooling.
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
        return 1

    # Full JSON to stdout for downstream consumers
    print("\n--- JSON ---")
    print(json.dumps(contract.model_dump(mode="json"), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
