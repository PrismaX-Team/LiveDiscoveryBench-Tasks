"""Single hidden-label score: mean measured_ddg of the configured final panel."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from campaign_contract import CampaignRequestError, finite, read_csv


TASK_ID = "protein_stability_campaign"
ALLOWED_PANELS = ("validated", "prospective")
# Used only when the score config itself cannot be read. Lower is better for this
# metric, so an invalid submission must never report a small, good-looking number.
INVALID_RAW_FALLBACK = 999.0


class FinalScoreError(ValueError):
    pass


def load_score_config(verifier_root: Path) -> dict[str, Any]:
    path = verifier_root / "test" / "data" / "score_config.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "task_id",
        "primary_metric_name",
        "direction",
        "aggregation",
        "hidden_label_field",
        "invalid_raw_value",
        "scored_panels",
        "panels",
        "required_nonempty_artifacts",
        "notes",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise RuntimeError("test/data/score_config.json has an invalid contract")
    if value["schema_version"] != "1.0" or value["task_id"] != TASK_ID:
        raise RuntimeError("score config identity is invalid")
    if value["direction"] != "minimize" or value["aggregation"] != "unweighted_mean":
        raise RuntimeError("score config aggregation contract is invalid")
    if value["hidden_label_field"] != "measured_ddg":
        raise RuntimeError("score config must read hidden measured_ddg")
    invalid_raw = value["invalid_raw_value"]
    if isinstance(invalid_raw, bool) or not isinstance(invalid_raw, (int, float)):
        raise RuntimeError("invalid_raw_value must be a number")
    if not math.isfinite(invalid_raw) or invalid_raw <= 0:
        raise RuntimeError("invalid_raw_value must be a finite worst-case placeholder")
    scored = value["scored_panels"]
    if not isinstance(scored, list) or not scored or len(set(scored)) != len(scored):
        raise RuntimeError("scored_panels must be a non-empty unique list")
    if any(item not in ALLOWED_PANELS for item in scored):
        raise RuntimeError("scored_panels contains an unknown panel")
    panels = value["panels"]
    if not isinstance(panels, dict) or set(panels) != set(ALLOWED_PANELS):
        raise RuntimeError("score config panels are incomplete")
    artifacts = value["required_nonempty_artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise RuntimeError("required_nonempty_artifacts is invalid")
    return value


def load_hidden_labels(observations: dict[str, dict[str, str]]) -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    for variant_id, row in observations.items():
        measured = float(row["measured_ddg"])
        if not math.isfinite(measured):
            raise RuntimeError("hidden measured_ddg must be finite")
        labels[variant_id] = {
            "episode_id": str(row["episode_id"]).strip(),
            "variant_id": variant_id,
            "measured_ddg": measured,
            "eligible": str(row.get("eligible_for_final_batch", "")).casefold() == "true",
        }
    if not labels:
        raise RuntimeError("hidden observation table is empty")
    return labels


def require_nonempty_artifacts(submission_root: Path, artifacts: list[str]) -> None:
    for relative in artifacts:
        path = submission_root / relative
        if path.is_symlink() or not path.is_file() or path.stat().st_size <= 0:
            raise FinalScoreError("missing or empty required artifact: %s" % relative)


def parse_final_panel(
    submission_root: Path,
    panel_name: str,
    panel: dict[str, Any],
    labels: dict[str, dict[str, Any]],
    measured_ids: set[str],
    episode_ids: list[str],
) -> list[dict[str, Any]]:
    rows = read_csv(submission_root / str(panel["path"]))
    required = set(panel["required_columns"])
    if not rows or not required.issubset(rows[0]):
        raise FinalScoreError("%s panel is missing required columns" % panel_name)
    expected = int(panel["per_episode"])
    must_be_measured = bool(panel["must_be_measured"])
    selected: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_by_episode: dict[str, set[str]] = defaultdict(set)
    ranks_by_episode: dict[str, set[int]] = defaultdict(set)
    for index, row in enumerate(rows, start=1):
        episode_id = str(row.get("episode_id", "")).strip()
        variant_id = str(row.get("variant_id", "")).strip()
        label = labels.get(variant_id)
        rank_value = finite(row.get("rank"), "%s row %d rank" % (panel_name, index))
        if not rank_value.is_integer():
            raise FinalScoreError("%s row %d has a non-integer rank" % (panel_name, index))
        rank = int(rank_value)
        if "pred_ddg" in required:
            finite(row.get("pred_ddg"), "%s row %d pred_ddg" % (panel_name, index))
            uncertainty = finite(
                row.get("pred_uncertainty"),
                "%s row %d pred_uncertainty" % (panel_name, index),
            )
            if uncertainty < 0:
                raise FinalScoreError("%s row %d has a negative uncertainty" % (panel_name, index))
        measured_ok = (variant_id in measured_ids) if must_be_measured else (variant_id not in measured_ids)
        if (
            label is None
            or label["episode_id"] != episode_id
            or not label["eligible"]
            or not measured_ok
            or variant_id in seen_by_episode[episode_id]
            or not 1 <= rank <= expected
            or rank in ranks_by_episode[episode_id]
        ):
            raise FinalScoreError("%s row %d is not a valid unique final candidate" % (panel_name, index))
        selected[episode_id].append({"episode_id": episode_id, "variant_id": variant_id, "measured_ddg": label["measured_ddg"]})
        seen_by_episode[episode_id].add(variant_id)
        ranks_by_episode[episode_id].add(rank)
    for episode_id in episode_ids:
        if len(selected.get(episode_id, [])) != expected:
            raise FinalScoreError(
                "%s must contain exactly %d rows for %s"
                % (panel_name, expected, episode_id)
            )
        if ranks_by_episode.get(episode_id) != set(range(1, expected + 1)):
            raise FinalScoreError("%s ranks for %s must be 1 through %d" % (panel_name, episode_id, expected))
    if len(rows) != expected * len(episode_ids):
        raise FinalScoreError("%s has extra rows" % panel_name)
    ordered: list[dict[str, Any]] = []
    for episode_id in episode_ids:
        ordered.extend(selected[episode_id])
    return ordered


def mean_ddg(rows: list[dict[str, Any]]) -> float:
    if not rows:
        raise FinalScoreError("scored final panel is empty")
    values = [float(row["measured_ddg"]) for row in rows]
    if not all(math.isfinite(value) for value in values):
        raise FinalScoreError("scored hidden labels are not finite")
    return sum(values) / len(values)


def stabilizing_fraction(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return sum(float(row["measured_ddg"]) < 0 for row in rows) / len(rows)


def score_final_candidates(
    submission_root: Path,
    observations: dict[str, dict[str, str]],
    measured_ids: set[str],
    config: dict[str, Any],
) -> dict[str, Any]:
    require_nonempty_artifacts(submission_root, [str(item) for item in config["required_nonempty_artifacts"]])
    labels = load_hidden_labels(observations)
    episode_ids = sorted({item["episode_id"] for item in labels.values()})
    panels: dict[str, list[dict[str, Any]]] = {}
    for name, panel in config["panels"].items():
        panels[name] = parse_final_panel(
            submission_root,
            name,
            panel,
            labels,
            measured_ids,
            episode_ids,
        )
    scored_rows: list[dict[str, Any]] = []
    for name in config["scored_panels"]:
        scored_rows.extend(panels[name])
    primary = mean_ddg(scored_rows)
    diagnostics = {
        "scored_panels": list(config["scored_panels"]),
        "scored_count": len(scored_rows),
        "mean_final_ddg": primary,
        "stabilizing_fraction": stabilizing_fraction(scored_rows),
        "validated_mean_ddg": mean_ddg(panels["validated"]),
        "validated_stabilizing_fraction": stabilizing_fraction(panels["validated"]),
        "prospective_mean_ddg": mean_ddg(panels["prospective"]),
        "prospective_stabilizing_fraction": stabilizing_fraction(panels["prospective"]),
    }
    return {
        "schema_version": "1.0",
        "task_id": TASK_ID,
        "valid": True,
        "status": "valid",
        "primary_metric": {
            "name": str(config["primary_metric_name"]),
            "value": primary,
            "direction": str(config["direction"]),
        },
        "metrics": [
            {"name": str(config["primary_metric_name"]), "value": primary, "unit": "ddg"},
            {"name": "scored_count", "value": float(len(scored_rows)), "unit": "count"},
            {"name": "stabilizing_fraction", "value": diagnostics["stabilizing_fraction"], "unit": None},
            {"name": "validated_mean_ddg", "value": diagnostics["validated_mean_ddg"], "unit": "ddg"},
            {"name": "validated_stabilizing_fraction", "value": diagnostics["validated_stabilizing_fraction"], "unit": None},
            {"name": "prospective_mean_ddg", "value": diagnostics["prospective_mean_ddg"], "unit": "ddg"},
            {"name": "prospective_stabilizing_fraction", "value": diagnostics["prospective_stabilizing_fraction"], "unit": None},
        ],
        "error": None,
        "diagnostics": diagnostics,
    }


def invalid_result(message: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
    name = "mean_final_ddg"
    direction = "minimize"
    placeholder = INVALID_RAW_FALLBACK
    if config is not None:
        name = str(config["primary_metric_name"])
        direction = str(config["direction"])
        placeholder = float(config["invalid_raw_value"])
    # An invalid result is never ranked; `valid` is the authoritative flag. The
    # placeholder is still far worse than any achievable mean so that a reader who
    # only looks at the number cannot mistake a rejected submission for a good one.
    return {
        "schema_version": "1.0",
        "task_id": TASK_ID,
        "valid": False,
        "status": "invalid",
        "primary_metric": {"name": name, "value": placeholder, "direction": direction},
        "metrics": [{"name": name, "value": placeholder, "unit": "ddg"}],
        "error": message,
    }


def public_result(details: dict[str, Any]) -> dict[str, Any]:
    return {key: details[key] for key in (
        "schema_version",
        "task_id",
        "valid",
        "status",
        "primary_metric",
        "metrics",
        "error",
    )}
