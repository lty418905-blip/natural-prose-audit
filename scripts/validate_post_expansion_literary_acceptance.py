#!/usr/bin/env python3
"""Validate identity and completeness of a post-expansion literary review."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REQUIRED_CHECKS = {
    "FUNCTION_LOST_IF_REMOVED",
    "NOVEL_INFORMATION_OR_STATE_CHANGE",
    "OBJECT_AND_SENSORY_RECURRENCE",
    "VOICE_AND_SEAM_FIT",
    "OUTLINE_AND_FACT_BOUNDARY",
    "PLAN_CLOSURE",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    args = parser.parse_args()
    path = Path(args.record).resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if data.get("schema") != "POST_EXPANSION_LITERARY_ACCEPTANCE_V1":
        errors.append("schema mismatch")
    if data.get("result") != "PASS":
        errors.append("result must be PASS")
    for key in ("object_id", "pre_expansion_prose", "post_expansion_prose",
                "outline", "fragments", "whole_chapter_counterfactual",
                "reviewer_identity"):
        if key not in data:
            errors.append(f"missing {key}")

    for key in ("pre_expansion_prose", "post_expansion_prose", "outline"):
        item = data.get(key, {})
        try:
            source = Path(item["path"]).resolve()
            expected = item["sha256"].upper()
            if sha(source) != expected:
                errors.append(f"{key} sha256 mismatch")
        except Exception as exc:
            errors.append(f"{key} invalid: {exc}")

    fragments = data.get("fragments", [])
    if not isinstance(fragments, list) or not fragments:
        errors.append("fragments must be a non-empty list")
    else:
        for index, fragment in enumerate(fragments):
            checks = fragment.get("checks", {})
            if set(checks) != REQUIRED_CHECKS:
                errors.append(f"fragment[{index}] checks must equal required six checks")
            if any(value not in ("PASS", "NOT_APPLICABLE") for value in checks.values()):
                errors.append(f"fragment[{index}] has non-pass check")
            if not fragment.get("path") or not fragment.get("sha256"):
                errors.append(f"fragment[{index}] missing path/sha256")
            else:
                try:
                    if sha(Path(fragment["path"]).resolve()) != fragment["sha256"].upper():
                        errors.append(f"fragment[{index}] sha256 mismatch")
                except Exception as exc:
                    errors.append(f"fragment[{index}] invalid: {exc}")
            if not fragment.get("function_lost_if_removed"):
                errors.append(f"fragment[{index}] missing counterfactual function")

    whole = data.get("whole_chapter_counterfactual", {})
    if whole.get("result") != "PASS" or not whole.get("evidence"):
        errors.append("whole_chapter_counterfactual must be PASS with evidence")

    result = "PASS" if not errors else "BLOCKED"
    print(json.dumps({"result": result, "record": str(path), "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"result": "ERROR", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(4)
