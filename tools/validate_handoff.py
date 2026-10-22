#!/usr/bin/env python3
"""Dependency-free structural validator for HFAI handoff v1."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED = {
    "schema_version", "project_id", "source_platform", "conversation_reference",
    "objective", "decisions", "task_status", "artifacts", "test_results",
    "next_actions", "permissions", "timestamp",
}
STATUSES = {"not_started", "in_progress", "blocked", "complete", "unknown"}
TEST_STATUSES = {"passed", "failed", "not_run", "blocked"}
SHARING = {"private", "explicit_recipients", "public"}
EXECUTION = {"none", "local_approved", "scoped_approved"}
HEX64 = re.compile(r"^[a-fA-F0-9]{64}$")


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["root must be a JSON object"]
    missing = REQUIRED - data.keys()
    extra = data.keys() - (REQUIRED | {"metadata"})
    if missing:
        errors.append("missing required fields: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("unknown top-level fields: " + ", ".join(sorted(extra)))
    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version must equal '1.0.0'")
    for key in ("project_id", "source_platform", "objective"):
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            errors.append(f"{key} must be a non-empty string")
    ref = data.get("conversation_reference")
    if ref is not None and not isinstance(ref, str):
        errors.append("conversation_reference must be a string or null")
    if isinstance(ref, str) and len(ref) > 2048:
        errors.append("conversation_reference exceeds 2048 characters")
    if data.get("task_status") not in STATUSES:
        errors.append("task_status is invalid")
    for key in ("decisions", "artifacts", "test_results", "next_actions"):
        if key in data and not isinstance(data[key], list):
            errors.append(f"{key} must be an array")
    if isinstance(data.get("decisions"), list) and any(not isinstance(x, str) for x in data["decisions"]):
        errors.append("decisions items must be strings")
    if isinstance(data.get("next_actions"), list) and any(not isinstance(x, str) or not x.strip() for x in data["next_actions"]):
        errors.append("next_actions items must be non-empty strings")
    if isinstance(data.get("artifacts"), list):
        for i, item in enumerate(data["artifacts"]):
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"].strip() or not isinstance(item.get("reference"), str) or not item["reference"].strip():
                errors.append(f"artifacts[{i}] requires non-empty name and reference")
                continue
            if set(item) - {"name", "reference", "media_type", "sha256"}:
                errors.append(f"artifacts[{i}] has unknown fields")
            if "sha256" in item and (not isinstance(item["sha256"], str) or not HEX64.fullmatch(item["sha256"])):
                errors.append(f"artifacts[{i}].sha256 must be 64 hexadecimal characters")
    if isinstance(data.get("test_results"), list):
        for i, item in enumerate(data["test_results"]):
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or item.get("status") not in TEST_STATUSES:
                errors.append(f"test_results[{i}] requires name and a valid status")
                continue
            if set(item) - {"name", "status", "evidence"}:
                errors.append(f"test_results[{i}] has unknown fields")
    p = data.get("permissions")
    if not isinstance(p, dict):
        errors.append("permissions must be an object")
    else:
        if set(p) != {"sharing", "external_fetch", "execution"}:
            errors.append("permissions must contain only sharing, external_fetch, execution")
        if p.get("sharing") not in SHARING:
            errors.append("permissions.sharing is invalid")
        if not isinstance(p.get("external_fetch"), bool):
            errors.append("permissions.external_fetch must be boolean")
        if p.get("execution") not in EXECUTION:
            errors.append("permissions.execution is invalid")
    ts = data.get("timestamp")
    if not isinstance(ts, str):
        errors.append("timestamp must be an ISO-8601 date-time string")
    else:
        try:
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                errors.append("timestamp must include a timezone")
        except ValueError:
            errors.append("timestamp must be a valid ISO-8601 date-time string")
    if "metadata" in data and not isinstance(data["metadata"], dict):
        errors.append("metadata must be an object")
    return errors


def main(argv):
    if len(argv) != 2:
        print(f"Usage: {Path(argv[0]).name} <handoff.json>", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS: HFAI handoff structure is valid (v1.0.0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
