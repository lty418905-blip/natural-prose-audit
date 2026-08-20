#!/usr/bin/env python3
"""Emit non-blocking shape warnings for Chinese prose. Never edits text."""

from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
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

ACTION_MARKERS = (
    "抬眼", "抬头", "低头", "看着", "看了", "停手", "放下", "放回",
    "敲了", "点了点", "转过身", "往前", "后退", "站在", "挪了",
    "收回手", "推开", "推到", "拿起", "握住", "攥住",
)

EXPLANATION_TAIL_PREFIXES = (
    "这说明", "这意味着", "也就是说", "换句话说", "显然", "我意识到",
    "我明白", "我知道", "原来", "事实上", "其实这", "可见",
)

ANSWER_CLOSURE_PREFIXES = (
    "是", "不是", "有", "没有", "能", "不能", "会", "不会", "因为",
    "当然", "意思是", "也就是说", "指的是", "这说明", "这意味着",
)

QUOTE_SPAN_PATTERN = re.compile(r'[“「"](?P<body>[^”」"\n]{1,220})[”」"]')
VISIBLE_TEXT_PATTERN = re.compile(r"[^\u3400-\u4dbf\u4e00-\u9fffA-Za-z0-9]")


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[。！？!?…])", text) if s.strip()]


def visible_length(sentence: str) -> int:
    return len(re.sub(r"\s|[，。！？!?；;：:\"'“”‘’（）()《》〈〉…]", "", sentence))


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def locate_units(text: str, units: list[str]) -> list[tuple[int, int]]:
    """Map already-split units back to inclusive source line ranges."""
    located: list[tuple[int, int]] = []
    cursor = 0
    for unit in units:
        start = text.find(unit, cursor)
        if start < 0:
            start = text.find(unit)
        if start < 0:
            located.append((1, 1))
            continue
        end = start + len(unit)
        located.append((
            line_for_offset(text, start),
            line_for_offset(text, max(start, end - 1)),
        ))
        cursor = end
    return located


def normalize_overlap_text(text: str) -> str:
    return VISIBLE_TEXT_PATTERN.sub("", text)


def source_label(path: Path, show_source_path: bool) -> str:
    return str(path.resolve()) if show_source_path else path.name


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


def rhythm_findings(sentences: list[str], include_excerpts: bool) -> list[dict]:
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
                "action": "review_in_context",
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
                    "action": "review_in_context",
                })
            run_start = None

    for i in range(max(0, len(sentences) - 2)):
        starts = [re.sub(r"^[\s\"'“”‘’（(]+", "", s)[:2] for s in sentences[i:i + 3]]
        if starts[0] and len(set(starts)) == 1:
            finding = {
                "type": "repeated_sentence_start",
                "sentence_range": [i + 1, i + 3],
                "action": "review_in_context",
            }
            if include_excerpts:
                finding["start_excerpt"] = starts[0]
            findings.append(finding)
    return findings


def pattern_findings(text: str, include_excerpts: bool) -> list[dict]:
    patterns = {
        "reversal_template": r"不是[^。！？\n]{0,45}(?:而是|是)[^。！？\n]{0,45}",
        "three_step_transition": r"首先[^。！？\n]{0,120}其次[^。！？\n]{0,120}最后",
    }
    findings: list[dict] = []
    for kind, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            finding = {
                "type": kind,
                "line": line_for_offset(text, match.start()),
                "action": "review_semantic_function",
            }
            if include_excerpts:
                finding["excerpt"] = match.group(0)[:80]
            findings.append(finding)
    return findings


def adjacent_paragraph_overlap_findings(
    paragraphs: list[str],
    paragraph_lines: list[tuple[int, int]],
    include_excerpts: bool,
) -> list[dict]:
    """Flag substantial verbatim overlap in adjacent paragraphs.

    This catches possible assembly duplication. Short refrains and shared names
    are deliberately below threshold; every hit still requires human review.
    """
    findings: list[dict] = []
    for index in range(len(paragraphs) - 1):
        left = normalize_overlap_text(paragraphs[index])
        right = normalize_overlap_text(paragraphs[index + 1])
        shorter = min(len(left), len(right))
        if shorter < 16:
            continue
        match = SequenceMatcher(None, left, right, autojunk=False).find_longest_match(
            0, len(left), 0, len(right)
        )
        overlap_share = match.size / shorter
        if match.size < 12 or (match.size < 24 and overlap_share < 0.35):
            continue
        finding = {
            "type": "adjacent_paragraph_overlap_candidate",
            "paragraph_range": [index + 1, index + 2],
            "line_range": [paragraph_lines[index][0], paragraph_lines[index + 1][1]],
            "overlap_characters": match.size,
            "action": "review_flag",
            "note": (
                "Verify possible assembly duplication; preserve intentional refrains, "
                "quoted evidence, and plot-bearing repetition."
            ),
        }
        if include_excerpts:
            finding["overlap_excerpt"] = left[match.a:match.a + match.size][:80]
        findings.append(finding)
    return findings


def action_explanation_tail_findings(
    text: str,
    sentences: list[str],
    sentence_lines: list[tuple[int, int]],
) -> list[dict]:
    """Flag an observable action followed immediately by an interpretive tail."""
    findings: list[dict] = []
    for index in range(len(sentences) - 1):
        action_sentence = sentences[index]
        explanation = re.sub(r'^[\s”」\"“「]+', "", sentences[index + 1])
        if not any(marker in action_sentence for marker in ACTION_MARKERS):
            continue
        explicit_tail = explanation.startswith(EXPLANATION_TAIL_PREFIXES)
        person_tail = re.match(
            r"^(?:他|她|我|他们|她们|这)[^。！？!?]{0,10}(?:是在|其实是在|显然是|无非是)",
            explanation,
        )
        if not explicit_tail and person_tail is None:
            continue
        findings.append({
            "type": "action_explanation_tail_candidate",
            "sentence_range": [index + 1, index + 2],
            "line_range": [sentence_lines[index][0], sentence_lines[index + 1][1]],
            "action": "review_flag",
            "note": (
                "Check whether the explanation repeats an already legible action. "
                "Keep it when it changes knowledge, causality, evidence strength, or relationship meaning."
            ),
        })
    return findings


def answer_looks_closed(answer: str) -> bool:
    answer = answer.strip()
    return any(answer.startswith(marker) for marker in ANSWER_CLOSURE_PREFIXES) or any(
        marker in answer for marker in ("意思是", "也就是说", "这说明", "这意味着")
    )


def dialogue_qa_closure_findings(text: str) -> list[dict]:
    """Flag clusters of tidily closed quoted question-answer pairs."""
    quotes = list(QUOTE_SPAN_PATTERN.finditer(text))
    pairs: list[tuple[int, int]] = []
    for index in range(len(quotes) - 1):
        question = quotes[index]
        answer = quotes[index + 1]
        question_text = question.group("body").strip()
        answer_text = answer.group("body").strip()
        if not question_text.endswith(("？", "?")):
            continue
        if answer_text.endswith(("？", "?")):
            continue
        if answer.start() - question.end() > 240:
            continue
        if answer_looks_closed(answer_text):
            pairs.append((question.start(), answer.end()))

    findings: list[dict] = []
    for start in range(len(pairs)):
        cluster = [pair for pair in pairs[start:] if pair[0] - pairs[start][0] <= 1600]
        if len(cluster) < 3:
            continue
        findings.append({
            "type": "dialogue_qa_closure_cluster_candidate",
            "line_range": [
                line_for_offset(text, cluster[0][0]),
                line_for_offset(text, cluster[-1][1]),
            ],
            "closed_pair_count": len(cluster),
            "action": "review_flag",
            "note": (
                "Check whether every question needs an immediate complete answer. "
                "Preserve accurate exposition, character-specific banter, interruptions, and deliberate ritual form."
            ),
        })
        break
    return findings


def sentence_start_counts(sentences: list[str]) -> Counter[str]:
    starts: Counter[str] = Counter()
    for sentence in sentences:
        cleaned = re.sub(r'^[\s\"\'“”‘’「」—（(]+', "", sentence)
        match = re.search(r"[\u3400-\u4dbf\u4e00-\u9fffA-Za-z0-9]{2}", cleaned)
        if match:
            starts[match.group(0)] += 1
    return starts


def punctuation_habits(text: str, sentence_count: int) -> set[str]:
    habits: set[str] = set()
    if text.count("……") + text.count("...") >= 2:
        habits.add("repeated_ellipsis")
    if text.count("——") + text.count("—") >= 2:
        habits.add("repeated_dash")
    if text.count("；") + text.count(";") >= 2:
        habits.add("semicolon_recurrence")
    questions = text.count("？") + text.count("?")
    if questions >= 3 and questions * 5 >= max(1, sentence_count):
        habits.add("question_dense")
    if len(QUOTE_SPAN_PATTERN.findall(text)) >= 4:
        habits.add("quoted_dialogue_present")
    return habits


def dominant_length_band(sentences: list[str]) -> str:
    counts = Counter()
    for sentence in sentences:
        length = visible_length(sentence)
        if length <= 9:
            counts["compressed"] += 1
        elif length >= 28:
            counts["extended"] += 1
        else:
            counts["middle"] += 1
    if not counts:
        return "not_available"
    most_common = counts.most_common()
    if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
        return "mixed"
    return most_common[0][0]


def voice_profile(text: str) -> dict:
    sentences = split_sentences(text)
    starts = sentence_start_counts(sentences)
    marked_phrases = {
        term for term in TRANSITIONS + AUTHOR_METAPHORS + NOVEL_CLICHES
        if text.count(term) >= 2
    }
    return {
        "repeated_starts": {term for term, count in starts.items() if count >= 2},
        "marked_phrases": marked_phrases,
        "punctuation_habits": punctuation_habits(text, len(sentences)),
        "dominant_length_band": dominant_length_band(sentences),
    }


def compare_voice_candidates(
    source_text: str,
    reference_path: Path,
    show_source_path: bool,
    include_excerpts: bool,
) -> dict:
    reference_bytes = reference_path.read_bytes()
    reference_text = reference_bytes.decode("utf-8")
    source_profile = voice_profile(source_text)
    reference_profile = voice_profile(reference_text)
    shared_starts = sorted(source_profile["repeated_starts"] & reference_profile["repeated_starts"])
    shared_phrases = sorted(source_profile["marked_phrases"] & reference_profile["marked_phrases"])
    shared_habits = sorted(
        source_profile["punctuation_habits"] & reference_profile["punctuation_habits"]
    )
    candidate_dimensions: list[str] = []
    if shared_starts:
        candidate_dimensions.append("repeated_sentence_starts")
    if shared_phrases:
        candidate_dimensions.append("repeated_marked_phrases")
    if shared_habits:
        candidate_dimensions.append("punctuation_habits")
    source_band = source_profile["dominant_length_band"]
    reference_band = reference_profile["dominant_length_band"]
    if source_band == reference_band and source_band not in ("mixed", "not_available"):
        candidate_dimensions.append("dominant_sentence_length_band")

    result = {
        "reference_source": source_label(reference_path, show_source_path),
        "reference_source_sha256": hashlib.sha256(reference_bytes).hexdigest(),
        "candidate_dimensions": candidate_dimensions,
        "candidate_dimension_counts": {
            "repeated_sentence_starts": len(shared_starts),
            "repeated_marked_phrases": len(shared_phrases),
            "punctuation_habits": len(shared_habits),
        },
        "dominant_sentence_length_bands": {
            "source": source_band,
            "reference": reference_band,
        },
        "status": "candidate_only_requires_human_review",
        "note": (
            "Observable overlap is not a similarity score, authorship attribution, defect finding, "
            "or permission to normalize either document's voice."
        ),
    }
    if include_excerpts:
        result["shared_repeated_sentence_start_excerpts"] = shared_starts[:12]
        result["shared_marked_phrase_excerpts"] = shared_phrases[:12]
        result["shared_punctuation_habits"] = shared_habits
    return result


def analyze(
    path: Path,
    mode: str,
    *,
    include_excerpts: bool = False,
    show_source_path: bool = False,
    voice_references: list[Path] | None = None,
) -> dict:
    source_bytes = path.read_bytes()
    text = source_bytes.decode("utf-8")
    sentences = split_sentences(text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    sentence_lines = locate_units(text, sentences)
    paragraph_lines = locate_units(text, paragraphs)

    findings = lexical_findings(text, mode)
    findings += rhythm_findings(sentences, include_excerpts)
    findings += pattern_findings(text, include_excerpts)
    findings += adjacent_paragraph_overlap_findings(
        paragraphs, paragraph_lines, include_excerpts
    )
    findings += action_explanation_tail_findings(text, sentences, sentence_lines)
    findings += dialogue_qa_closure_findings(text)

    result = {
        "schema": "natural_prose_audit_v2",
        "source": source_label(path, show_source_path),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "source_path_policy": "absolute_path_opt_in" if show_source_path else "filename_only_default",
        "excerpt_policy": "short_excerpts_opt_in" if include_excerpts else "no_excerpts_default",
        "mode": mode,
        "statistics": {
            "characters": len(text),
            "sentences": len(sentences),
            "paragraphs": len(paragraphs),
        },
        "finding_count": len(findings),
        "finding_count_semantics": "inventory_count_only_not_a_risk_score",
        "findings": findings,
        "verdict": "warnings_only_no_detector_claim",
    }
    if voice_references:
        result["voice_candidate_comparisons"] = [
            compare_voice_candidates(text, reference, show_source_path, include_excerpts)
            for reference in voice_references
        ]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-blocking naturalness audit for Chinese prose")
    parser.add_argument("text_path", type=Path)
    parser.add_argument("--mode", choices=("fiction", "general"), default="fiction")
    parser.add_argument(
        "--voice-reference",
        type=Path,
        action="append",
        default=[],
        help=(
            "optional comparison document; may be repeated and emits candidate dimensions only, "
            "never a similarity or risk score"
        ),
    )
    parser.add_argument(
        "--show-source-path",
        action="store_true",
        help="opt in to absolute source paths in JSON output",
    )
    parser.add_argument(
        "--include-excerpts",
        action="store_true",
        help="opt in to short excerpts (capped at 80 characters) for pattern localization",
    )
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    if not args.text_path.is_file():
        parser.error(f"file not found: {args.text_path}")
    missing_references = [path for path in args.voice_reference if not path.is_file()]
    if missing_references:
        parser.error(f"voice reference not found: {missing_references[0]}")
    result = analyze(
        args.text_path,
        args.mode,
        include_excerpts=args.include_excerpts,
        show_source_path=args.show_source_path,
        voice_references=args.voice_reference,
    )
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
