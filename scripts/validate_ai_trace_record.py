#!/usr/bin/env python3
"""Validate a canonical cold-read AI_TRACE record.

This validates source identity, bounded ranges, and detector-evidence bindings.
It does not score prose, identify authorship, or make an evasion claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterator


SCHEMA = "NATURAL_PROSE_AI_TRACE_RECORD_V1"
SEGMENT_MAP_SCHEMA_V1 = "NATURAL_PROSE_DETECTOR_SEGMENT_MAP_V1"
SEGMENT_MAP_SCHEMA_V2 = "NATURAL_PROSE_DETECTOR_SEGMENT_MAP_V2"
RANGE_UNIT = "UTF8_BYTE"
VALID_EVIDENCE_STATUS = {
    "NO_REPORT",
    "ORDERING_ONLY",
    "MAPPED_SINGLE_RUN",
    "MAPPED_REPEATABILITY_BOUNDED",
}
VALID_FINDING_CLASSES = {
    "DISTRIBUTED_VOICE",
    "STRUCTURAL",
    "RHYTHM",
    "EXPLANATION",
    "DIALOGUE_CLOSURE",
    "BACKGROUND_BEAT",
    "ASSEMBLY_SEAM",
    "OBJECT_OVERLOAD",
    "LOCAL_ISOLATED",
    "UNKNOWN",
    "NONE",
}
VALID_SCOPES = {"LOCAL", "LOCAL_ISOLATED", "MULTI_SCENE", "WHOLE_TEXT", "UNKNOWN", "NONE"}
VALID_FINDING_ACTIONS = {
    "REVIEW_FLAG",
    "KEEP",
    "DELETE_TAIL",
    "BOUNDED_REPHRASE",
    "AIGC_COMPATIBILITY_TARGETED_WITH_GUARDS",
    "SYNTAX_BOUNDED_REPHRASE",
    "NEXT_AUTHOR_HANDOFF",
    "NO_CHANGE",
}
VALID_AUTH_STATUSES = {"NOT_AUTHORIZED", "AUTHORIZED"}

SAFE_POLICY_PHRASES = (
    re.compile(r"(?:不|不得|不应|不以)[^。；;\n]{0,24}(?:检测器|AIGC|AI)[^。；;\n]{0,20}(?:分数|检测率)[^。；;\n]{0,12}(?:为|作为)?[^。；;\n]{0,8}(?:目标|指标)"),
    re.compile(r"(?:不|不得|不应|不会|不追求)[^。；;\n]{0,10}(?:绕过|规避|骗过)[^。；;\n]{0,18}(?:检测器|检测|AIGC|AI)"),
    re.compile(r"(?:not|never|no)\s+(?:a\s+)?detector\s+(?:score\s+)?(?:target|goal)", re.I),
    re.compile(r"(?:do\s+not|must\s+not|will\s+not)\s+(?:bypass|evade|beat)\s+(?:the\s+)?(?:detector|detection)", re.I),
)
FORBIDDEN_VALUE_PATTERNS = (
    re.compile(r"(?:绕过|规避|骗过|逃避)[^。；;\n]{0,24}(?:检测器|检测|AIGC|AI)", re.I),
    re.compile(r"(?:检测器|检测率|AIGC|AI)[^。；;\n]{0,28}(?:降到|压到|低于|少于|归零|通过|达标)", re.I),
    re.compile(r"(?:通过|绕过|骗过)[^。；;\n]{0,14}(?:检测器|检测|AIGC|AI)", re.I),
    re.compile(r"\b(?:bypass|evade|undetectable|beat)\b[^.\n]{0,36}\b(?:detector|detection)\b", re.I),
    re.compile(r"\b(?:detector|detection|aigc)\b[^.\n]{0,36}\b(?:target|goal|below|under|zero)\b", re.I),
)
FORBIDDEN_KEY_PATTERN = re.compile(
    r"(?:绕过|规避|逃避|bypass|evasion|evade|undetectable)|"
    r"(?=.*(?:target|goal|目标))(?=.*(?:detector|detection|aigc|score|rate|检测|分数|检测率))",
    re.I,
)


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def _iter_strings(value: Any, path: str = "record") -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_path = f"{path}.{key}"
            yield key_path, str(key)
            yield from _iter_strings(item, key_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_strings(item, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def _is_safe_policy_sentence(value: str) -> bool:
    return any(pattern.fullmatch(value.strip()) for pattern in SAFE_POLICY_PHRASES)


def find_forbidden_detector_goals(payload: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    ignored_keys = {
        "schema",
        "path",
        "sha256",
        "source_sha256",
        "detector_evidence_status",
        "report_locator",
    }
    objective_keys = {
        "objective_mode",
        "aigc_compatibility_target",
        "aigc_compatibility_targets",
        "detector_target_alignment",
        "aigc_compatibility_outcome",
        "user_detector_acceptance",
        "literary_regression",
        "syntax_revision",
        "syntax_outcome",
        "target_mechanism",
        "mechanism_target",
        "operation",
        "allowed_operations",
        "forbidden_operations",
        "evidence_level",
        "semantic_equivalence",
        "structure_delta",
    }
    for field_path, value in _iter_strings(payload):
        key = field_path.rsplit(".", 1)[-1]
        if key in ignored_keys or not isinstance(value, str) or _is_safe_policy_sentence(value):
            continue
        if key not in objective_keys and FORBIDDEN_KEY_PATTERN.search(key):
            errors.append({"code": "forbidden_detector_goal_field", "field": field_path})
            continue
        if any(pattern.search(value) for pattern in FORBIDDEN_VALUE_PATTERNS):
            errors.append({"code": "forbidden_detector_goal_or_evasion", "field": field_path})
    return errors


def _resolve_path(raw: str, record_path: Path) -> Path:
    candidate = Path(raw)
    return candidate if candidate.is_absolute() else record_path.parent / candidate


def _read_bound_file(
    binding: Any,
    *,
    record_path: Path,
    field: str,
    errors: list[dict[str, str]],
) -> tuple[Path | None, bytes | None, str | None]:
    if not isinstance(binding, dict):
        errors.append({"code": "file_binding_object_required", "field": field})
        return None, None, None
    raw_path = binding.get("path")
    declared_sha = binding.get("sha256")
    if not _non_empty(raw_path):
        errors.append({"code": "bound_file_path_required", "field": field})
        return None, None, None
    if not _valid_sha256(declared_sha):
        errors.append({"code": "bound_file_sha256_invalid", "field": field})
    path = _resolve_path(raw_path, record_path)
    try:
        data = path.read_bytes()
    except OSError as exc:
        errors.append({"code": "bound_file_read_failed", "field": field, "detail": type(exc).__name__})
        return path, None, None
    digest = hashlib.sha256(data).hexdigest()
    if isinstance(declared_sha, str) and digest.lower() != declared_sha.lower():
        errors.append({"code": "bound_file_sha256_mismatch", "field": field})
    return path, data, digest


def _parse_range(item: Any, field: str, errors: list[dict[str, str]]) -> tuple[int, int] | None:
    if not isinstance(item, dict):
        errors.append({"code": "range_must_be_object", "field": field})
        return None
    if item.get("unit") != RANGE_UNIT:
        errors.append({"code": "range_unit_must_be_utf8_byte", "field": field})
    start = item.get("start")
    end = item.get("end")
    if not isinstance(start, int) or isinstance(start, bool) or not isinstance(end, int) or isinstance(end, bool):
        errors.append({"code": "range_offsets_must_be_integers", "field": field})
        return None
    if start < 0 or end <= start:
        errors.append({"code": "range_must_be_nonempty_and_ordered", "field": field})
        return None
    return start, end


def _validate_source_bound_range(
    parsed_range: tuple[int, int] | None,
    *,
    source_size: int | None,
    field: str,
    errors: list[dict[str, str]],
) -> None:
    if parsed_range is not None and source_size is not None and parsed_range[1] > source_size:
        errors.append({"code": "range_exceeds_source_bytes", "field": field})


def _validate_segment_map(
    binding: Any,
    *,
    record_path: Path,
    source_sha256: str | None,
    source_size: int | None,
    errors: list[dict[str, str]],
) -> tuple[bool, str | None, str | None]:
    _path, data, _digest = _read_bound_file(
        binding, record_path=record_path, field="detector_evidence.segment_map", errors=errors
    )
    if data is None:
        return False, None, None
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        errors.append({"code": "segment_map_json_invalid", "detail": type(exc).__name__})
        return False, None, None
    if not isinstance(payload, dict):
        errors.append({"code": "segment_map_schema_invalid"})
        return False, None, None
    schema = payload.get("schema")
    if schema not in {SEGMENT_MAP_SCHEMA_V1, SEGMENT_MAP_SCHEMA_V2}:
        errors.append({"code": "segment_map_schema_invalid"})
        return False, None, None
    if not _valid_sha256(payload.get("source_sha256")) or (
        source_sha256 is not None and payload.get("source_sha256", "").lower() != source_sha256.lower()
    ):
        errors.append({"code": "segment_map_source_sha256_mismatch"})
    segments = payload.get("segments")
    if not isinstance(segments, list) or not segments:
        errors.append({"code": "segment_map_segments_required"})
        return False, None, schema

    submission_data: bytes | None = None
    submission_sha256: str | None = None
    if schema == SEGMENT_MAP_SCHEMA_V2:
        _submission_path, submission_data, submission_digest = _read_bound_file(
            payload.get("submission"),
            record_path=record_path,
            field="segment_map.submission",
            errors=errors,
        )
        declared_submission_sha = payload.get("submission_sha256")
        if not _valid_sha256(declared_submission_sha):
            errors.append({"code": "segment_map_submission_sha256_invalid"})
        elif submission_digest is not None and declared_submission_sha.lower() != submission_digest.lower():
            errors.append({"code": "segment_map_submission_sha256_mismatch"})
        if submission_digest is not None:
            submission_sha256 = submission_digest
        if not _non_empty(payload.get("normalization_transform")):
            errors.append({"code": "segment_map_normalization_transform_required"})
        coverage_mode = payload.get("coverage_mode", "FULL_DOCUMENT")
        if coverage_mode not in {"FULL_DOCUMENT", "PARTIAL_WINDOW"}:
            errors.append({"code": "segment_map_coverage_mode_invalid"})

    valid_count = 0
    previous_submission_end: int | None = None
    for index, segment in enumerate(segments):
        field = f"segment_map.segments[{index}]"
        if not isinstance(segment, dict):
            errors.append({"code": "segment_map_entry_must_be_object", "field": field})
            continue
        if schema == SEGMENT_MAP_SCHEMA_V1:
            parsed_range = _parse_range(segment.get("source_range"), f"{field}.source_range", errors)
            _validate_source_bound_range(
                parsed_range,
                source_size=source_size,
                field=f"{field}.source_range",
                errors=errors,
            )
        else:
            parsed_range = _parse_range(segment.get("submission_range"), f"{field}.submission_range", errors)
            _validate_source_bound_range(
                parsed_range,
                source_size=len(submission_data) if submission_data is not None else None,
                field=f"{field}.submission_range",
                errors=errors,
            )
            source_range = _parse_range(segment.get("source_range"), f"{field}.source_range", errors)
            _validate_source_bound_range(
                source_range,
                source_size=source_size,
                field=f"{field}.source_range",
                errors=errors,
            )
            if parsed_range is not None:
                if previous_submission_end is not None and parsed_range[0] != previous_submission_end:
                    errors.append({"code": "segment_map_submission_ranges_not_contiguous", "field": field})
                previous_submission_end = parsed_range[1]
                reported_chars = segment.get("reported_chars")
                if reported_chars is not None:
                    if not isinstance(reported_chars, int) or isinstance(reported_chars, bool) or reported_chars <= 0:
                        errors.append({"code": "segment_map_reported_chars_invalid", "field": field})
                    elif submission_data is not None:
                        try:
                            decoded_chars = len(submission_data[parsed_range[0]:parsed_range[1]].decode("utf-8"))
                        except UnicodeDecodeError:
                            errors.append({"code": "segment_map_submission_range_splits_utf8", "field": field})
                        else:
                            if decoded_chars != reported_chars:
                                errors.append({"code": "segment_map_reported_chars_mismatch", "field": field})
        if not _non_empty(segment.get("report_locator")):
            errors.append({"code": "segment_report_locator_required", "field": field})
        if parsed_range is not None:
            valid_count += 1
    if schema == SEGMENT_MAP_SCHEMA_V2 and submission_data is not None and segments:
        coverage_mode = payload.get("coverage_mode", "FULL_DOCUMENT")
        first = segments[0].get("submission_range") if isinstance(segments[0], dict) else None
        last = segments[-1].get("submission_range") if isinstance(segments[-1], dict) else None
        if coverage_mode == "FULL_DOCUMENT" and (
            not isinstance(first, dict)
            or first.get("start") != 0
            or not isinstance(last, dict)
            or last.get("end") != len(submission_data)
        ):
            errors.append({"code": "segment_map_full_document_coverage_required"})
    return valid_count > 0, submission_sha256, schema


def _validate_detector_evidence(
    record: dict[str, Any],
    *,
    record_path: Path,
    source_sha256: str | None,
    source_size: int | None,
    errors: list[dict[str, str]],
) -> None:
    status = record.get("detector_evidence_status")
    evidence = record.get("detector_evidence")
    if evidence is None:
        evidence = {}
    if not isinstance(evidence, dict):
        errors.append({"code": "detector_evidence_must_be_object"})
        return
    runs = evidence.get("runs", [])
    if not isinstance(runs, list):
        errors.append({"code": "detector_evidence_runs_must_be_list"})
        runs = []

    run_digests: set[str] = set()
    run_paths: set[str] = set()
    run_submission_shas: list[str | None] = []
    valid_run_count = 0
    for index, run in enumerate(runs):
        field = f"detector_evidence.runs[{index}]"
        if not isinstance(run, dict):
            errors.append({"code": "detector_run_must_be_object", "field": field})
            continue
        run_source_sha = run.get("source_sha256")
        if not _valid_sha256(run_source_sha) or (
            source_sha256 is not None and run_source_sha.lower() != source_sha256.lower()
        ):
            errors.append({"code": "detector_run_source_sha256_mismatch", "field": field})
        run_submission_sha = run.get("submission_sha256")
        if run_submission_sha is not None and not _valid_sha256(run_submission_sha):
            errors.append({"code": "detector_run_submission_sha256_invalid", "field": field})
            run_submission_shas.append(None)
        else:
            run_submission_shas.append(run_submission_sha.lower() if isinstance(run_submission_sha, str) else None)
        report_path, report_data, report_digest = _read_bound_file(
            run.get("report"), record_path=record_path, field=f"{field}.report", errors=errors
        )
        if report_data is not None and report_digest is not None and report_path is not None:
            valid_run_count += 1
            run_digests.add(report_digest.lower())
            run_paths.add(str(report_path.resolve()).lower())

    segment_binding = evidence.get("segment_map")
    segment_map_valid = False
    segment_map_submission_sha: str | None = None
    segment_map_schema: str | None = None
    if segment_binding is not None:
        segment_map_valid, segment_map_submission_sha, segment_map_schema = _validate_segment_map(
            segment_binding,
            record_path=record_path,
            source_sha256=source_sha256,
            source_size=source_size,
            errors=errors,
        )
    if segment_map_schema == SEGMENT_MAP_SCHEMA_V2:
        for index, run_submission_sha in enumerate(run_submission_shas):
            if run_submission_sha is None:
                errors.append({"code": "detector_run_submission_sha256_required_for_v2_map", "field": f"detector_evidence.runs[{index}]"})
            elif segment_map_submission_sha is not None and run_submission_sha != segment_map_submission_sha.lower():
                errors.append({"code": "detector_run_submission_sha256_mismatch", "field": f"detector_evidence.runs[{index}]"})

    if status == "NO_REPORT":
        if runs or segment_binding is not None:
            errors.append({"code": "no_report_status_must_not_bind_detector_evidence"})
    elif status == "MAPPED_SINGLE_RUN":
        if valid_run_count < 1:
            errors.append({"code": "mapped_single_run_requires_bound_report"})
        if not segment_map_valid:
            errors.append({"code": "mapped_single_run_requires_valid_segment_map"})
    elif status == "MAPPED_REPEATABILITY_BOUNDED":
        if valid_run_count < 2 or len(run_digests) < 2 or len(run_paths) < 2:
            errors.append({"code": "repeatability_requires_two_distinct_bound_reports"})
        if not segment_map_valid:
            errors.append({"code": "repeatability_requires_valid_segment_map"})


def validate_record(
    record_path: Path,
    *,
    source_path: Path | None = None,
    show_source_path: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    try:
        parsed = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        parsed = None
        errors.append({"code": "record_read_failed", "detail": type(exc).__name__})
    record = parsed if isinstance(parsed, dict) else None
    if parsed is not None and record is None:
        errors.append({"code": "record_must_be_object"})

    source: Path | None = None
    source_bytes: bytes | None = None
    source_digest: str | None = None
    primary_ranges: list[tuple[int, int]] = []
    allowed_ranges: list[tuple[int, int]] = []

    if record is not None:
        if record.get("schema") != SCHEMA:
            errors.append({"code": "unsupported_schema"})
        if record.get("mode") != "PRE_REVISION":
            errors.append({"code": "cold_read_record_must_be_pre_revision"})
        if record.get("cold_read_locked_before_detector") is not True:
            errors.append({"code": "cold_read_order_not_locked"})
        if record.get("detector_evidence_status") not in VALID_EVIDENCE_STATUS:
            errors.append({"code": "invalid_detector_evidence_status"})

        source_info = record.get("source")
        if not isinstance(source_info, dict):
            errors.append({"code": "source_object_required"})
            source_info = {}
        declared_digest = source_info.get("sha256")
        if not _valid_sha256(declared_digest):
            errors.append({"code": "invalid_source_sha256"})
        if source_path is not None:
            source = source_path
        elif _non_empty(source_info.get("path")):
            source = _resolve_path(source_info["path"], record_path)
        else:
            errors.append({"code": "source_path_required"})
        if source is not None:
            try:
                source_bytes = source.read_bytes()
                source_digest = hashlib.sha256(source_bytes).hexdigest()
            except OSError as exc:
                errors.append({"code": "source_read_failed", "detail": type(exc).__name__})
            else:
                if isinstance(declared_digest, str) and source_digest.lower() != declared_digest.lower():
                    errors.append({"code": "source_sha256_mismatch"})

        primary = record.get("primary_finding")
        if not isinstance(primary, dict):
            errors.append({"code": "primary_finding_object_required"})
            primary = {}
        primary_id = primary.get("id")
        primary_class = primary.get("class")
        primary_scope = primary.get("scope")
        primary_action = primary.get("action")
        if not _non_empty(primary_id):
            errors.append({"code": "primary_finding_id_required"})
        if primary_class not in VALID_FINDING_CLASSES:
            errors.append({"code": "invalid_primary_finding_class"})
        if primary_scope not in VALID_SCOPES:
            errors.append({"code": "invalid_primary_finding_scope"})
        if primary_action not in VALID_FINDING_ACTIONS:
            errors.append({"code": "invalid_primary_finding_action"})

        evidence_ranges = primary.get("evidence_ranges", [])
        if not isinstance(evidence_ranges, list):
            errors.append({"code": "evidence_ranges_must_be_list"})
            evidence_ranges = []
        for index, item in enumerate(evidence_ranges):
            field = f"primary_finding.evidence_ranges[{index}]"
            parsed_range = _parse_range(item, field, errors)
            _validate_source_bound_range(
                parsed_range,
                source_size=len(source_bytes) if source_bytes is not None else None,
                field=field,
                errors=errors,
            )
            if parsed_range is not None:
                primary_ranges.append(parsed_range)

        if primary_id == "NONE_WITH_REASON":
            if primary_class != "NONE" or primary_scope != "NONE" or primary_action != "NO_CHANGE":
                errors.append({"code": "none_finding_requires_none_identity_and_no_change"})
            if primary_ranges:
                errors.append({"code": "none_finding_must_not_have_evidence_ranges"})
            if not _non_empty(primary.get("reason")):
                errors.append({"code": "none_finding_reason_required"})
        elif not primary_ranges:
            errors.append({"code": "primary_finding_evidence_required"})

        protection = primary.get("voice_protection")
        if not isinstance(protection, list) or not protection or not all(_non_empty(item) for item in protection):
            errors.append({"code": "voice_protection_items_required"})

        authorization = record.get("revision_authorization")
        if not isinstance(authorization, dict):
            errors.append({"code": "revision_authorization_object_required"})
            authorization = {}
        auth_status = authorization.get("status")
        if auth_status not in VALID_AUTH_STATUSES:
            errors.append({"code": "invalid_revision_authorization_status"})
        if authorization.get("target_finding_id") != primary_id:
            errors.append({"code": "revision_target_does_not_match_primary_finding"})
        raw_allowed_ranges = authorization.get("allowed_ranges", [])
        if not isinstance(raw_allowed_ranges, list):
            errors.append({"code": "allowed_ranges_must_be_list"})
            raw_allowed_ranges = []
        for index, item in enumerate(raw_allowed_ranges):
            field = f"revision_authorization.allowed_ranges[{index}]"
            parsed_range = _parse_range(item, field, errors)
            _validate_source_bound_range(
                parsed_range,
                source_size=len(source_bytes) if source_bytes is not None else None,
                field=field,
                errors=errors,
            )
            if parsed_range is not None:
                allowed_ranges.append(parsed_range)

        if auth_status == "NOT_AUTHORIZED" and allowed_ranges:
            errors.append({"code": "not_authorized_must_have_no_allowed_ranges"})
        if auth_status == "AUTHORIZED" and not allowed_ranges:
            errors.append({"code": "authorized_revision_requires_allowed_ranges"})
        if primary_id == "NONE_WITH_REASON" and auth_status != "NOT_AUTHORIZED":
            errors.append({"code": "none_finding_cannot_authorize_revision"})
        for index, allowed in enumerate(allowed_ranges):
            if not any(parent[0] <= allowed[0] and allowed[1] <= parent[1] for parent in primary_ranges):
                errors.append({
                    "code": "allowed_range_outside_primary_finding",
                    "field": f"revision_authorization.allowed_ranges[{index}]",
                })

        if not _non_empty(record.get("detector_independent_reason")):
            errors.append({"code": "detector_independent_reason_required"})
        if not isinstance(record.get("unresolved", []), list):
            errors.append({"code": "unresolved_must_be_list"})

        _validate_detector_evidence(
            record,
            record_path=record_path,
            source_sha256=source_digest,
            source_size=len(source_bytes) if source_bytes is not None else None,
            errors=errors,
        )
        errors.extend(find_forbidden_detector_goals(record))

    result: dict[str, Any] = {
        "schema": "natural_prose_ai_trace_validation_v1",
        "result": "PASS" if not errors else "FAIL",
        "record": record_path.name,
        "source": source.name if source is not None else None,
        "source_sha256": source_digest,
        "errors": errors,
        "verdict": "record_integrity_only_no_literary_or_detector_claim",
    }
    if show_source_path:
        result["record_path"] = str(record_path.resolve())
        result["source_path"] = str(source.resolve()) if source is not None else None
    return result


def self_test() -> dict[str, Any]:
    source_data = "甲。\n乙。".encode("utf-8")
    source_sha = hashlib.sha256(source_data).hexdigest()
    segment_map = {
        "schema": SEGMENT_MAP_SCHEMA_V2,
        "source_sha256": source_sha,
        "submission": {"path": "submission.txt", "sha256": source_sha},
        "submission_sha256": source_sha,
        "normalization_transform": "NONE",
        "coverage_mode": "FULL_DOCUMENT",
        "segments": [
            {
                "submission_range": {"unit": RANGE_UNIT, "start": 0, "end": 7},
                "source_range": {"unit": RANGE_UNIT, "start": 0, "end": 7},
                "reported_chars": 3,
                "report_locator": "segment:1",
            },
            {
                "submission_range": {"unit": RANGE_UNIT, "start": 7, "end": 13},
                "source_range": {"unit": RANGE_UNIT, "start": 7, "end": 13},
                "reported_chars": 2,
                "report_locator": "segment:2",
            },
        ],
    }
    segment_map_data = json.dumps(segment_map, ensure_ascii=False).encode("utf-8")
    segment_map_sha = hashlib.sha256(segment_map_data).hexdigest()
    responses = iter(
        [
            (Path("segment-map.json"), segment_map_data, segment_map_sha),
            (Path("submission.txt"), source_data, source_sha),
        ]
    )
    original_reader = globals()["_read_bound_file"]

    def fake_reader(*_args: Any, **_kwargs: Any) -> tuple[Path | None, bytes | None, str | None]:
        return next(responses)

    errors: list[dict[str, str]] = []
    try:
        globals()["_read_bound_file"] = fake_reader
        valid, submission_sha, schema = _validate_segment_map(
            {"path": "segment-map.json", "sha256": segment_map_sha},
            record_path=Path("record.json"),
            source_sha256=source_sha,
            source_size=len(source_data),
            errors=errors,
        )
    finally:
        globals()["_read_bound_file"] = original_reader
    passed = valid and submission_sha == source_sha and schema == SEGMENT_MAP_SCHEMA_V2 and not errors
    return {
        "schema": "NATURAL_PROSE_AI_TRACE_VALIDATOR_SELF_TEST_V2",
        "result": "PASS" if passed else "FAIL",
        "segment_map_schema": schema,
        "submission_sha256": submission_sha,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a canonical cold-read AI_TRACE record")
    parser.add_argument("record_path", nargs="?", type=Path)
    parser.add_argument(
        "--source",
        type=Path,
        help="optional source manuscript path; otherwise source.path is resolved relative to the record",
    )
    parser.add_argument("--show-source-path", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
        print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
        return 0 if result["result"] == "PASS" else 1
    if args.record_path is None:
        parser.error("record_path is required unless --self-test is used")
    result = validate_record(
        args.record_path,
        source_path=args.source,
        show_source_path=args.show_source_path,
    )
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
