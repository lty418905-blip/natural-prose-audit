#!/usr/bin/env python3
"""Validate a bounded life-event library call chain without external dependencies."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


STATUSES = {
    "DRAFT",
    "READY",
    "ADOPTED",
    "REJECTED_OR_MERGED",
    "REVIEW_FLAG",
    "NOT_USED",
}
DISPOSITIONS = {"ADOPTED", "REJECTED_OR_MERGED", "REVIEW_FLAG", "NOT_USED"}


def fail(message: str) -> None:
    raise ValueError(message)


def nonempty(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")


def validate_source_bindings(event: dict[str, Any], index: int) -> None:
    bindings = event.get("source_bindings")
    if not isinstance(bindings, list) or not bindings:
        fail(f"events[{index}].source_bindings must be a non-empty list")
    for binding_index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            fail(f"events[{index}].source_bindings[{binding_index}] must be an object")
        nonempty(binding.get("source_id"), f"source_bindings[{binding_index}].source_id")
        if binding.get("source_id") != "INLINE_CANDIDATE":
            nonempty(binding.get("sha256"), f"source_bindings[{binding_index}].sha256")


def validate_step(step: Any, event_index: int, step_index: int) -> None:
    if not isinstance(step, dict):
        fail(f"events[{event_index}].chain_steps[{step_index}] must be an object")
    for field in ("step_id", "actor", "target", "action", "state_in", "state_out", "residue"):
        nonempty(step.get(field), f"chain_steps[{step_index}].{field}")
    if not isinstance(step.get("residue_changes_next_action"), bool):
        fail(f"chain_steps[{step_index}].residue_changes_next_action must be boolean")
    if step["residue_changes_next_action"]:
        nonempty(step.get("next_action_link"), f"chain_steps[{step_index}].next_action_link")


def validate_event(event: Any, index: int) -> None:
    if not isinstance(event, dict):
        fail(f"events[{index}] must be an object")
    nonempty(event.get("event_id"), f"events[{index}].event_id")
    nonempty(event.get("root_event"), f"events[{index}].root_event")
    status = event.get("status")
    if status not in STATUSES:
        fail(f"events[{index}].status must be one of {sorted(STATUSES)}")
    validate_source_bindings(event, index)
    steps = event.get("chain_steps", [])
    if status in {"READY", "ADOPTED", "REVIEW_FLAG"}:
        if not isinstance(steps, list) or not 2 <= len(steps) <= 6:
            fail(f"events[{index}] requires 2-6 chain_steps for status {status}")
        for step_index, step in enumerate(steps):
            validate_step(step, index, step_index)
        nonempty(event.get("abort_point"), f"events[{index}].abort_point")
        if not isinstance(event.get("forbidden_outcomes"), list):
            fail(f"events[{index}].forbidden_outcomes must be a list")
    elif steps and (not isinstance(steps, list) or len(steps) > 6):
        fail(f"events[{index}].chain_steps must contain at most 6 steps")


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != "LIFE_EVENT_CHAIN_V1":
        fail("schema must be LIFE_EVENT_CHAIN_V1")
    nonempty(payload.get("chapter_id"), "chapter_id")
    events = payload.get("events")
    if not isinstance(events, list):
        fail("events must be a list")
    max_units = payload.get("max_autonomous_units", 5)
    if not isinstance(max_units, int) or max_units < 0:
        fail("max_autonomous_units must be a non-negative integer")
    if len(events) > max_units:
        fail(f"event count {len(events)} exceeds max_autonomous_units {max_units}")
    ids: set[str] = set()
    adopted = 0
    for index, event in enumerate(events):
        validate_event(event, index)
        event_id = event["event_id"]
        if event_id in ids:
            fail(f"duplicate event_id: {event_id}")
        ids.add(event_id)
        if event["status"] == "ADOPTED":
            adopted += 1
    declared = payload.get("adopted_event_count")
    if declared is not None and declared != adopted:
        fail(f"adopted_event_count={declared} does not match {adopted}")
    return {
        "result": "PASS",
        "schema": payload["schema"],
        "chapter_id": payload["chapter_id"],
        "event_count": len(events),
        "adopted_event_count": adopted,
    }


def self_test() -> int:
    sample = {
        "schema": "LIFE_EVENT_CHAIN_V1",
        "chapter_id": "example",
        "max_autonomous_units": 1,
        "events": [
            {
                "event_id": "e1",
                "status": "ADOPTED",
                "root_event": "a request arrives during a task",
                "source_bindings": [{"source_id": "INLINE_CANDIDATE"}],
                "chain_steps": [
                    {"step_id": "s1", "actor": "a", "target": "b", "action": "ask", "state_in": "open", "state_out": "interrupted", "residue": "request remains", "residue_changes_next_action": True, "next_action_link": "s2"},
                    {"step_id": "s2", "actor": "b", "target": "a", "action": "defer", "state_in": "interrupted", "state_out": "delayed", "residue": "time is lost", "residue_changes_next_action": True, "next_action_link": "scene-exit"},
                ],
                "abort_point": "the request can be withdrawn",
                "forbidden_outcomes": [],
            }
        ],
    }
    validate(sample)
    try:
        broken = dict(sample)
        broken["events"] = [{**sample["events"][0], "chain_steps": []}]
        validate(broken)
    except ValueError:
        return 0
    raise SystemExit("self-test failed to reject an incomplete chain")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("SELF_TEST=PASS" if self_test() == 0 else "SELF_TEST=FAIL")
        return 0
    if not args.path:
        parser.error("path is required unless --self-test is used")
    try:
        payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
        result = validate(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"result": "BLOCKED", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
