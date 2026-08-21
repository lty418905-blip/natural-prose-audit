#!/usr/bin/env python3
"""Report repeated event mechanism signatures across task-local JSONL libraries."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def read_library(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    entries: list[dict[str, Any]] = []
    warnings: list[str] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: entry must be an object")
        signature = value.get("event_pattern_signature")
        if not isinstance(signature, str) or not signature.strip():
            warnings.append(f"{path}:{line_number}: event_pattern_signature missing")
            continue
        entries.append(
            {
                "library": str(path.resolve()),
                "line": line_number,
                "event_id": value.get("event_id", "UNKNOWN"),
                "scene_id": value.get("scene_id", "UNKNOWN"),
                "signature": signature.strip(),
            }
        )
    return entries, warnings


def compare(paths: list[Path]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    warnings: list[str] = []
    entry_count = 0
    for path in paths:
        entries, local_warnings = read_library(path)
        warnings.extend(local_warnings)
        entry_count += len(entries)
        for entry in entries:
            grouped[entry["signature"]].append(entry)

    repeated = []
    for signature, occurrences in sorted(grouped.items()):
        distinct_libraries = {item["library"] for item in occurrences}
        if len(distinct_libraries) > 1:
            repeated.append(
                {
                    "event_pattern_signature": signature,
                    "library_count": len(distinct_libraries),
                    "occurrence_count": len(occurrences),
                    "occurrences": occurrences,
                    "action": "REVIEW_FLAG",
                }
            )
    return {
        "schema": "CROSS_DOCUMENT_EVENT_PATTERN_AUDIT_V1",
        "result": "PASS_WITH_REVIEW_FLAG" if repeated else "PASS",
        "library_count": len(paths),
        "signed_event_count": entry_count,
        "unique_signature_count": len(grouped),
        "repeated_signature_count": len(repeated),
        "repeated_signatures": repeated,
        "warnings": warnings,
        "scope_note": (
            "Repeated signatures are review flags only. They do not prove detector causality and do not authorize "
            "event deletion, rejection, or prose changes."
        ),
    }


def self_test() -> dict[str, Any]:
    occurrences = {
        "OBJECT_INTERRUPTS_TASK->SOCIAL_FRICTION->RESIDUE": ["A", "B"],
        "ORDINARY_TASK->NO_RESIDUE": ["A"],
    }
    passed = len([key for key, libraries in occurrences.items() if len(set(libraries)) > 1]) == 1
    return {"schema": "CROSS_DOCUMENT_EVENT_PATTERN_AUDIT_SELF_TEST_V1", "result": "PASS" if passed else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare event_pattern_signature values across JSONL libraries")
    parser.add_argument("libraries", nargs="*", type=Path)
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            output = self_test()
            print(json.dumps(output, ensure_ascii=False, indent=None if args.compact else 2))
            return 0 if output["result"] == "PASS" else 1
        if len(args.libraries) < 2:
            raise ValueError("at least two JSONL libraries are required")
        output = compare(args.libraries)
        print(json.dumps(output, ensure_ascii=False, indent=None if args.compact else 2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": "CROSS_DOCUMENT_EVENT_PATTERN_AUDIT_V1", "result": "INVALID_INPUT", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
