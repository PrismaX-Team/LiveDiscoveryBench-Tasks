"""Read-only package checks. Never import or execute candidate task code."""

import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

TYPE_LABELS = {"type:new-task", "type:task-fix", "type:maintenance"}
METRIC_TYPES = {
    "linear_maximize", "linear_minimize", "log_ratio_maximize", "log_ratio_minimize",
    "upper_residual_log", "lower_residual_log", "power_maximize", "power_minimize",
    "monotone_piecewise_maximize", "monotone_piecewise_minimize", "custom", "raw_only",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_path(value):
    require(isinstance(value, str) and value and "\\" not in value, "Invalid relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(part not in ("", ".", "..") for part in value.split("/")),
            "Paths must be relative without empty, dot or parent segments")
    return path


def read_object(path):
    require(path.is_file() and not path.is_symlink(), f"Missing regular JSON file: {path}")
    require(0 < path.stat().st_size <= 1_000_000, f"JSON must be nonempty and at most 1 MB: {path}")
    def reject_constant(value):
        raise ValueError(f"Non-finite JSON number: {value}")
    value = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    require(isinstance(value, dict), f"Expected JSON object: {path}")
    return value


def check_package(root):
    require(not root.parent.is_symlink() and root.is_dir() and not root.is_symlink(),
            f"Missing or linked task directory: {root}")
    require({p.name for p in root.iterdir()} == {"instruction.json", "input", "environment", "verifier", "meta.json"},
            f"Expected exactly five top-level parts: {root}")
    # Reject links before reading JSON or following declared file paths.
    for path in root.rglob("*"):
        require(not path.is_symlink(), f"Symlink not allowed: {path}")
        require(path.is_file() or path.is_dir(), f"Special file not allowed: {path}")
    for name in ("input", "environment", "verifier"):
        require((root / name).is_dir(), f"Missing directory: {name}")
    for stage in ("validation", "test"):
        entry = root / "verifier" / stage / "run" / "main.py"
        require(entry.is_file() and entry.stat().st_size > 0, f"Missing nonempty entry: {entry}")
    require(not (root / "verifier/run/main.py").exists(), "Remove obsolete verifier/run/main.py")

    instruction = read_object(root / "instruction.json")
    require(set(instruction) == {"instructions", "input", "submission", "environment", "requirement", "limitation"},
            "instruction.json must use the current six fields (no objective/custom_environment)")
    require(isinstance(instruction["instructions"], str) and instruction["instructions"].strip(), "Empty instructions")
    for key in ("input", "environment", "requirement"):
        require(isinstance(instruction[key], list), f"{key} must be an array")
    require(all(isinstance(item, str) for item in instruction["requirement"]), "requirement must contain strings")
    require(isinstance(instruction["limitation"], dict), "limitation must be an object")
    submission = instruction["submission"]
    require(isinstance(submission, dict), "submission must be an object")
    artifacts = submission.get("artifacts")
    require(isinstance(artifacts, list) and artifacts, "At least one submission artifact is required")
    paths = set()
    for artifact in artifacts:
        require(isinstance(artifact, dict), "Artifact must be an object")
        path = relative_path(artifact.get("path"))
        require(str(path) not in paths, "Duplicate artifact path")
        paths.add(str(path))
        require(isinstance(artifact.get("format"), str) and artifact["format"], "Artifact format required")
        require(isinstance(artifact.get("description"), str) and artifact["description"], "Artifact description required")
        require("required" not in artifact, "Artifacts are always required; omit the required field")
        has_template = artifact.get("has_template", True)
        require(isinstance(has_template, bool), "has_template must be boolean")
        if has_template:
            require((root / "input" / path).is_file(), f"Missing input submission template: {path}")

    environment = read_object(root / "environment/environment.json")
    require(environment.get("schema_version") == "1.0", "environment schema_version must be 1.0")
    if environment.get("type") == "default":
        require(set(environment) == {"schema_version", "type"}, "Unexpected default environment fields")
        require({p.name for p in (root / "environment").iterdir()} == {"environment.json"},
                "Default environment may contain only environment.json")
    else:
        require(environment.get("type") == "containerfile", "Unknown environment type")
        path = relative_path(environment.get("containerfile"))
        file = root / "environment" / path
        require(file.is_file() and file.stat().st_size > 0, "Missing nonempty Containerfile")

    meta = read_object(root / "meta.json")
    for key in ("id", "title", "domain", "source_id"):
        require(isinstance(meta.get(key), str) and meta[key].strip(), f"Missing meta.{key}")
    require(re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", meta["id"]), "Invalid task ID")
    require(root.name == "_template" or meta["id"] == root.name, "Task ID must match directory")
    require(re.fullmatch(r"[a-z][a-z0-9+.-]*:[^\s]+", meta["source_id"]), "Invalid source_id namespace")
    require(isinstance(meta.get("data_sources"), list), "data_sources must be an array")
    metric = meta.get("metric")
    require(isinstance(metric, dict) and isinstance(metric.get("description"), str) and metric["description"].strip(),
            "Metric description required")
    require("type" in metric and (metric["type"] is None or isinstance(metric["type"], str) and metric["type"] in METRIC_TYPES),
            "Invalid metric.type")
    if metric["type"] not in (None, "raw_only"):
        require(isinstance(metric.get("transform"), dict), "Classified conversions require metric.transform")
    if metric["type"] == "custom":
        require((root / "verifier/matrix/transform.py").is_file(), "Custom conversion requires verifier/matrix/transform.py")


def classify_changes(paths, existing_tasks, labels):
    selected = TYPE_LABELS.intersection(labels)
    require(len(selected) == 1, "Maintainer must set exactly one type:new-task / type:task-fix / type:maintenance label")
    kind = next(iter(selected))
    tasks = {PurePosixPath(path).parts[1] for path in paths
             if len(PurePosixPath(path).parts) >= 2 and PurePosixPath(path).parts[0] == "tasks"
             and PurePosixPath(path).parts[1] != "_template"}
    if kind == "type:maintenance":
        require(tasks <= existing_tasks, "Maintenance cannot introduce new tasks")
    else:
        require(len(tasks) == 1, "New-task/fix PR must change exactly one task")
        task = next(iter(tasks))
        require(all(path.startswith(f"tasks/{task}/") for path in paths),
                "Separate task contributions from repository maintenance")
        require((task not in existing_tasks) == (kind == "type:new-task"), "PR type does not match new/existing task")
    if any(path.startswith("tasks/_template/") for path in paths):
        tasks.add("_template")
    return tasks


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args]).decode("utf-8")


def main():
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    base = os.environ.get("BASE_SHA", "")
    if base:
        require(re.fullmatch(r"[a-f0-9]{40,64}", base), "Invalid base SHA")
        event = read_object(Path(os.environ["GITHUB_EVENT_PATH"]))
        labels = {item["name"] for item in event["pull_request"]["labels"]}
        paths = git(repo, "diff", "--no-renames", "--name-only", "-z", base, "HEAD", "--").strip("\0").split("\0")
        paths = [path for path in paths if path]
        existing = set(git(repo, "ls-tree", "--name-only", "-d", base + ":tasks").splitlines())
        tasks = classify_changes(paths, existing, labels)
    else:
        require(not (repo / "tasks").is_symlink(), "Linked tasks directory")
        tasks = {path.name for path in (repo / "tasks").iterdir()}
    for task in sorted(tasks):
        check_package(repo / "tasks" / task)
        print(f"Structure passed: tasks/{task}")
    print("Read-only checks passed. Approval, identity, scientific validity and runtime remain manual review.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"Task structure check failed: {error}", file=sys.stderr)
        sys.exit(1)
