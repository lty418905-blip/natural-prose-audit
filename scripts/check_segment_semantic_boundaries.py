#!/usr/bin/env python3
"""Check declared detector segment byte boundaries without parsing a detector report."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SENTENCE_END = set("。！？!?；;…")
CLOSING_QUOTES = set("”’\"'）】》」』")


def valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdefABCDEF" for char in value)
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _has_unclosed_dialogue(text: str) -> bool:
    """Handle both Chinese and the ASCII quotes used by project prose."""
    ascii_open = text.count('"') % 2 == 1
    curly_open = text.count("“") > text.count("”") or text.count("‘") > text.count("’")
    return ascii_open or curly_open


def boundary_state(raw: bytes, offset: int) -> dict[str, Any]:
    if offset < 0 or offset > len(raw):
        raise ValueError(f"boundary outside source bytes: {offset}")
    try:
        left = raw[:offset].decode("utf-8")
        right = raw[offset:].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"boundary {offset} splits a UTF-8 code point") from exc

    if offset in (0, len(raw)):
        return {"offset": offset, "classification": "DOCUMENT_EDGE", "review_flag": False}

    open_dialogue = _has_unclosed_dialogue(left)
    line_boundary = left.endswith("\n") or right.startswith("\n")
    if open_dialogue:
        classification = "MID_DIALOGUE_FLAG"
        review_flag = True
    elif line_boundary:
        classification = "PARAGRAPH_OR_LINE_BOUNDARY"
        review_flag = False
    else:
        previous = left.rstrip()
        while previous and previous[-1] in CLOSING_QUOTES:
            previous = previous[:-1].rstrip()
        if previous and previous[-1] in SENTENCE_END:
            classification = "SENTENCE_WITHIN_PARAGRAPH_FLAG"
            review_flag = True
        else:
            classification = "MID_SENTENCE_FLAG"
            review_flag = True

    return {"offset": offset, "classification": classification, "review_flag": review_flag}


def apply_known_normalization(source: bytes, profile: str) -> bytes:
    normalized_profile = profile.strip().upper()
    if normalized_profile in {"NONE", "IDENTICAL"}:
        return source
    if normalized_profile in {
        "COLLAPSE_DOUBLE_LF_AND_TRIM_TRAILING_LF",
        "COLLAPSE_DOUBLE_LF_ONCE_TRIM_TRAILING_LF_UTF8",
    }:
        text = source.decode("utf-8")
        return text.replace("\n\n", "\n").rstrip("\n").encode("utf-8")
    raise ValueError(f"unsupported normalization_profile: {profile}")


def check_payload(submission_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    raw = submission_path.read_bytes()
    actual_sha = sha256_bytes(raw)
    origin_sha = payload.get("source_sha256")
    submission_sha = payload.get("submission_sha256")
    normalization_transform = payload.get("normalization_transform")
    normalization_profile = payload.get("normalization_profile")
    if origin_sha is not None and not valid_sha256(origin_sha):
        raise ValueError("source_sha256 must be a 64-character hexadecimal SHA-256")
    if submission_sha is not None and not valid_sha256(submission_sha):
        raise ValueError("submission_sha256 must be a 64-character hexadecimal SHA-256")

    # Backward compatibility: legacy payloads used source_sha256 for the bytes
    # being checked. New payloads may bind an original source and a normalized
    # detector submission separately.
    if submission_sha is None:
        if origin_sha is not None and str(origin_sha).upper() != actual_sha:
            raise ValueError(f"legacy source sha256 mismatch: {actual_sha}")
        submission_identity_mode = "LEGACY_SOURCE_EQUALS_SUBMISSION"
    else:
        if submission_sha.upper() != actual_sha:
            raise ValueError(f"submission sha256 mismatch: {actual_sha}")
        submission_identity_mode = "SEPARATE_SOURCE_AND_SUBMISSION"

    declared_submission_bytes = payload.get("submission_bytes")
    declared_source_bytes = payload.get("source_bytes")
    if submission_sha is None:
        if declared_source_bytes is not None and declared_source_bytes != len(raw):
            raise ValueError(f"legacy source bytes mismatch: {len(raw)} != {declared_source_bytes}")
    elif declared_submission_bytes is not None and declared_submission_bytes != len(raw):
        raise ValueError(f"submission bytes mismatch: {len(raw)} != {declared_submission_bytes}")
    if (
        declared_source_bytes is not None
        and origin_sha is not None
        and origin_sha.upper() == actual_sha
        and declared_source_bytes != len(raw)
    ):
        raise ValueError(f"source bytes mismatch: {len(raw)} != {declared_source_bytes}")

    identity_review_flags: list[str] = []
    source_path_value = payload.get("source_path")
    bound_source_path: Path | None = None
    bound_source_bytes: bytes | None = None
    if source_path_value is not None:
        if not isinstance(source_path_value, str) or not source_path_value.strip():
            raise ValueError("source_path must be a non-empty path string")
        bound_source_path = Path(source_path_value)
        if not bound_source_path.is_absolute():
            raise ValueError("source_path must be absolute")
        bound_source_bytes = bound_source_path.read_bytes()
        bound_source_sha = sha256_bytes(bound_source_bytes)
        if origin_sha is None:
            raise ValueError("source_path requires source_sha256")
        if bound_source_sha != origin_sha.upper():
            raise ValueError(f"bound source sha256 mismatch: {bound_source_sha}")
        if declared_source_bytes is not None and declared_source_bytes != len(bound_source_bytes):
            raise ValueError(f"bound source bytes mismatch: {len(bound_source_bytes)} != {declared_source_bytes}")

    if origin_sha is None:
        source_identity_status = "SUBMISSION_ONLY_NO_ORIGIN"
        source_verification_status = "NOT_APPLICABLE"
    elif origin_sha.upper() == actual_sha:
        source_identity_status = "BYTE_IDENTICAL"
        source_verification_status = "VERIFIED_BY_SUBMISSION_BYTES"
    elif (
        normalization_transform
        and str(normalization_transform).strip().upper() not in {"NONE", "IDENTICAL"}
    ) or (
        normalization_profile
        and str(normalization_profile).strip().upper() not in {"NONE", "IDENTICAL"}
    ):
        source_identity_status = "SOURCE_SUBMISSION_DIFFERENT_DECLARED_TRANSFORM"
        identity_review_flags.append("source and detector submission bytes differ; declared transform requires comparability review")
        if bound_source_bytes is None:
            source_verification_status = "ORIGIN_HASH_ONLY_NOT_REVALIDATED"
            identity_review_flags.append("source bytes were not bound and revalidated")
        else:
            source_verification_status = "VERIFIED_BOUND_SOURCE_FILE"
    else:
        source_identity_status = "SOURCE_SUBMISSION_DIFFERENT_UNEXPLAINED"
        source_verification_status = (
            "VERIFIED_BOUND_SOURCE_FILE" if bound_source_bytes is not None else "ORIGIN_HASH_ONLY_NOT_REVALIDATED"
        )
        identity_review_flags.append("source and detector submission bytes differ without a declared transform")

    transform_verification_status = "NOT_APPLICABLE"
    if origin_sha is not None and origin_sha.upper() != actual_sha:
        if normalization_profile is None:
            transform_verification_status = "DECLARED_NOT_MECHANICALLY_VERIFIED"
            identity_review_flags.append("normalization transform has no mechanically executable profile")
        elif bound_source_bytes is None:
            transform_verification_status = "SOURCE_BYTES_REQUIRED"
            identity_review_flags.append("normalization profile cannot be verified without bound source bytes")
        else:
            reconstructed = apply_known_normalization(bound_source_bytes, str(normalization_profile))
            if reconstructed != raw:
                raise ValueError("normalization_profile output does not match detector submission bytes")
            transform_verification_status = "PASS"

    if payload.get("boundary_unit", "UTF8_BYTES") != "UTF8_BYTES":
        raise ValueError("boundary_unit must be UTF8_BYTES")

    coverage_mode = payload.get("coverage_mode", "FULL_DOCUMENT")
    if coverage_mode not in {"FULL_DOCUMENT", "PARTIAL_WINDOW"}:
        raise ValueError("coverage_mode must be FULL_DOCUMENT or PARTIAL_WINDOW")

    segments = payload.get("segments")
    if not isinstance(segments, list) or not segments:
        raise ValueError("segments must be a non-empty array")

    normalized: list[dict[str, Any]] = []
    offsets: set[int] = set()
    previous_end: int | None = None
    for index, segment in enumerate(segments, 1):
        if not isinstance(segment, dict):
            raise ValueError(f"segment {index} must be an object")
        start = segment.get("utf8_start")
        end = segment.get("utf8_end")
        if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(raw):
            raise ValueError(f"segment {index} has an invalid UTF-8 byte range")
        if previous_end is not None and start != previous_end:
            raise ValueError(f"segment {index} is not contiguous with the previous segment")
        try:
            decoded_segment = raw[start:end].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"segment {index} splits a UTF-8 code point") from exc
        reported_chars = segment.get("reported_chars")
        if reported_chars is not None:
            if not isinstance(reported_chars, int) or isinstance(reported_chars, bool) or reported_chars <= 0:
                raise ValueError(f"segment {index} reported_chars must be a positive integer")
            if reported_chars != len(decoded_segment):
                raise ValueError(
                    f"segment {index} reported_chars mismatch: {reported_chars} != {len(decoded_segment)}"
                )
        normalized.append(
            {
                "segment_id": segment.get("segment_id", f"SEG-{index:03d}"),
                "utf8_start": start,
                "utf8_end": end,
                "utf8_bytes": end - start,
                "decoded_chars": len(decoded_segment),
                "reported_chars": reported_chars,
            }
        )
        offsets.update((start, end))
        previous_end = end

    if coverage_mode == "FULL_DOCUMENT" and (
        normalized[0]["utf8_start"] != 0 or normalized[-1]["utf8_end"] != len(raw)
    ):
        raise ValueError("FULL_DOCUMENT segments must cover the complete submission byte range")

    boundary_results = [boundary_state(raw, offset) for offset in sorted(offsets)]
    boundary_review_flags = [item for item in boundary_results if item["review_flag"]]
    review_flags = boundary_review_flags + [
        {"classification": "SOURCE_SUBMISSION_IDENTITY_REVIEW_FLAG", "message": message}
        for message in identity_review_flags
    ]
    return {
        "schema": "SEGMENT_BOUNDARY_SEMANTIC_CHECK_V2",
        "result": "PASS_WITH_REVIEW_FLAG" if review_flags else "PASS",
        "source_path": (
            str(bound_source_path.resolve())
            if bound_source_path is not None
            else str(submission_path.resolve())
            if origin_sha is None or origin_sha.upper() == actual_sha
            else "NOT_BOUND"
        ),
        "submission_path": str(submission_path.resolve()),
        "source_sha256": (origin_sha or actual_sha).upper(),
        "submission_sha256": actual_sha,
        "source_bytes": (
            len(bound_source_bytes)
            if bound_source_bytes is not None
            else len(raw)
            if origin_sha is None or origin_sha.upper() == actual_sha
            else declared_source_bytes
        ),
        "submission_bytes": len(raw),
        "submission_identity_mode": submission_identity_mode,
        "source_identity_status": source_identity_status,
        "source_verification_status": source_verification_status,
        "normalization_transform": normalization_transform or "NONE_DECLARED",
        "normalization_profile": normalization_profile or "NOT_DECLARED",
        "transform_verification_status": transform_verification_status,
        "boundary_unit": "UTF8_BYTES",
        "coverage_mode": coverage_mode,
        "segment_count": len(normalized),
        "segments": normalized,
        "boundaries": boundary_results,
        "boundary_review_flag_count": len(boundary_review_flags),
        "identity_review_flag_count": len(identity_review_flags),
        "review_flag_count": len(review_flags),
        "scope_note": (
            "Evidence-only source mapping. A sentence-within-paragraph or mid-dialogue detector boundary is not a "
            "prose defect and does not authorize production segmentation changes. Source/submission identity flags "
            "require comparability review before causal interpretation."
        ),
    }


def self_test() -> dict[str, Any]:
    raw = "甲走进门。\n\n\"你来了？乙还没说完。\"\n下一句还没说完".encode("utf-8")
    paragraph_boundary = raw.index("\n\n".encode("utf-8")) + 2
    # Use a separate non-dialogue fixture for the ordinary mid-sentence case;
    # the main fixture intentionally keeps an open ASCII quote until later so
    # the dialogue-boundary case can be tested independently.
    mid_sentence_raw = "甲走进门，还没说完。".encode("utf-8")
    mid_sentence = mid_sentence_raw.index("还没".encode("utf-8"))
    sentence_within_paragraph = "甲。乙。".encode("utf-8").index("。".encode("utf-8")) + len("。".encode("utf-8"))
    dialogue_boundary = raw.index("。\"".encode("utf-8")) + len("。".encode("utf-8"))
    checks = [
        boundary_state(raw, 0),
        boundary_state(raw, paragraph_boundary),
        boundary_state(mid_sentence_raw, mid_sentence),
        boundary_state("甲。乙。".encode("utf-8"), sentence_within_paragraph),
        boundary_state(raw, dialogue_boundary),
    ]
    normalized = apply_known_normalization(b"\xe7\x94\xb2\xe3\x80\x82\n\n\xe4\xb9\x99\xe3\x80\x82\n", "COLLAPSE_DOUBLE_LF_ONCE_TRIM_TRAILING_LF_UTF8")
    passed = (
        checks[0]["classification"] == "DOCUMENT_EDGE"
        and checks[1]["classification"] == "PARAGRAPH_OR_LINE_BOUNDARY"
        and checks[2]["classification"] == "MID_SENTENCE_FLAG"
        and checks[3]["classification"] == "SENTENCE_WITHIN_PARAGRAPH_FLAG"
        and checks[4]["classification"] == "MID_DIALOGUE_FLAG"
        and normalized == "甲。\n乙。".encode("utf-8")
    )
    return {
        "schema": "SEGMENT_BOUNDARY_SEMANTIC_CHECK_SELF_TEST_V2",
        "result": "PASS" if passed else "FAIL",
        "checks": checks,
        "normalization_profile_check": "PASS" if normalized == "甲。\n乙。".encode("utf-8") else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check detector segment UTF-8 boundaries against actual submission semantics")
    parser.add_argument("submission_path", nargs="?", type=Path)
    parser.add_argument("segments_json", nargs="?", type=Path)
    parser.add_argument("--strict", action="store_true", help="return 1 when semantic review flags exist")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            output = self_test()
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return 0 if output["result"] == "PASS" else 1
        if args.submission_path is None or args.segments_json is None:
            raise ValueError("submission_path and segments_json are required unless --self-test is used")
        payload = json.loads(args.segments_json.read_text(encoding="utf-8-sig"))
        if not isinstance(payload, dict):
            raise ValueError("segments_json must contain a JSON object")
        output = check_payload(args.submission_path, payload)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        if args.strict and output["review_flag_count"]:
            return 1
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": "SEGMENT_BOUNDARY_SEMANTIC_CHECK_V2", "result": "INVALID_INPUT", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
