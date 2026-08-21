#!/usr/bin/env python3
"""Transparent, offline shadow scorer for registered detector probe evidence.

This is an evidence-bound surrogate, not a reconstruction of a private detector.
It never uploads text, parses PDFs, calls a model, or writes production prose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np


THRESHOLDS = (0.5, 0.99)
FEATURE_NAMES = [
    "log_chars",
    "paragraph_count",
    "title_prefix",
    "prefix_kind_date_or_author",
    "sentence_mean",
    "sentence_std",
    "short_sentence_ratio",
    "dialogue_ratio",
    "first_person_ratio",
    "third_person_ratio",
    "explanation_marker_ratio",
    "ascii_punctuation_ratio",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def section(source: str, heading: str, next_heading: str) -> str:
    start = source.index(heading) + len(heading)
    end = source.index(next_heading, start)
    return source[start:end].strip()


def remove_annotation(block: str) -> str:
    lines = block.strip().splitlines()
    if lines and lines[0].strip().startswith("（"):
        lines = lines[2:] if len(lines) > 1 and not lines[1].strip() else lines[1:]
    return "\n".join(lines).strip()


def source_texts(v1_path: Path, v2_path: Path, v3_path: Path) -> dict[str, dict[str, Any]]:
    v1 = v1_path.read_text(encoding="utf-8")
    v2 = v2_path.read_text(encoding="utf-8")
    v3 = v3_path.read_text(encoding="utf-8")

    p0 = section(v1, "## P0_RAW_REPLAY_BODY", "## P2A_TITLE_PREFIX")
    paragraphs = [item.strip() for item in p0.split("\n\n") if item.strip()]
    if len(paragraphs) != 8:
        raise ValueError(f"expected 8 P0 paragraphs, got {len(paragraphs)}")
    p0_single = "".join(paragraphs)
    p0_four = "\n\n".join("".join(paragraphs[index:index + 2]) for index in range(0, 8, 2))

    p4a = section(v1, "## P4A_PROCEDURAL_CONTROL", "## P4B_ACTION_INTERRUPTION_CONTROL")
    p4b = section(v1, "## P4B_ACTION_INTERRUPTION_CONTROL", "## 记录字段")
    tail_block = section(v2, "### S1_MATCHED_LENGTH_APPEND", "### S2_VIEWPOINT_PAIR")
    tail = tail_block.split("尾段不能单独检测。", 1)[1].strip()

    def v3_section(heading: str, next_heading: str) -> str:
        return remove_annotation(section(v3, heading, next_heading))

    m5_l1 = v3_section("### M5-L1", "### M5-L2")
    m5_l2 = v3_section("### M5-L2", "### M5-L3")
    m5_l3 = v3_section("### M5-L3", "### M5-L4")
    m5_l4 = v3_section("### M5-L4", "## M4_PUNCTUATION_LONG")
    m4a = v3_section("### M4-A", "### M4-B")
    m4b = v3_section("### M4-B", "## S2_VIEWPOINT_350PLUS")
    s2a = v3_section("### S2-A 第一人称", "### S2-B 第三人称")
    s2b = v3_section("### S2-B 第三人称", "## S3_DIALOGUE_350PLUS")
    s3a = v3_section("### S3-A 叙述主导", "### S3-B 对白主导")
    s3b = v3_section("### S3-B 对白主导", "## S4_EXPLANATION_350PLUS")
    s4a = v3_section("### S4-A 即时解释", "### S4-B 延迟解释")
    s4b = v3_section("### S4-B 延迟解释", "## S5_SENTENCE_RHYTHM_350PLUS")
    s5a = v3_section("### S5-A 短句版", "### S5-B 合并句版")
    s5b = v3_section("### S5-B 合并句版", "## C1_INTERACTION_350PLUS")

    def entry(text: str, source: Path, **metadata: Any) -> dict[str, Any]:
        return {
            "text": text,
            "source_path": str(source),
            "source_sha256": sha256_file(source),
            **metadata,
        }

    return {
        "M0": entry(p0, v1_path, variant="P0_EIGHT_PARAGRAPHS"),
        "M1": entry(p0_single, v1_path, variant="P0_SINGLE_PARAGRAPH"),
        "M2": entry(p0_four, v1_path, variant="P0_FOUR_PARAGRAPHS"),
        "M3-AUTHOR": entry("记录人：林岚\n" + p0, v1_path, variant="AUTHOR_PREFIX", prefix_kind="author"),
        "M3-DATE": entry("周五，雨停以后\n" + p0, v1_path, variant="DATE_PREFIX", prefix_kind="date"),
        "M3-TITLE": entry("第七排的借书卡\n" + p0, v1_path, variant="TITLE_PREFIX", prefix_kind="title"),
        "M4-A": entry(m4a, v3_path, variant="CHINESE_PUNCTUATION_PLANNED"),
        "M4-B": entry(m4b, v3_path, variant="ASCII_PUNCTUATION"),
        "M5-L1": entry(m5_l1, v3_path, variant="PHOTO_PREFIX_L1"),
        "M5-L2": entry(m5_l2, v3_path, variant="PHOTO_PREFIX_L2"),
        "M5-L3": entry(m5_l3, v3_path, variant="PHOTO_PREFIX_L3"),
        "M5-L4": entry(m5_l4, v3_path, variant="PHOTO_FULL_L4"),
        "S1-A": entry(p4a + "\n" + tail + "\n", v1_path, variant="PROCEDURAL_PLUS_COMMON_TAIL"),
        "S1-B": entry(p4b + "\n" + tail + "\n", v1_path, variant="ACTION_PLUS_COMMON_TAIL"),
        "S2-A": entry(s2a, v3_path, variant="FIRST_PERSON"),
        "S2-B": entry(s2b, v3_path, variant="THIRD_PERSON"),
        "S3-A": entry(s3a, v3_path, variant="NARRATION_LED"),
        "S3-B": entry(s3b, v3_path, variant="DIALOGUE_LED"),
        "S4-A": entry(s4a, v3_path, variant="IMMEDIATE_EXPLANATION"),
        "S4-B": entry(s4b, v3_path, variant="DELAYED_EXPLANATION"),
        "S5-A": entry(s5a, v3_path, variant="SHORT_SENTENCES"),
        "S5-B": entry(s5b, v3_path, variant="MERGED_SENTENCES"),
        "C1-A": entry("少了一张照片\n" + m5_l4, v3_path, variant="TITLE_PLUS_PHOTO_FULL"),
        "C1-B": entry(m5_l4.replace("\n\n", ""), v3_path, variant="PHOTO_FULL_SINGLE_PARAGRAPH"),
    }


def sentence_lengths(text: str) -> list[int]:
    pieces = [piece.strip() for piece in re.split(r"[。！？!?；;]+", text) if piece.strip()]
    return [len(piece) for piece in pieces]


def features(text: str, prefix_kind: str | None = None) -> dict[str, float]:
    chars = max(len(text), 1)
    lengths = sentence_lengths(text)
    mean = float(np.mean(lengths)) if lengths else 0.0
    std = float(np.std(lengths)) if lengths else 0.0
    dialogue_chars = 0
    for match in re.finditer(r"“([^”]*)”", text):
        dialogue_chars += len(match.group(1))
    punctuation = re.findall(r"[，。！？；：、,.!?;:\"'“”‘’]", text)
    ascii_punc = re.findall(r"[,\.!?;:\"']", text)
    explanation_markers = "因为所以于是因此判断认为说明结论可能显然其实意味着" 
    title = 1.0 if prefix_kind == "title" else 0.0
    date_author = 1.0 if prefix_kind in {"date", "author"} else 0.0
    return {
        "log_chars": math.log1p(chars),
        "paragraph_count": float(text.count("\n\n") + 1),
        "title_prefix": title,
        "prefix_kind_date_or_author": date_author,
        "sentence_mean": mean,
        "sentence_std": std,
        "short_sentence_ratio": (sum(length <= 12 for length in lengths) / len(lengths)) if lengths else 0.0,
        "dialogue_ratio": dialogue_chars / chars,
        "first_person_ratio": sum(text.count(token) for token in ("我", "我的", "我们")) / chars,
        "third_person_ratio": sum(text.count(token) for token in ("她", "他", "陈岚")) / chars,
        "explanation_marker_ratio": sum(text.count(token) for token in explanation_markers) / chars,
        "ascii_punctuation_ratio": (len(ascii_punc) / len(punctuation)) if punctuation else 0.0,
    }


def observed_score(report: dict[str, Any]) -> float:
    total = max(int(report["reported_chars"]), 1)
    return sum(float(segment["chars"]) * float(segment["score"]) for segment in report["segments"]) / total


def observed_class_shares(report: dict[str, Any]) -> dict[str, float]:
    total = max(int(report["reported_chars"]), 1)
    shares = {"HUMAN": 0.0, "SUSPECTED_AI": 0.0, "AI": 0.0}
    for segment in report["segments"]:
        score = float(segment["score"])
        cls = "HUMAN" if score < THRESHOLDS[0] else "SUSPECTED_AI" if score < THRESHOLDS[1] else "AI"
        shares[cls] += int(segment["chars"]) / total
    return shares


def fit(records: list[dict[str, Any]], alpha: float = 8.0) -> dict[str, Any]:
    x = np.array([[record["features"][name] for name in FEATURE_NAMES] for record in records], dtype=float)
    y = np.array([record["observed_score"] for record in records], dtype=float)
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0] = 1.0
    xs = (x - mean) / scale
    design = np.column_stack([np.ones(len(xs)), xs])
    penalty = np.eye(design.shape[1]) * alpha
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    return {
        "feature_names": FEATURE_NAMES,
        "mean": mean.tolist(),
        "scale": scale.tolist(),
        "feature_min": x.min(axis=0).tolist(),
        "feature_max": x.max(axis=0).tolist(),
        "beta": beta.tolist(),
        "alpha": alpha,
    }


def predict(model: dict[str, Any], feature_map: dict[str, float]) -> float:
    vector = np.array([feature_map[name] for name in model["feature_names"]], dtype=float)
    mean = np.array(model["mean"], dtype=float)
    scale = np.array(model["scale"], dtype=float)
    beta = np.array(model["beta"], dtype=float)
    value = float(np.dot(np.r_[1.0, (vector - mean) / scale], beta))
    return max(0.0, min(1.0, value))


def domain_status(model: dict[str, Any], feature_map: dict[str, float]) -> dict[str, Any]:
    vector = np.array([feature_map[name] for name in model["feature_names"]], dtype=float)
    lower = np.array(model["feature_min"], dtype=float)
    upper = np.array(model["feature_max"], dtype=float)
    outside = [
        name for name, value, low, high in zip(model["feature_names"], vector, lower, upper)
        if value < low or value > high
    ]
    return {
        "status": "IN_DOMAIN" if not outside else "OUT_OF_CALIBRATION_DOMAIN_UNTRUSTED",
        "outside_features": outside,
    }


def metrics(pairs: list[tuple[float, float]]) -> dict[str, float]:
    if not pairs:
        return {"count": 0, "mae": None, "rmse": None, "bias": None}
    deltas = np.array([pred - actual for actual, pred in pairs], dtype=float)
    return {
        "count": len(pairs),
        "mae": float(np.mean(np.abs(deltas))),
        "rmse": float(np.sqrt(np.mean(deltas**2))),
        "bias": float(np.mean(deltas)),
    }


def build_records(reports: dict[str, Any], texts: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    issues: list[str] = []
    for report in reports["reports"]:
        probe_id = report["probe_id"]
        source = texts.get(probe_id)
        if source is None:
            issues.append(f"{probe_id}: no source text mapping")
            continue
        text = source["text"]
        prefix_kind = source.get("prefix_kind")
        feature_map = features(text, prefix_kind)
        source_length = len(text)
        length_match = source_length == int(report["reported_chars"])
        identity = str(report.get("input_identity", "UNKNOWN"))
        comparability = str(report.get("comparability", "UNKNOWN"))
        excluded = (
            "MISMATCH" in identity
            or "MIXED_SOURCE" in comparability
            or "INVALID_INPUT_IDENTITY" in comparability
            or "CONFOUNDED_TWO_FACTOR" in comparability
        )
        if not length_match:
            issues.append(f"{probe_id}: planned source len {source_length} != report chars {report['reported_chars']}")
        records.append({
            "probe_id": probe_id,
            "group": probe_id.split("-", 1)[0],
            "text": text,
            "source": source,
            "features": feature_map,
            "source_length": source_length,
            "reported_chars": int(report["reported_chars"]),
            "length_match": length_match,
            "observed_score": observed_score(report),
            "observed_class_shares": observed_class_shares(report),
            "identity": identity,
            "comparability": comparability,
            "excluded_from_fit": excluded,
        })
    return records, issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--source-v1", type=Path, required=True)
    parser.add_argument("--source-v2", type=Path, required=True)
    parser.add_argument("--source-v3", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--score-text", type=Path)
    parser.add_argument("--score-prefix-kind", choices=["title", "date", "author"])
    parser.add_argument("--alpha", type=float, default=8.0)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    for path in (args.reports, args.source_v1, args.source_v2, args.source_v3):
        if not path.is_file():
            print(json.dumps({"result": "BLOCKED", "reason": f"missing file: {path}"}, ensure_ascii=False, indent=2))
            return 2

    reports = json.loads(args.reports.read_text(encoding="utf-8-sig"))
    texts = source_texts(args.source_v1, args.source_v2, args.source_v3)
    records, issues = build_records(reports, texts)
    eligible = [record for record in records if not record["excluded_from_fit"] and record["length_match"]]
    if len(eligible) < 6:
        print(json.dumps({"result": "BLOCKED", "reason": "fewer than six eligible calibration records", "issues": issues}, ensure_ascii=False, indent=2))
        return 2

    model = fit(eligible, args.alpha)
    training_pairs = [(record["observed_score"], predict(model, record["features"])) for record in eligible]
    global_mean = float(np.mean([record["observed_score"] for record in eligible]))
    baseline_training_pairs = [(record["observed_score"], global_mean) for record in eligible]
    group_cv: list[dict[str, Any]] = []
    group_pairs: list[tuple[float, float]] = []
    baseline_group_pairs: list[tuple[float, float]] = []
    for group in sorted({record["group"] for record in eligible}):
        train = [record for record in eligible if record["group"] != group]
        test = [record for record in eligible if record["group"] == group]
        if len(train) < 6:
            continue
        fold_model = fit(train, args.alpha)
        fold_mean = float(np.mean([record["observed_score"] for record in train]))
        fold_rows = []
        for record in test:
            pred = predict(fold_model, record["features"])
            group_pairs.append((record["observed_score"], pred))
            baseline_group_pairs.append((record["observed_score"], fold_mean))
            fold_rows.append({"probe_id": record["probe_id"], "observed": record["observed_score"], "predicted": pred, "delta": pred - record["observed_score"]})
        group_cv.append({"held_out_group": group, "rows": fold_rows})

    rows = []
    for record in records:
        pred = predict(model, record["features"])
        rows.append({
            "probe_id": record["probe_id"],
            "group": record["group"],
            "excluded_from_fit": record["excluded_from_fit"],
            "source_length": record["source_length"],
            "reported_chars": record["reported_chars"],
            "length_match": record["length_match"],
            "observed_weighted_score": record["observed_score"],
            "shadow_predicted_score_full_fit": pred,
            "full_fit_delta": pred - record["observed_score"],
            "observed_class_shares": record["observed_class_shares"],
            "input_identity": record["identity"],
            "comparability": record["comparability"],
        })

    output: dict[str, Any] = {
        "schema": "SHADOW_DETECTOR_SCORER_V1",
        "result": "SHADOW_SURROGATE_ONLY",
        "warning": "not a reconstruction of a private detector; no authorship or evasion claim",
        "fit_scope": "eligible records only; identity-mismatched, mixed-source, confounded diagonal and length-mismatched records excluded",
        "alpha": args.alpha,
        "feature_names": FEATURE_NAMES,
        "eligible_count": len(eligible),
        "all_record_count": len(records),
        "model": model,
        "baseline_mean_score": global_mean,
        "baseline_training_metrics": metrics(baseline_training_pairs),
        "training_metrics": metrics(training_pairs),
        "group_blocked_cv_metrics": metrics(group_pairs),
        "baseline_group_blocked_cv_metrics": metrics(baseline_group_pairs),
        "group_blocked_cv": group_cv,
        "rows": rows,
        "source_issues": issues,
        "not_executed": ["PDF_OCR", "DETECTOR_CALL", "PRIVATE_ALGORITHM_INFERENCE", "PRODUCTION_PROSE_CHANGE"],
        "production_visible": False,
    }

    if args.score_text:
        text = args.score_text.read_text(encoding="utf-8")
        fmap = features(text, args.score_prefix_kind)
        predicted = predict(model, fmap)
        output["arbitrary_text_score"] = {
            "path": str(args.score_text),
            "sha256": sha256_file(args.score_text),
            "chars": len(text),
            "predicted_score": predicted,
            "predicted_class": "HUMAN" if predicted < 0.5 else "SUSPECTED_AI" if predicted < 0.99 else "AI",
            "inference_status": domain_status(model, fmap),
            "features": fmap,
            "shape_shadow": {
                "paragraph_count": text.count("\n\n") + 1,
                "title_prefix": bool(args.score_prefix_kind == "title"),
                "estimated_segment_count": 2 if (args.score_prefix_kind == "title" or (len(text) > 800 and text.count("\n\n") + 1 <= 4)) else 1,
                "warning": "estimated parser shape, not detector output",
            },
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {
        "result": output["result"],
        "eligible_count": len(eligible),
        "all_record_count": len(records),
        "training_metrics": output["training_metrics"],
        "group_blocked_cv_metrics": output["group_blocked_cv_metrics"],
        "baseline_group_blocked_cv_metrics": output["baseline_group_blocked_cv_metrics"],
        "output": str(args.out),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not args.strict or not issues else 1


if __name__ == "__main__":
    sys.exit(main())
