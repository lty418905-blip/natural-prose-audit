#!/usr/bin/env python3
"""Post-assembly prose hygiene gate for the controlled prose workflow.

This scanner is deliberately narrow: it locates editorial residue that can be
checked without deciding story semantics.  Near-duplicate findings remain a
human literary decision; hard findings cannot be waived by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


SCHEMA = "POST_ASSEMBLY_TEXT_HYGIENE_RESULT_V1"
INTERNAL_MARKERS = (
    "CANDIDATE_ONLY",
    "NOT_A_FACT_SOURCE",
    "CALL_MANIFEST",
    "CARD_PAYLOAD_BEGIN",
    "CARD_PAYLOAD_END",
    "PART_1",
    "PART_2",
    "PART_3",
    "TODO",
    "FIXME",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def norm_paragraph(text: str) -> str:
    return re.sub(r"[\s\u3000\W_]+", "", text, flags=re.UNICODE)


def finding_id(kind: str, locations: list[int], evidence: str) -> str:
    raw = f"{kind}|{','.join(map(str, locations))}|{evidence}".encode("utf-8")
    return f"HYGIENE-{kind}-{hashlib.sha256(raw).hexdigest()[:12].upper()}"


def add_finding(items: list[dict], kind: str, severity: str,
                locations: list[int], evidence: str, message: str) -> None:
    items.append({
        "finding_id": finding_id(kind, locations, evidence),
        "kind": kind,
        "severity": severity,
        "paragraph_indices_1_based": locations,
        "evidence": evidence[:240],
        "message": message,
    })


def load_obsolete_register(path: Path | None, prose_sha: str) -> list[dict]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "OBSOLETE_TERM_REGISTER_V1":
        raise ValueError("obsolete register schema must be OBSOLETE_TERM_REGISTER_V1")
    bound = payload.get("candidate_prose_sha256")
    if bound and bound.upper() != prose_sha:
        raise ValueError("obsolete register candidate_prose_sha256 mismatch")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("obsolete register entries must be a list")
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("term") or not entry.get("reason"):
            raise ValueError("each obsolete entry requires term and reason")
    return entries


def scan(text: str, obsolete_entries: list[dict]) -> tuple[list[dict], dict]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    findings: list[dict] = []

    exact: dict[str, list[int]] = {}
    normalized: dict[str, list[int]] = {}
    for index, paragraph in enumerate(paragraphs, start=1):
        if len(paragraph) >= 24:
            exact.setdefault(paragraph, []).append(index)
        normalized_text = norm_paragraph(paragraph)
        if len(normalized_text) >= 24:
            normalized.setdefault(normalized_text, []).append(index)

    for paragraph, locations in exact.items():
        if len(locations) > 1 and max(locations) - min(locations) > 1:
            add_finding(findings, "EXACT_DISTANT_PARAGRAPH_DUPLICATE", "HARD_BLOCK",
                        locations, paragraph, "非相邻段落逐字重复")

    exact_keys = set(exact)
    for normalized_text, locations in normalized.items():
        if len(locations) > 1 and max(locations) - min(locations) > 1:
            originals = [paragraphs[i - 1] for i in locations]
            if not all(item in exact_keys and exact[item] == locations for item in originals):
                add_finding(findings, "NORMALIZED_DISTANT_PARAGRAPH_DUPLICATE", "HARD_BLOCK",
                            locations, normalized_text, "非相邻段落仅标点或空白不同，归一化后重复")

    for left in range(len(paragraphs)):
        a = norm_paragraph(paragraphs[left])
        if len(a) < 48:
            continue
        for right in range(left + 2, len(paragraphs)):
            b = norm_paragraph(paragraphs[right])
            if len(b) < 48 or a == b:
                continue
            ratio = SequenceMatcher(None, a, b, autojunk=False).ratio()
            if ratio >= 0.86:
                evidence = f"similarity={ratio:.4f}; left={paragraphs[left][:100]}; right={paragraphs[right][:100]}"
                add_finding(findings, "DISTANT_NEAR_DUPLICATE_PARAGRAPHS", "REVIEW_REQUIRED",
                            [left + 1, right + 1], evidence,
                            "非相邻段落高度近似，需判断必要复现或同一洞察重复")

    curly_open = text.count("“")
    curly_close = text.count("”")
    ascii_quotes = text.count('"')
    if curly_open != curly_close:
        add_finding(findings, "UNBALANCED_CURLY_QUOTES", "HARD_BLOCK", [],
                    f"open={curly_open}; close={curly_close}", "中文弯引号不平衡")
    if ascii_quotes % 2:
        add_finding(findings, "UNBALANCED_ASCII_QUOTES", "HARD_BLOCK", [],
                    f"count={ascii_quotes}", "ASCII直引号不平衡")
    if ascii_quotes and (curly_open or curly_close):
        add_finding(findings, "MIXED_DIALOGUE_QUOTE_FAMILIES", "HARD_BLOCK", [],
                    f"curly_open={curly_open}; curly_close={curly_close}; ascii={ascii_quotes}",
                    "同一正文混用中文弯引号与ASCII直引号")

    ascii_punctuation = {
        "ASCII_COMMA": len(re.findall(r"(?<!\d),(?!\d)", text)),
        "ASCII_COLON": text.count(":"),
        "ASCII_SEMICOLON": text.count(";"),
    }
    for kind, count in ascii_punctuation.items():
        if count:
            add_finding(findings, kind, "REVIEW_REQUIRED", [], f"count={count}",
                        "正文含半角标点；核对是否为必要原文、URL或格式残留")

    for marker in INTERNAL_MARKERS:
        if marker in text:
            add_finding(findings, "INTERNAL_PROCESS_MARKER_LEAK", "HARD_BLOCK", [], marker,
                        "正文泄漏内部流程或装配标记")

    for entry in obsolete_entries:
        term = entry["term"]
        allowed = set(entry.get("allowed_exact_contexts", []))
        start = 0
        while True:
            position = text.find(term, start)
            if position < 0:
                break
            context = text[max(0, position - 40): position + len(term) + 40]
            if context not in allowed:
                add_finding(findings, "OBSOLETE_TERM_MATCH", "HARD_BLOCK", [],
                            f"term={term}; offset={position}; context={context}", entry["reason"])
            start = position + max(1, len(term))

    stats = {
        "paragraph_count": len(paragraphs),
        "curly_quote_open_count": curly_open,
        "curly_quote_close_count": curly_close,
        "ascii_quote_count": ascii_quotes,
        **{key.lower() + "_count": value for key, value in ascii_punctuation.items()},
    }
    return findings, stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prose")
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--obsolete-register")
    args = parser.parse_args()

    prose_path = Path(args.prose).resolve()
    raw = prose_path.read_bytes()
    text = raw.decode("utf-8")
    prose_sha = sha256_bytes(raw)
    register_path = Path(args.obsolete_register).resolve() if args.obsolete_register else None
    obsolete_entries = load_obsolete_register(register_path, prose_sha)
    findings, stats = scan(text, obsolete_entries)
    hard_count = sum(item["severity"] == "HARD_BLOCK" for item in findings)
    review_count = sum(item["severity"] == "REVIEW_REQUIRED" for item in findings)
    result = "HARD_BLOCK" if hard_count else ("REVIEW_REQUIRED" if review_count else "PASS")
    payload = {
        "schema": SCHEMA,
        "object_id": args.object_id,
        "prose_path": str(prose_path),
        "prose_sha256": prose_sha,
        "prose_bytes": len(raw),
        "obsolete_register_path": str(register_path) if register_path else None,
        "result": result,
        "hard_block_count": hard_count,
        "review_required_count": review_count,
        "statistics": stats,
        "findings": findings,
    }
    output_path = Path(args.output).resolve()
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": result, "output": str(output_path),
                      "hard_block_count": hard_count,
                      "review_required_count": review_count}, ensure_ascii=False))
    return 0 if result == "PASS" else (2 if result == "HARD_BLOCK" else 3)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # fail closed with a concise, machine-visible error
        print(json.dumps({"result": "ERROR", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(4)
