from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


STATE_KEY = "protein_stability_campaign"
REQUIRED_QUERY_FIELDS = {
    "episode_id",
    "rank",
    "variant_id",
    "pred_ddg",
    "pred_uncertainty",
    "acquisition_type",
}


class CampaignRequestError(ValueError):
    pass


def load_config(verifier_root: Path) -> dict[str, Any]:
    value = json.loads(
        (verifier_root / "validation" / "config.json").read_text(encoding="utf-8")
    )
    required = {
        "schema_version",
        "round_count",
        "episode_count",
        "batch_size_per_episode",
        "batch_size_total",
        "valid_acquisition_types",
    }
    if not isinstance(value, dict) or set(value) != required or value["schema_version"] != "1.0":
        raise RuntimeError("validation/config.json has an invalid contract")
    if int(value["round_count"]) < 1 or int(value["episode_count"]) < 1:
        raise RuntimeError("validation round and episode counts must be positive")
    if int(value["batch_size_per_episode"]) * int(value["episode_count"]) != int(
        value["batch_size_total"]
    ):
        raise RuntimeError("validation batch totals are inconsistent")
    if not value["valid_acquisition_types"] or len(set(value["valid_acquisition_types"])) != len(
        value["valid_acquisition_types"]
    ):
        raise RuntimeError("validation acquisition types are invalid")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file() or path.is_symlink():
        raise CampaignRequestError("missing or unsafe CSV: %s" % path.name)
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        {str(key): str(value).strip() for key, value in row.items() if key is not None}
        for row in rows
    ]


def load_design(input_root: Path) -> dict[str, dict[str, str]]:
    try:
        rows = read_csv(input_root / "data" / "design_space.csv")
    except CampaignRequestError as error:
        raise RuntimeError("public design space is missing or unsafe") from error
    by_id = {row.get("variant_id", ""): row for row in rows}
    if len(rows) != 3953 or len(by_id) != len(rows) or "" in by_id:
        raise RuntimeError("public design space identity is invalid")
    return by_id


def load_observations(verifier_root: Path) -> dict[str, dict[str, str]]:
    try:
        rows = read_csv(verifier_root / "target_study" / "oracle_observations.csv")
    except CampaignRequestError as error:
        raise RuntimeError("hidden observation table is missing or unsafe") from error
    by_id = {row.get("variant_id", ""): row for row in rows}
    if len(rows) != 3953 or len(by_id) != len(rows) or "" in by_id:
        raise RuntimeError("hidden observation table identity is invalid")
    return by_id


def finite(value: Any, label: str) -> float:
    try:
        selected = float(value)
    except (TypeError, ValueError) as error:
        raise CampaignRequestError("%s must be numeric" % label) from error
    if not math.isfinite(selected):
        raise CampaignRequestError("%s must be finite" % label)
    return selected


def normalize_queries(
    round_id: int,
    values: Any,
    design: dict[str, dict[str, str]],
    prior_ids: set[str],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    if not isinstance(values, list) or len(values) != int(config["batch_size_total"]):
        raise CampaignRequestError(
            "round %d must contain exactly %d queries"
            % (round_id, int(config["batch_size_total"]))
        )
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    ranks: dict[str, set[int]] = {}
    valid_acquisition_types = set(str(item) for item in config["valid_acquisition_types"])
    for index, value in enumerate(values, start=1):
        if not isinstance(value, dict) or not REQUIRED_QUERY_FIELDS.issubset(value):
            raise CampaignRequestError("query %d lacks required fields" % index)
        episode_id = str(value["episode_id"]).strip()
        variant_id = str(value["variant_id"]).strip()
        design_row = design.get(variant_id)
        if design_row is None or design_row.get("episode_id") != episode_id:
            raise CampaignRequestError("query %d has an invalid episode/variant pair" % index)
        if variant_id in seen or variant_id in prior_ids:
            raise CampaignRequestError("query %d repeats a variant" % index)
        rank_value = finite(value["rank"], "query %d rank" % index)
        prediction = finite(value["pred_ddg"], "query %d pred_ddg" % index)
        uncertainty = finite(
            value["pred_uncertainty"], "query %d pred_uncertainty" % index
        )
        if not rank_value.is_integer() or uncertainty < 0:
            raise CampaignRequestError("query %d has an invalid rank or uncertainty" % index)
        rank = int(rank_value)
        acquisition_type = str(value["acquisition_type"]).strip()
        if acquisition_type not in valid_acquisition_types:
            raise CampaignRequestError("query %d has an invalid acquisition_type" % index)
        normalized = {
            "episode_id": episode_id,
            "rank": rank,
            "variant_id": variant_id,
            "pred_ddg": prediction,
            "pred_uncertainty": uncertainty,
            "acquisition_type": acquisition_type,
            "rationale": str(value.get("rationale", "")).strip(),
        }
        output.append(normalized)
        seen.add(variant_id)
        counts[episode_id] += 1
        ranks.setdefault(episode_id, set()).add(rank)
    episode_count = int(config["episode_count"])
    per_episode = int(config["batch_size_per_episode"])
    if len(counts) != episode_count or set(counts.values()) != {per_episode}:
        raise CampaignRequestError(
            "round %d must contain %d rows for each of %d episodes"
            % (round_id, per_episode, episode_count)
        )
    expected_ranks = set(range(1, per_episode + 1))
    if any(value != expected_ranks for value in ranks.values()):
        raise CampaignRequestError(
            "round %d ranks must be exactly 1 through %d per episode"
            % (round_id, per_episode)
        )
    return output


def initial_state() -> dict[str, Any]:
    return {"schema_version": "1.0", "accepted_rounds": [], "queried_variant_ids": []}


def validate_state(value: Any, config: dict[str, Any]) -> dict[str, Any]:
    if value is None:
        return initial_state()
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "accepted_rounds",
        "queried_variant_ids",
    }:
        raise RuntimeError("VerifyContext campaign state is malformed")
    if value["schema_version"] != "1.0" or not isinstance(value["accepted_rounds"], list):
        raise RuntimeError("VerifyContext campaign state has an invalid version")
    if len(value["accepted_rounds"]) > int(config["round_count"]):
        raise RuntimeError("VerifyContext campaign state exceeds its scientific budget")
    queried = value["queried_variant_ids"]
    if not isinstance(queried, list) or len(queried) != len(set(queried)):
        raise RuntimeError("VerifyContext campaign query history is malformed")
    return value


def make_results(
    round_id: int,
    queries: list[dict[str, Any]],
    observations: dict[str, dict[str, str]],
    prior_total: int,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    results = []
    batch_total = int(config["batch_size_total"])
    overall_total = batch_total * int(config["round_count"])
    for ordinal, query in enumerate(queries, start=1):
        hidden = observations[query["variant_id"]]
        if str(hidden.get("eligible_for_final_batch", "")).casefold() != "true":
            raise CampaignRequestError("selected variant is not eligible for this campaign")
        result = {
            **query,
            "round": round_id,
            "server_batch_id": "round_%d" % round_id,
            "status": "ok",
            "accepted": True,
            "charged": True,
            "mutation": hidden["mutation"],
            "position": int(hidden["position"]),
            "wt_aa": hidden["wt_aa"],
            "mut_aa": hidden["mut_aa"],
            "region": hidden["region"],
            "measured_ddg": float(hidden["measured_ddg"]),
            "assay_sd": float(hidden["assay_sd"]),
            "qc_status": hidden["qc_status"],
            "is_stabilizing": float(hidden["measured_ddg"]) < 0,
            "remaining_episode_round_budget": 0,
            "remaining_round_budget": batch_total - ordinal,
            "remaining_total_budget": overall_total - prior_total - ordinal,
        }
        results.append(result)
    return results


def process_validation(
    request: Any,
    input_root: Path,
    verifier_root: Path,
    current_state: Any,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    config = load_config(verifier_root)
    state = validate_state(current_state, config)
    if not isinstance(request, dict) or set(request) != {"round", "queries"}:
        raise CampaignRequestError("validation request must contain only round and queries")
    expected_round = len(state["accepted_rounds"]) + 1
    if expected_round > int(config["round_count"]):
        raise CampaignRequestError("no validation rounds remain")
    try:
        round_id = int(request["round"])
    except (TypeError, ValueError) as error:
        raise CampaignRequestError("round must be an integer") from error
    if round_id != expected_round:
        raise CampaignRequestError("the next accepted validation round must be %d" % expected_round)
    design = load_design(input_root)
    observations = load_observations(verifier_root)
    if set(observations) != set(design):
        raise RuntimeError("hidden observations do not match the public design space")
    prior_ids = set(str(item) for item in state["queried_variant_ids"])
    queries = normalize_queries(round_id, request["queries"], design, prior_ids, config)
    results = make_results(round_id, queries, observations, len(prior_ids), config)
    next_state = {
        "schema_version": "1.0",
        "accepted_rounds": list(state["accepted_rounds"])
        + [{"round": round_id, "queries": queries, "results": results}],
        "queried_variant_ids": list(state["queried_variant_ids"])
        + [item["variant_id"] for item in queries],
    }
    return {
        "status": "ok",
        "round": round_id,
        "server_batch_id": "round_%d" % round_id,
        "results": results,
    }, next_state
