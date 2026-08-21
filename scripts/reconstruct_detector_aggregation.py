#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reconstruct visible detector category shares from segment lengths and scores."
    )
    parser.add_argument("input_json", nargs="?", help="JSON with a top-level reports array")
    parser.add_argument("--tolerance", type=float, default=0.02, help="percentage-point tolerance")
    parser.add_argument(
        "--score-tolerance",
        type=float,
        default=0.0002,
        help="absolute tolerance for a declared 0-1 weighted score",
    )
    parser.add_argument("--strict", action="store_true", help="exit non-zero when a declared total/share mismatches")
    parser.add_argument("--self-test", action="store_true", help="run an embedded deterministic fixture")
    return parser.parse_args()


def segment_tuple(segment: Any) -> tuple[int, float]:
    if isinstance(segment, list) and len(segment) == 2:
        chars, score = segment
    elif isinstance(segment, dict):
        chars = segment.get("chars", segment.get("reported_chars"))
        score = segment.get("score")
    else:
        raise ValueError(f"invalid segment shape: {segment!r}")
    if not isinstance(chars, int) or chars <= 0:
        raise ValueError(f"segment chars must be a positive integer: {chars!r}")
    if not isinstance(score, (int, float)) or not 0 <= float(score) <= 1:
        raise ValueError(f"segment score must be within [0,1]: {score!r}")
    return chars, float(score)


def reconstruct(report: dict[str, Any], tolerance: float, score_tolerance: float) -> dict[str, Any]:
    parsed = [segment_tuple(segment) for segment in report.get("segments", [])]
    if not parsed:
        raise ValueError("report has no segments")
    total = sum(chars for chars, _score in parsed)
    human_chars = sum(chars for chars, score in parsed if score < 0.5)
    suspected_chars = sum(chars for chars, score in parsed if 0.5 <= score < 0.99)
    ai_chars = sum(chars for chars, score in parsed if score >= 0.99)
    weighted_score = sum(chars * score for chars, score in parsed) / total

    shares = {
        "human_percent": human_chars / total * 100,
        "suspected_ai_percent": suspected_chars / total * 100,
        "ai_percent": ai_chars / total * 100,
    }
    declared_checks: dict[str, Any] = {}
    declared_total = report.get("total_chars")
    if declared_total is not None:
        declared_checks["total_chars"] = {
            "declared": declared_total,
            "computed": total,
            "pass": declared_total == total,
        }
    declared_weighted_score = next(
        (
            report[field]
            for field in ("weighted_score", "weighted_average_score", "observed_weighted_score")
            if report.get(field) is not None
        ),
        None,
    )
    if declared_weighted_score is not None:
        declared_checks["weighted_score"] = {
            "declared": declared_weighted_score,
            "computed": round(weighted_score, 6),
            "pass": abs(float(declared_weighted_score) - weighted_score) <= score_tolerance,
        }
    for field, computed in shares.items():
        declared = report.get(field)
        if declared is not None:
            declared_checks[field] = {
                "declared": declared,
                "computed": round(computed, 6),
                "pass": abs(float(declared) - computed) <= tolerance,
            }

    threshold_layer = {
        "thresholds": {
            "human": "score < 0.5",
            "suspected_ai": "0.5 <= score < 0.99",
            "ai": "score >= 0.99",
        },
        "category_chars": {
            "human": human_chars,
            "suspected_ai": suspected_chars,
            "ai": ai_chars,
        },
        "category_percent": {key: round(value, 6) for key, value in shares.items()},
    }
    continuous_layer = {
        "weighted_mean": round(weighted_score, 6),
        "formula": "sum(segment_chars * segment_score) / total_chars",
        "segment_count": len(parsed),
    }
    return {
        "name": report.get("name", "UNNAMED_REPORT"),
        "chapter_id": report.get("chapter_id", "UNBOUND_CHAPTER"),
        "record_scope": "SINGLE_CHAPTER_SINGLE_SUBMISSION",
        "segment_count": len(parsed),
        "total_chars": total,
        "category_chars": {
            "human": human_chars,
            "suspected_ai": suspected_chars,
            "ai": ai_chars,
        },
        "computed_weighted_score": round(weighted_score, 6),
        "weighted_score_formula": "sum(segment_chars * segment_score) / total_chars",
        "computed_percent": {key: round(value, 6) for key, value in shares.items()},
        "thresholds": {
            "human": "score < 0.5",
            "suspected_ai": "0.5 <= score < 0.99",
            "ai": "score >= 0.99",
        },
        "declared_checks": declared_checks,
        "layered_metrics": {
            "continuous_weighted_layer": continuous_layer,
            "threshold_bucket_layer": threshold_layer,
            "cross_chapter_comparison": "NOT_PERFORMED",
        },
        "pass": all(check["pass"] for check in declared_checks.values()),
    }


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.self_test:
        return {
            "reports": [
                {
                    "name": "self-test",
                    "total_chars": 1000,
                    "human_percent": 30.0,
                    "suspected_ai_percent": 60.0,
                    "ai_percent": 10.0,
                    "weighted_score": 0.5795,
                    "segments": [[300, 0.2], [600, 0.7], [100, 0.995]],
                }
            ]
        }
    if not args.input_json:
        raise ValueError("input_json is required unless --self-test is used")
    return json.loads(Path(args.input_json).read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args)
        reports = payload.get("reports")
        if not isinstance(reports, list) or not reports:
            raise ValueError("top-level reports must be a non-empty array")
        results = [reconstruct(report, args.tolerance, args.score_tolerance) for report in reports]
        output = {
            "schema": "detector_aggregation_reconstruction_v1",
            "report_count": len(results),
            "pass_count": sum(1 for result in results if result["pass"]),
            "all_pass": all(result["pass"] for result in results),
            "scope_note": "Observed single-chapter aggregation only; does not infer private model features, author identity, or cross-chapter causality.",
            "reports": results,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        if args.strict and not output["all_pass"]:
            return 1
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": "detector_aggregation_reconstruction_v1", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
