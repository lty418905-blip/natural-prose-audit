#!/usr/bin/env python3
"""Emit non-blocking shape warnings for Chinese prose. Never edits text."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path


TRANSITIONS = (
    "首先", "其次", "最后", "此外", "另外", "与此同时", "综上所述",
    "值得注意的是", "需要指出的是", "从某种意义上说",
)

AUTHOR_METAPHORS = ("算账", "这笔账", "把账算清")

NOVEL_CLICHES = (
    "瞳孔骤缩", "倒吸一口凉气", "空气仿佛凝固", "满场死寂",
    "眼中闪过一丝", "嘴角上扬", "攥紧了拳头",
)


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[。！？!?…])", text) if s.strip()]


def visible_length(sentence: str) -> int:
    return len(re.sub(r"\s|[，。！？!?；;：:\"'“”‘’（）()《》〈〉…]", "", sentence))


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def lexical_findings(text: str, mode: str) -> list[dict]:
    terms = [(x, "transition") for x in TRANSITIONS]
    terms += [(x, "author_metaphor") for x in AUTHOR_METAPHORS]
    if mode == "fiction":
        terms += [(x, "novel_cliche") for x in NOVEL_CLICHES]

    findings: list[dict] = []
    for term, kind in terms:
        starts = [m.start() for m in re.finditer(re.escape(term), text)]
        if not starts:
            continue
        findings.append({
            "type": kind,
            "term": term,
            "count": len(starts),
            "lines": [line_for_offset(text, p) for p in starts[:12]],
            "action": "review_in_context",
        })
    return findings


def rhythm_findings(sentences: list[str]) -> list[dict]:
    findings: list[dict] = []
    lengths = [visible_length(s) for s in sentences]

    for i in range(max(0, len(lengths) - 4)):
        window = lengths[i:i + 5]
        mean = statistics.fmean(window)
        if mean and statistics.pstdev(window) / mean < 0.12:
            findings.append({
                "type": "uniform_sentence_window",
                "sentence_range": [i + 1, i + 5],
                "lengths": window,
                "action": "read_aloud_then_keep_or_rephrase",
            })

    run_start = None
    for i, length in enumerate(lengths + [999]):
        if length <= 7 and run_start is None:
            run_start = i
        elif length > 7 and run_start is not None:
            if i - run_start >= 4:
                findings.append({
                    "type": "short_sentence_run",
                    "sentence_range": [run_start + 1, i],
                    "action": "keep_if_scene_pressure_supports_it",
                })
            run_start = None

    for i in range(max(0, len(sentences) - 2)):
        starts = [re.sub(r"^[\s\"'“”‘’（(]+", "", s)[:2] for s in sentences[i:i + 3]]
        if starts[0] and len(set(starts)) == 1:
            findings.append({
                "type": "repeated_sentence_start",
                "sentence_range": [i + 1, i + 3],
                "start": starts[0],
                "action": "review_in_context",
            })
    return findings


def pattern_findings(text: str) -> list[dict]:
    patterns = {
        "reversal_template": r"不是[^。！？\n]{0,45}(?:而是|是)[^。！？\n]{0,45}",
        "three_step_transition": r"首先[^。！？\n]{0,120}其次[^。！？\n]{0,120}最后",
    }
    findings: list[dict] = []
    for kind, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            findings.append({
                "type": kind,
                "line": line_for_offset(text, match.start()),
                "excerpt": match.group(0)[:80],
                "action": "review_semantic_function",
            })
    return findings


def analyze(path: Path, mode: str) -> dict:
    text = path.read_text(encoding="utf-8")
    sentences = split_sentences(text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    findings = lexical_findings(text, mode)
    findings += rhythm_findings(sentences)
    findings += pattern_findings(text)
    return {
        "schema": "natural_prose_audit_v1",
        "source": str(path.resolve()),
        "mode": mode,
        "statistics": {
            "characters": len(text),
            "sentences": len(sentences),
            "paragraphs": len(paragraphs),
        },
        "finding_count": len(findings),
        "findings": findings,
        "verdict": "warnings_only_no_detector_claim",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-blocking naturalness audit for Chinese prose")
    parser.add_argument("text_path", type=Path)
    parser.add_argument("--mode", choices=("fiction", "general"), default="fiction")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    if not args.text_path.is_file():
        parser.error(f"file not found: {args.text_path}")
    result = analyze(args.text_path, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

