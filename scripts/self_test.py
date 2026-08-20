#!/usr/bin/env python3
"""Offline checks for the generic natural-prose-audit scripts."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Callable, Iterator


@contextmanager
def temporary_files(parent: Path) -> Iterator[Callable[[str], Path]]:
    """Create flat temporary files; the sandbox permits files but not new dirs."""
    paths: list[Path] = []

    def make_file(suffix: str = ".tmp") -> Path:
        handle = tempfile.NamedTemporaryFile(
            dir=parent, prefix="audit_self_", suffix=suffix, delete=False
        )
        path = Path(handle.name)
        handle.close()
        paths.append(path)
        return path

    try:
        yield make_file
    finally:
        for path in paths:
            try:
                path.unlink()
            except FileNotFoundError:
                pass


def run_json(command: list[str], expected_code: int = 0) -> dict:
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    run = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=child_env,
    )
    if run.returncode != expected_code:
        raise SystemExit(
            f"unexpected exit code {run.returncode} (wanted {expected_code}): {run.stderr}"
        )
    try:
        return json.loads(run.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"child did not emit JSON: {run.stdout!r}") from exc


def finding_types(result: dict) -> set[str]:
    return {item.get("type") for item in result.get("findings", [])}


def assert_absent(value: str, *needles: str) -> None:
    for needle in needles:
        if needle in value:
            raise SystemExit(f"privacy boundary failed; found {needle!r}")


def main() -> int:
    scripts = Path(__file__).parent
    audit_script = scripts / "audit_prose.py"
    validator_script = scripts / "validate_ai_trace_record.py"
    fixture = (scripts / "self_test_fixture.txt").read_text(encoding="utf-8")

    positive = fixture + """

他把蓝色搪瓷杯推到窗边，杯底擦过木桌，发出一声短响。走廊尽头有人关门。

他把蓝色搪瓷杯推到窗边，杯底擦过木桌，发出一声短响。只是这次没人回头。

他抬眼看了看门。这说明他已经知道有人来过。

“你为什么回来？”
“因为钥匙还在这里。”

“门能打开吗？”
“不能，这意味着锁已经换过。”

“我们现在走吗？”
“是，也就是说，不能再等。”
"""
    protective = """
“别怕。”

“别怕。”

他把杯子放在桌上。杯沿碰到木头，水晃了一下。

“你来吗？”
她没有回答，只把窗帘拉开。
"""

    with temporary_files(scripts.parent) as make_file:
        source = make_file(".txt")
        source.write_text(positive, encoding="utf-8", newline="")
        reference = make_file(".txt")
        reference.write_text(
            "他把纸放在桌上。他把门推开。\n\n他把灯关掉。首先，等一等。",
            encoding="utf-8",
            newline="",
        )
        negative = make_file(".txt")
        negative.write_text(protective, encoding="utf-8", newline="")

        audit_command = [sys.executable, "-B", str(audit_script), str(source), "--compact"]
        result = run_json(audit_command)
        types = finding_types(result)
        required = {
            "transition",
            "author_metaphor",
            "reversal_template",
            "repeated_sentence_start",
            "adjacent_paragraph_overlap_candidate",
            "action_explanation_tail_candidate",
            "dialogue_qa_closure_cluster_candidate",
        }
        missing = sorted(required - types)
        if missing:
            raise SystemExit(f"missing expected findings: {missing}; got {sorted(types)}")
        if result["verdict"] != "warnings_only_no_detector_claim":
            raise SystemExit("verdict boundary changed")
        if result["source"] != source.name:
            raise SystemExit(f"default source label leaked or changed: {result['source']!r}")
        expected_sha = hashlib.sha256(source.read_bytes()).hexdigest()
        if result["source_sha256"] != expected_sha:
            raise SystemExit("source SHA was not computed from source bytes")
        if result["finding_count_semantics"] != "inventory_count_only_not_a_risk_score":
            raise SystemExit("finding_count semantics boundary changed")
        dumped = json.dumps(result, ensure_ascii=False)
        assert_absent(
            dumped,
            str(source.resolve()).replace("\\", "\\\\"),
            positive[:42],
            "他把",
        )
        if any("excerpt" in item for item in result["findings"]):
            raise SystemExit("long excerpts are exposed by default")

        opted_in = run_json(audit_command + ["--show-source-path", "--include-excerpts"])
        opted_dumped = json.dumps(opted_in, ensure_ascii=False)
        if opted_in["source"] != str(source.resolve()):
            raise SystemExit("explicit source-path opt-in did not work")
        if not any("excerpt" in item for item in opted_in["findings"]):
            raise SystemExit("explicit excerpt opt-in did not work")

        negative_result = run_json(
            [sys.executable, "-B", str(audit_script), str(negative), "--compact"]
        )
        negative_types = finding_types(negative_result)
        protected_flags = {
            "adjacent_paragraph_overlap_candidate",
            "action_explanation_tail_candidate",
            "dialogue_qa_closure_cluster_candidate",
        }
        unexpected = sorted(protected_flags & negative_types)
        if unexpected:
            raise SystemExit(f"protective negative produced false-positive flags: {unexpected}")

        compared = run_json(audit_command + ["--voice-reference", str(reference)])
        comparisons = compared.get("voice_candidate_comparisons", [])
        if len(comparisons) != 1:
            raise SystemExit("cross-document voice comparison missing")
        comparison = comparisons[0]
        if comparison["status"] != "candidate_only_requires_human_review":
            raise SystemExit("voice comparison escaped candidate-only status")
        if comparison["reference_source"] != reference.name:
            raise SystemExit("voice comparison leaked an absolute path")
        if not comparison["candidate_dimensions"]:
            raise SystemExit("voice comparison produced no observable candidate dimension")
        if "similarity_score" in json.dumps(comparison, ensure_ascii=False):
            raise SystemExit("voice comparison emitted a similarity score")
        comparison_dumped = json.dumps(comparison, ensure_ascii=False)
        assert_absent(comparison_dumped, "他把", "这笔账")
        if any(key.endswith("_excerpts") for key in comparison):
            raise SystemExit("cross-document comparison exposed excerpts by default")

        compared_opted_in = run_json(
            audit_command
            + ["--voice-reference", str(reference), "--include-excerpts"]
        )
        opted_comparison = compared_opted_in["voice_candidate_comparisons"][0]
        if not any(key.endswith("_excerpts") for key in opted_comparison):
            raise SystemExit("voice comparison excerpt opt-in did not work")

        record = {
            "schema": "NATURAL_PROSE_AI_TRACE_RECORD_V1",
            "mode": "PRE_REVISION",
            "source": {"path": str(source.resolve()), "sha256": expected_sha},
            "detector_evidence_status": "ORDERING_ONLY",
            "cold_read_locked_before_detector": True,
            "primary_finding": {
                "id": "LOCAL_ACTION_TAIL",
                "class": "EXPLANATION",
                "scope": "LOCAL",
                "evidence_ranges": [
                    {"unit": "UTF8_BYTE", "start": 0, "end": 80}
                ],
                "voice_protection": ["人物的停顿与误解"],
                "action": "REVIEW_FLAG",
            },
            "revision_authorization": {
                "status": "NOT_AUTHORIZED",
                "target_finding_id": "LOCAL_ACTION_TAIL",
                "allowed_ranges": [],
            },
            "detector_independent_reason": "即使不看任何检测报告，也会依据段落功能做这个判断。",
            "unresolved": [],
        }
        record_path = make_file(".json")
        record_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8", newline="")
        validator_prefix = [sys.executable, "-B", str(validator_script)]
        validator_suffix = ["--source", str(source), "--compact"]
        validator_command = validator_prefix + [str(record_path)] + validator_suffix
        valid = run_json(validator_command)
        if valid["result"] != "PASS":
            raise SystemExit(f"valid AI_TRACE record rejected: {valid}")
        valid_dumped = json.dumps(valid, ensure_ascii=False)
        assert_absent(valid_dumped, str(source.resolve()).replace("\\", "\\\\"))

        tampered = json.loads(json.dumps(record, ensure_ascii=False))
        tampered["source"]["sha256"] = "0" * 64
        tampered_path = make_file(".json")
        tampered_path.write_text(json.dumps(tampered, ensure_ascii=False), encoding="utf-8", newline="")
        tampered_result = run_json(
            validator_prefix + [str(tampered_path)] + validator_suffix, 1
        )
        if tampered_result["result"] != "FAIL" or not any(
            item["code"] == "source_sha256_mismatch" for item in tampered_result["errors"]
        ):
            raise SystemExit("SHA mismatch was not rejected")

        detector_goal = json.loads(json.dumps(record, ensure_ascii=False))
        detector_goal["detector_independent_reason"] = "目标是把AIGC检测率降到5%并绕过检测器。"
        detector_path = make_file(".json")
        detector_path.write_text(json.dumps(detector_goal, ensure_ascii=False), encoding="utf-8", newline="")
        detector_result = run_json(
            validator_prefix + [str(detector_path)] + validator_suffix, 1
        )
        if detector_result["result"] != "FAIL" or not any(
            item["code"] == "forbidden_detector_goal_or_evasion" for item in detector_result["errors"]
        ):
            raise SystemExit("detector score/evasion goal was not rejected")

        no_protection = json.loads(json.dumps(record, ensure_ascii=False))
        no_protection["primary_finding"]["voice_protection"] = []
        no_protection_path = make_file(".json")
        no_protection_path.write_text(json.dumps(no_protection, ensure_ascii=False), encoding="utf-8", newline="")
        no_protection_result = run_json(
            validator_prefix + [str(no_protection_path)] + validator_suffix, 1
        )
        if no_protection_result["result"] != "FAIL" or not any(
            item["code"] == "voice_protection_items_required"
            for item in no_protection_result["errors"]
        ):
            raise SystemExit("missing voice protection was not rejected")

        wrong_order = json.loads(json.dumps(record, ensure_ascii=False))
        wrong_order["cold_read_locked_before_detector"] = False
        wrong_order_path = make_file(".json")
        wrong_order_path.write_text(json.dumps(wrong_order, ensure_ascii=False), encoding="utf-8", newline="")
        wrong_order_result = run_json(
            validator_prefix + [str(wrong_order_path)] + validator_suffix, 1
        )
        if wrong_order_result["result"] != "FAIL" or not any(
            item["code"] == "cold_read_order_not_locked"
            for item in wrong_order_result["errors"]
        ):
            raise SystemExit("detector-before-cold-read order was not rejected")

        wrong_target = json.loads(json.dumps(record, ensure_ascii=False))
        wrong_target["revision_authorization"]["target_finding_id"] = "OTHER_FINDING"
        wrong_target_path = make_file(".json")
        wrong_target_path.write_text(json.dumps(wrong_target, ensure_ascii=False), encoding="utf-8", newline="")
        wrong_target_result = run_json(
            validator_prefix + [str(wrong_target_path)] + validator_suffix, 1
        )
        if wrong_target_result["result"] != "FAIL" or not any(
            item["code"] == "revision_target_does_not_match_primary_finding"
            for item in wrong_target_result["errors"]
        ):
            raise SystemExit("revision target mismatch was not rejected")

        safe_policy = json.loads(json.dumps(record, ensure_ascii=False))
        safe_policy["detector_independent_reason"] = "不以检测器分数为目标，只记录可复核的文学问题。"
        safe_policy_path = make_file(".json")
        safe_policy_path.write_text(json.dumps(safe_policy, ensure_ascii=False), encoding="utf-8", newline="")
        safe_policy_result = run_json(
            validator_prefix + [str(safe_policy_path)] + validator_suffix
        )
        if safe_policy_result["result"] != "PASS":
            raise SystemExit(f"explicit anti-goal policy was rejected: {safe_policy_result}")

        forged_high_evidence = json.loads(json.dumps(record, ensure_ascii=False))
        forged_high_evidence["detector_evidence_status"] = "MAPPED_REPEATABILITY_BOUNDED"
        forged_high_path = make_file(".json")
        forged_high_path.write_text(
            json.dumps(forged_high_evidence, ensure_ascii=False),
            encoding="utf-8",
            newline="",
        )
        forged_high_result = run_json(
            validator_prefix + [str(forged_high_path)] + validator_suffix, 1
        )
        if forged_high_result["result"] != "FAIL" or not any(
            item["code"] == "repeatability_requires_two_distinct_bound_reports"
            for item in forged_high_result["errors"]
        ):
            raise SystemExit("unbound high detector-evidence status was not rejected")

        report_one = make_file(".bin")
        report_one.write_bytes(b"detector-run-one")
        report_two = make_file(".bin")
        report_two.write_bytes(b"detector-run-two")
        segment_map = make_file(".json")
        segment_payload = {
            "schema": "NATURAL_PROSE_DETECTOR_SEGMENT_MAP_V1",
            "source_sha256": expected_sha,
            "segments": [
                {
                    "source_range": {
                        "unit": "UTF8_BYTE",
                        "start": 0,
                        "end": 60,
                    },
                    "report_locator": "segment:1",
                }
            ],
        }
        segment_map.write_text(
            json.dumps(segment_payload, ensure_ascii=False), encoding="utf-8", newline=""
        )
        bound_repeatability = json.loads(json.dumps(record, ensure_ascii=False))
        bound_repeatability["detector_evidence_status"] = "MAPPED_REPEATABILITY_BOUNDED"
        bound_repeatability["detector_evidence"] = {
            "runs": [
                {
                    "source_sha256": expected_sha,
                    "report": {
                        "path": str(report_one.resolve()),
                        "sha256": hashlib.sha256(report_one.read_bytes()).hexdigest(),
                    },
                },
                {
                    "source_sha256": expected_sha,
                    "report": {
                        "path": str(report_two.resolve()),
                        "sha256": hashlib.sha256(report_two.read_bytes()).hexdigest(),
                    },
                },
            ],
            "segment_map": {
                "path": str(segment_map.resolve()),
                "sha256": hashlib.sha256(segment_map.read_bytes()).hexdigest(),
            },
        }
        bound_repeatability_path = make_file(".json")
        bound_repeatability_path.write_text(
            json.dumps(bound_repeatability, ensure_ascii=False),
            encoding="utf-8",
            newline="",
        )
        bound_repeatability_result = run_json(
            validator_prefix + [str(bound_repeatability_path)] + validator_suffix
        )
        if bound_repeatability_result["result"] != "PASS":
            raise SystemExit(
                f"bound repeatability evidence rejected: {bound_repeatability_result}"
            )

        out_of_bounds = json.loads(json.dumps(record, ensure_ascii=False))
        out_of_bounds["revision_authorization"] = {
            "status": "AUTHORIZED",
            "target_finding_id": "LOCAL_ACTION_TAIL",
            "allowed_ranges": [
                {"unit": "UTF8_BYTE", "start": 0, "end": len(source.read_bytes()) + 1}
            ],
        }
        out_of_bounds_path = make_file(".json")
        out_of_bounds_path.write_text(
            json.dumps(out_of_bounds, ensure_ascii=False), encoding="utf-8", newline=""
        )
        out_of_bounds_result = run_json(
            validator_prefix + [str(out_of_bounds_path)] + validator_suffix, 1
        )
        if out_of_bounds_result["result"] != "FAIL" or not any(
            item["code"] == "range_exceeds_source_bytes"
            for item in out_of_bounds_result["errors"]
        ):
            raise SystemExit("out-of-source authorization was not rejected")

        outside_primary = json.loads(json.dumps(record, ensure_ascii=False))
        outside_primary["revision_authorization"] = {
            "status": "AUTHORIZED",
            "target_finding_id": "LOCAL_ACTION_TAIL",
            "allowed_ranges": [
                {"unit": "UTF8_BYTE", "start": 81, "end": 100}
            ],
        }
        outside_primary_path = make_file(".json")
        outside_primary_path.write_text(
            json.dumps(outside_primary, ensure_ascii=False), encoding="utf-8", newline=""
        )
        outside_primary_result = run_json(
            validator_prefix + [str(outside_primary_path)] + validator_suffix, 1
        )
        if outside_primary_result["result"] != "FAIL" or not any(
            item["code"] == "allowed_range_outside_primary_finding"
            for item in outside_primary_result["errors"]
        ):
            raise SystemExit("authorization outside the primary finding was not rejected")

    contract_files = {
        "SKILL.md": (
            "SINGLE_AGENT_TWO_DRAFT",
            "two-draft-workflow.md",
            "voice-style-contract.md",
        ),
        "references/ai-trace-audit.md": (
            "NATURAL_PROSE_AI_TRACE_RECORD_V1",
            "cold_read_locked_before_detector",
            "detector_independent_reason",
            "ORDERING_ONLY",
            "RED_HIGHLIGHT_REVIEW",
            "UTF8_BYTE",
        ),
        "references/two-draft-workflow.md": (
            "DRAFT_1_AUDIT",
            "KEEP_FUNCTIONS",
            "REQUIRED_REPAIRS",
            "DRAFT_2_INPUT",
            "FINAL_CHECK",
        ),
        "references/two-draft-input-template.md": (
            "NATURAL_PROSE_TWO_DRAFT_INPUT_V1",
            "SOURCE_BINDINGS",
            "RETENTION_ENGINE",
            "CONCRETE_CONTAINER",
            "TURN_PLACEMENT",
            "regression_guards",
        ),
        "references/voice-style-contract.md": (
            "VOICE_STYLE_LAYERED_V1",
            "DOMINANT_LAYER",
            "WEB_NARRATIVE_PROFILE",
            "RETENTION_ENGINE",
            "CONCRETE_CONTAINER",
            "TURN_PLACEMENT",
            "EXIT_PULL",
            "LITERARY_MODULATION",
            "translation_status",
            "PRIORITY_ORDER",
            "RETURN_INTERFACE",
        ),
    }
    absolute_path_pattern = re.compile(r"(?i)(?<![A-Za-z0-9])[A-Z]:[\\/][^\s`\"']+")
    project_object_pattern = re.compile(r"\b(?:VOL(?:UME)?|CH(?:APTER)?)[-_]?\d{1,4}\b", re.I)
    synthetic_drive_leak = "Q" + ":" + "\\" + "private-workspace" + "\\" + "file.md"
    synthetic_object_leak = "VO" + "L" + "9" + "-" + "CH" + "88"
    runtime_project_markers = (
        "call" + "-" + "writing" + "-" + "model",
        "Build" + "-" + "Corpus" + "Manifest",
        "Manage" + "-" + "Review" + "Dispatch",
        "FINAL" + "_" + "CANON" + "_" + "CONTEXT",
    )
    if not absolute_path_pattern.search(synthetic_drive_leak):
        raise SystemExit("absolute path contamination pattern is ineffective")
    if not project_object_pattern.search(synthetic_object_leak):
        raise SystemExit("project object contamination pattern is ineffective")

    for relative, required in contract_files.items():
        file_path = scripts.parent / relative
        if not file_path.is_file():
            raise SystemExit(f"missing contract file: {relative}")
        content = file_path.read_text(encoding="utf-8")
        missing_contracts = [needle for needle in required if needle not in content]
        if missing_contracts:
            raise SystemExit(
                f"missing contract fields in {relative}: {missing_contracts}"
            )
        if absolute_path_pattern.search(content):
            raise SystemExit(f"absolute project path leaked into generic file: {relative}")
        if project_object_pattern.search(content):
            raise SystemExit(f"project object identity leaked into generic file: {relative}")

    public_suffixes = {".md", ".py", ".yaml", ".yml", ".txt"}
    for file_path in scripts.parent.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in public_suffixes:
            continue
        content = file_path.read_text(encoding="utf-8")
        relative = file_path.relative_to(scripts.parent)
        if absolute_path_pattern.search(content):
            raise SystemExit(f"absolute project path leaked into generic package: {relative}")
        if project_object_pattern.search(content):
            raise SystemExit(f"project object identity leaked into generic package: {relative}")
        leaked_runtime_markers = [
            marker for marker in runtime_project_markers if marker in content
        ]
        if leaked_runtime_markers:
            raise SystemExit(
                f"project workflow marker leaked into generic package: {relative}"
            )

    print("SELF_TEST=PASS")
    print("GENERIC_CONTRACT=PASS")
    print("AI_TRACE_RECORD_VALIDATION=PASS")
    print("PRIVACY_BOUNDARY=PASS")
    print("PROTECTIVE_NEGATIVES=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
