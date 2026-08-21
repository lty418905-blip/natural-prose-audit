#!/usr/bin/env python3
"""Validate an evidence-only detector probe batch without parsing or calling a detector."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


VALID_CLASSES = {"HUMAN", "SUSPECTED_AI", "AI"}


def score_class(score: float) -> str:
    if score < 0.0 or score > 1.0:
        raise ValueError(f"score outside [0, 1]: {score}")
    if score < 0.5:
        return "HUMAN"
    if score < 0.99:
        return "SUSPECTED_AI"
    return "AI"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_json", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.batch_json.read_text(encoding="utf-8-sig"))
    reports = data.get("reports")
    errors: list[str] = []
    warnings: list[str] = []
    identity_blockers: list[str] = []

    if not isinstance(reports, list) or not reports:
        errors.append("reports must be a non-empty array")
        reports = []

    seen: set[str] = set()
    for index, report in enumerate(reports):
        label = report.get("probe_id", f"index-{index}")
        if label in seen:
            errors.append(f"duplicate probe_id: {label}")
        seen.add(label)

        for field in ("probe_id", "path", "sha256", "bytes", "reported_chars", "segments", "input_identity", "comparability"):
            if field not in report:
                errors.append(f"{label}: missing {field}")

        path_text = report.get("path")
        if isinstance(path_text, str):
            path = Path(path_text)
            if path.is_file():
                actual_bytes = path.stat().st_size
                if actual_bytes != report.get("bytes"):
                    errors.append(f"{label}: bytes mismatch {actual_bytes} != {report.get('bytes')}")
                actual_sha = sha256_file(path)
                if actual_sha != str(report.get("sha256", "")).upper():
                    errors.append(f"{label}: sha256 mismatch {actual_sha}")
            elif args.strict:
                errors.append(f"{label}: report file not found: {path}")
            else:
                warnings.append(f"{label}: report file not available for rehash")

        segments = report.get("segments")
        if isinstance(segments, list) and segments:
            total = 0
            for segment_index, segment in enumerate(segments):
                try:
                    chars = int(segment["chars"])
                    score = float(segment["score"])
                    declared_class = segment["class"]
                except (KeyError, TypeError, ValueError) as exc:
                    errors.append(f"{label}: invalid segment {segment_index}: {exc}")
                    continue
                total += chars
                if declared_class not in VALID_CLASSES:
                    errors.append(f"{label}: invalid class {declared_class}")
                else:
                    expected = score_class(score)
                    if declared_class != expected:
                        errors.append(f"{label}: class {declared_class} != {expected} for score {score}")
            if total != report.get("reported_chars"):
                errors.append(f"{label}: segment chars {total} != reported_chars {report.get('reported_chars')}")
        else:
            errors.append(f"{label}: segments must be a non-empty array")

        identity = str(report.get("input_identity", "UNKNOWN"))
        comparability = str(report.get("comparability", "UNKNOWN"))
        if "MISMATCH" in identity or identity == "UNKNOWN" or "INVALID_INPUT_IDENTITY" in comparability:
            identity_blockers.append(f"{label}: {identity} / {comparability}")
        elif "MIXED_SOURCE" in comparability:
            identity_blockers.append(f"{label}: {comparability}")

    invalid_groups = data.get("invalid_groups", [])
    if invalid_groups:
        for group in invalid_groups:
            identity_blockers.append(f"group {group.get('group', 'UNKNOWN')}: {group.get('reason', 'no reason')}")

    if errors:
        result = "FAILED_MECHANICAL_VALIDATION"
        exit_code = 2
    elif identity_blockers:
        result = "BLOCKED_FOR_CAUSAL_INTERPRETATION"
        exit_code = 3
    else:
        result = "PASS"
        exit_code = 0

    output = {
        "schema": "DETECTOR_PROBE_BATCH_VALIDATION_V1",
        "result": result,
        "report_count": len(reports),
        "mechanical_errors": errors,
        "identity_blockers": identity_blockers,
        "warnings": warnings,
        "not_executed": [
            "PDF_TEXT_EXTRACTION",
            "DETECTOR_CALL",
            "PRIVATE_ALGORITHM_INFERENCE",
            "PRODUCTION_PROSE_CHANGE"
        ]
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
