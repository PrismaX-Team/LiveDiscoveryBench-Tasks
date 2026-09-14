#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from science_innovation_exam.verify_context import VerifyContext


VERIFIER_ROOT = Path(__file__).resolve().parents[2]
if str(VERIFIER_ROOT) not in sys.path:
    sys.path.insert(0, str(VERIFIER_ROOT))

from campaign_contract import CampaignRequestError, STATE_KEY, process_validation  # noqa: E402


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"))
        context = VerifyContext.current()
        response, next_state = process_validation(
            request,
            args.input.resolve(),
            VERIFIER_ROOT,
            context.get(STATE_KEY),
        )
        # This is the only scientific-budget mutation. Rejected requests never
        # reach it, so they do not consume an accepted validation round.
        context[STATE_KEY] = next_state
        measurements = [float(row["measured_ddg"]) for row in response["results"]]
        context.log({
            "round": response["round"],
            "measured_count": len(measurements),
            "mean_ddg": sum(measurements) / len(measurements),
            "stabilizing_fraction": sum(value < 0 for value in measurements) / len(measurements),
        })
    except (CampaignRequestError, json.JSONDecodeError) as error:
        response = {"status": "error", "error": str(error), "results": []}
    atomic_json(args.response.resolve(), response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
