#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from science_innovation_exam.verify_context import VerifyContext


VERIFIER_ROOT = Path(__file__).resolve().parents[2]
if str(VERIFIER_ROOT) not in sys.path:
    sys.path.insert(0, str(VERIFIER_ROOT))

from campaign_contract import (  # noqa: E402
    CampaignRequestError,
    STATE_KEY,
    load_config,
    load_observations,
    validate_state,
)
from final_score import (  # noqa: E402
    FinalScoreError,
    invalid_result,
    load_score_config,
    public_result,
    score_final_candidates,
)


class SubmissionError(ValueError):
    pass


def measured_ids_from_state(state: dict[str, Any], config: dict[str, Any]) -> set[str]:
    # Official measurement history is the locked validation Context, not the
    # submitted round CSVs. Those files are required artifacts, not a replay lock.
    if len(state["accepted_rounds"]) != int(config["round_count"]):
        raise SubmissionError("all three validation rounds must be completed before test")
    prior_ids: set[str] = set()
    for expected_round, record in enumerate(state["accepted_rounds"], start=1):
        if not isinstance(record, dict) or record.get("round") != expected_round:
            raise SubmissionError("trusted validation history is malformed")
        queries = record.get("queries")
        results = record.get("results")
        if not isinstance(queries, list) or not isinstance(results, list):
            raise SubmissionError("trusted validation history is incomplete")
        for query in queries:
            variant_id = str(query.get("variant_id", ""))
            if not variant_id or variant_id in prior_ids:
                raise SubmissionError("trusted validation history is malformed")
            prior_ids.add(variant_id)
    if prior_ids != set(str(item) for item in state["queried_variant_ids"]):
        raise SubmissionError("trusted validation query index is inconsistent")
    return prior_ids


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def score(input_root: Path, submission_root: Path) -> dict[str, Any]:
    del input_root
    campaign_config = load_config(VERIFIER_ROOT)
    score_config = load_score_config(VERIFIER_ROOT)
    state = validate_state(VerifyContext.current().get(STATE_KEY), campaign_config)
    measured_ids = measured_ids_from_state(state, campaign_config)
    observations = load_observations(VERIFIER_ROOT)
    details = score_final_candidates(submission_root, observations, measured_ids, score_config)
    return details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    result_path = args.result.resolve()
    score_config = None
    try:
        score_config = load_score_config(VERIFIER_ROOT)
        details = score(args.input.resolve(), args.submission.resolve())
        result = public_result(details)
        log_payload = {
            "phase": "test",
            "valid": result["valid"],
            "primary_metric": result["primary_metric"],
            "metrics": result["metrics"],
            "error": result["error"],
            "diagnostics": details.get("diagnostics"),
        }
    except (SubmissionError, CampaignRequestError, FinalScoreError) as error:
        result = invalid_result(str(error), score_config)
        log_payload = {
            "phase": "test",
            "valid": result["valid"],
            "primary_metric": result["primary_metric"],
            "metrics": result["metrics"],
            "error": result["error"],
        }
    VerifyContext.current().log(log_payload)
    atomic_json(result_path, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
