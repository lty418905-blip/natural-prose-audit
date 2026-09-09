#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def test_unicode_layer_a(base: Path, env: dict[str, str]) -> None:
    layer_script = base / "unicode_layer_a.py"
    fixture_text = "\ufeff甲\u200b乙\u2060丙\u00ad丁\u202e戊\ufeff己\u200c庚\u200d辛\ufe0f"
    temp_root = base / f".layer-a-self-test-{os.getpid()}"
    if temp_root.exists():
        raise SystemExit(f"Layer A self-test path already exists: {temp_root}")
    temp_root.mkdir()
    source = temp_root / "source.txt"
    output = temp_root / "source.layer-a-clean.txt"
    try:
        source.write_text(fixture_text, encoding="utf-8")
        source_before = source.read_bytes()

        inspect_run = subprocess.run(
            [sys.executable, str(layer_script), "inspect", str(source), "--compact"],
            check=True, capture_output=True, text=True, encoding="utf-8", env=env,
        )
        inspected = json.loads(inspect_run.stdout)
        if inspected["scan"]["high_confidence_total"] != 5:
            raise SystemExit("Layer A inspect missed removable controls")
        if inspected["scan"]["preserved_semantic_total"] != 3:
            raise SystemExit("Layer A inspect missed preserved semantic controls")
        if inspected["scan"]["initial_bom_preserved"] != 1:
            raise SystemExit("Layer A inspect did not preserve initial BOM")

        clean_run = subprocess.run(
            [sys.executable, str(layer_script), "clean", str(source), "--compact"],
            check=True, capture_output=True, text=True, encoding="utf-8", env=env,
        )
        cleaned = json.loads(clean_run.stdout)
        if source.read_bytes() != source_before or cleaned["source_modified"]:
            raise SystemExit("Layer A clean modified the source")
        if Path(cleaned["output"]) != output.resolve():
            raise SystemExit("Layer A clean did not use the non-in-place default output")
        if cleaned["removed_total"] != 5:
            raise SystemExit("Layer A clean removed unexpected count")
        if cleaned["post_clean_scan"]["high_confidence_total"] != 0:
            raise SystemExit("Layer A post-clean scan is not zero")
        output_text = output.read_text(encoding="utf-8")
        for preserved in ("\u200c", "\u200d", "\ufe0f"):
            if preserved not in output_text:
                raise SystemExit("Layer A clean removed a semantic control")
        if not output_text.startswith("\ufeff"):
            raise SystemExit("Layer A clean removed the initial BOM")

        in_place_run = subprocess.run(
            [
                sys.executable, str(layer_script), "clean", str(source),
                "--output", str(source), "--compact",
            ],
            check=False, capture_output=True, text=True, encoding="utf-8", env=env,
        )
        if in_place_run.returncode == 0 or "refusing in-place clean" not in in_place_run.stderr:
            raise SystemExit("Layer A did not refuse in-place output")
    finally:
        source.unlink(missing_ok=True)
        output.unlink(missing_ok=True)
        temp_root.rmdir()


def test_house_style_is_optional(base: Path, env: dict[str, str]) -> None:
    """Contextual punctuation rules must not be hard failures by default."""
    script = base / "check_human_writing.py"
    temp_root = base / f".house-style-self-test-{os.getpid()}"
    if temp_root.exists():
        raise SystemExit(f"house-style self-test path already exists: {temp_root}")
    temp_root.mkdir()
    source = temp_root / "source.txt"
    try:
        source.write_text(
            "甲" * 20 + "。不是甲而是乙：这是人物说话——不是规则。\n",
            encoding="utf-8",
        )
        default_run = subprocess.run(
            [sys.executable, str(script), str(source)],
            check=False, capture_output=True, text=True, encoding="utf-8", env=env,
        )
        if default_run.returncode != 0:
            raise SystemExit("contextual house-style rules became default failures")

        strict_run = subprocess.run(
            [sys.executable, str(script), str(source), "--strict-house-style"],
            check=False, capture_output=True, text=True, encoding="utf-8", env=env,
        )
        if strict_run.returncode != 1:
            raise SystemExit("strict house-style mode did not fail on the fixture")
    finally:
        source.unlink(missing_ok=True)
        temp_root.rmdir()


def test_redundant_modifier_stack(base: Path, env: dict[str, str]) -> None:
    """Only high-confidence stacked modifiers should become mechanical findings."""
    script = base / "audit_prose.py"
    temp_root = base / f".modifier-self-test-{os.getpid()}"
    if temp_root.exists():
        raise SystemExit(f"modifier self-test path already exists: {temp_root}")
    temp_root.mkdir()
    source = temp_root / "source.txt"
    try:
        source.write_text(
            "她轻轻地缓缓地抬起手。随后她压低声音，免得门外的人听见。\n",
            encoding="utf-8",
        )
        run = subprocess.run(
            [sys.executable, str(script), str(source), "--mode", "fiction", "--compact"],
            check=True, capture_output=True, text=True, encoding="utf-8", env=env,
        )
        payload = json.loads(run.stdout)
        matches = [
            item for item in payload.get("findings", [])
            if item.get("type") == "redundant_modifier_stack_candidate"
        ]
        if len(matches) != 1 or matches[0].get("excerpt") != "轻轻地缓缓地":
            raise SystemExit("redundant modifier stack was not detected exactly once")
        if any(item.get("excerpt") == "压低声音" for item in payload.get("findings", [])):
            raise SystemExit("functional manner information was incorrectly flagged")
    finally:
        source.unlink(missing_ok=True)
        temp_root.rmdir()


def test_dual_subagent_review_templates(base: Path) -> None:
    assets = base.parent / "assets"
    reference = base.parent / "references" / "project-dual-subagent-review-gate.md"
    coverage = json.loads(
        (assets / "outline-expression-coverage-audit-v2.template.json").read_text(
            encoding="utf-8"
        )
    )
    closure = json.loads(
        (assets / "narrative-closure-audit-v1.template.json").read_text(
            encoding="utf-8"
        )
    )
    binding = json.loads(
        (assets / "dual-subagent-pre-review-binding-v1.template.json").read_text(
            encoding="utf-8"
        )
    )

    if coverage.get("schema") != "outline_expression_coverage_audit_v2":
        raise SystemExit("coverage report template schema changed unexpectedly")
    if closure.get("schema_version") != "NARRATIVE_LOGIC_CLOSURE_AUDIT_V1":
        raise SystemExit("narrative-closure report template schema changed unexpectedly")
    if binding.get("schema") != "dual_subagent_pre_review_binding_v1":
        raise SystemExit("dual-subagent binding template schema changed unexpectedly")

    for identity_key in ("object_id", "outline", "prose"):
        if coverage.get(identity_key) != closure.get(identity_key):
            raise SystemExit(f"dual reports do not share source identity: {identity_key}")
    if coverage.get("task_id") == closure.get("auditor", {}).get("task_id"):
        raise SystemExit("dual report task identities are not distinct")
    if coverage.get("context_id") == closure.get("auditor", {}).get("context_id"):
        raise SystemExit("dual report context identities are not distinct")
    for report in (coverage, closure):
        independence = report.get("independence", {})
        if report is closure:
            if closure.get("auditor", {}).get("kind") != "INDEPENDENT_SUBAGENT":
                raise SystemExit("closure report lost independent auditor identity")
            if closure.get("auditor", {}).get("one_time") is not True:
                raise SystemExit("closure report lost one-time identity")
            continue
        if independence.get("execution_mode") != "PARALLEL_INDEPENDENT":
            raise SystemExit("dual report template lost parallel-independent execution")
        if independence.get("peer_report_read") is not False:
            raise SystemExit("dual report template permits reading the peer report")
        if report.get("one_time") is not True:
            raise SystemExit("dual report template lost one-time identity")

    expected_dimensions = [
        "ACTION_REASON_OVEREXPLANATION",
        "OBSERVATION_INFERENCE_CONCLUSION",
        "DIALOGUE_QUESTION_ANSWER_CLOSURE",
        "SELF_CORRECTION_TO_RIGHT_ANSWER",
        "UNKNOWN_ENUMERATION_AND_FUTURE_PLAN",
        "SETUP_PAYOFF_SUMMARY_UNIFORMITY",
        "EXTERNAL_INTERRUPTION_AND_RESIDUE",
    ]
    if closure.get("dimensions_checked") != expected_dimensions:
        raise SystemExit("narrative-closure template does not preserve all seven dimensions")
    if binding.get("outline_expression_coverage_report", {}).get("task_id") != coverage.get("task_id"):
        raise SystemExit("dual binding does not carry the coverage task identity")
    if binding.get("narrative_closure_report", {}).get("task_id") != closure.get("auditor", {}).get("task_id"):
        raise SystemExit("dual binding does not carry the closure task identity")
    if binding.get("source_changed_after_reports") is not False:
        raise SystemExit("dual binding template does not fail closed on source drift")

    reference_text = reference.read_text(encoding="utf-8")
    for required_token in (
        "PARALLEL_INDEPENDENT",
        "peer_report_read=false",
        "DUAL_SUBAGENT_REPORT_GATE_INCOMPLETE",
        "scene_evidence",
        "next_action_dependency",
    ):
        if required_token not in reference_text:
            raise SystemExit(f"dual-subagent reference is missing: {required_token}")


def test_generic_production_tools(base: Path, env: dict[str, str]) -> None:
    import hashlib
    import post_assembly_text_hygiene as hygiene
    import shadow_detector_scorer as shadow

    clean = "阿青关好窗，拿着湿外套去了厨房。"
    findings, _ = hygiene.scan(clean, [])
    assert not findings
    findings, _ = hygiene.scan(clean + "TODO", [])
    assert any(f["kind"] == "INTERNAL_PROCESS_MARKER_LEAK" for f in findings)
    paragraph = "她把外套挂在门后，水沿着衣角落到地上，门外的脚步声渐渐远了。"
    findings, _ = hygiene.scan(paragraph + "\n\n" + clean + "\n\n" + paragraph, [])
    assert any(f["severity"] == "HARD_BLOCK" for f in findings)

    with tempfile.TemporaryDirectory(prefix="npa-test-") as directory:
        root = Path(directory)
        prose = root / "prose.txt"
        prose.write_text(clean, encoding="utf-8")
        binding = {"path": str(prose), "sha256": hashlib.sha256(prose.read_bytes()).hexdigest()}
        record = {
            "schema": "POST_EXPANSION_LITERARY_ACCEPTANCE_V1", "object_id": "example",
            "pre_expansion_prose": binding, "post_expansion_prose": binding,
            "outline": binding, "reviewer_identity": "test-only",
            "fragments": [{**binding, "function_lost_if_removed": "The visible exit would be lost.",
                           "checks": {key: "PASS" for key in (
                               "FUNCTION_LOST_IF_REMOVED", "NOVEL_INFORMATION_OR_STATE_CHANGE",
                               "OBJECT_AND_SENSORY_RECURRENCE", "VOICE_AND_SEAM_FIT",
                               "OUTLINE_AND_FACT_BOUNDARY", "PLAN_CLOSURE")}}],
            "whole_chapter_counterfactual": {"result": "PASS", "evidence": "test fixture"},
            "result": "PASS",
        }
        path = root / "review.json"

        def run_review(expected: int) -> None:
            path.write_text(json.dumps(record), encoding="utf-8")
            run = subprocess.run([sys.executable, str(base / "validate_post_expansion_literary_acceptance.py"), str(path)],
                                 capture_output=True, text=True, encoding="utf-8", env=env)
            assert run.returncode == expected, run.stdout + run.stderr

        run_review(0)
        record["fragments"][0]["checks"].pop("PLAN_CLOSURE")
        run_review(2)
        record["fragments"][0]["checks"]["PLAN_CLOSURE"] = "PASS"
        prose.write_text(clean + "天黑了。", encoding="utf-8")
        run_review(2)

        # Calibration uses arbitrary files and real group boundaries, not fixed pack headings.
        mapping, reports = {}, []
        for index in range(12):
            source = root / f"probe-{index}.txt"
            text = "甲走过走廊。" * (index + 1) + "\r\n她把门关上。"
            source.write_bytes(text.encode("utf-8"))
            mapping[f"sample-{index}"] = {
                "path": source.name, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "group": f"source-{index // 4}",
            }
            reports.append({"probe_id": f"sample-{index}", "reported_chars": len(text),
                            "segments": [{"chars": len(text), "score": 0.4}],
                            "input_identity": "MATCH", "comparability": "SAME_SOURCE"})
        map_path = root / "map.json"
        report_path = root / "reports.json"
        output = root / "shadow.json"
        map_path.write_text(json.dumps(mapping), encoding="utf-8")
        report_path.write_text(json.dumps({"reports": reports}), encoding="utf-8")
        texts = shadow.mapped_texts(map_path)
        assert "\r\n" in texts["sample-0"]["text"]
        records, issues = shadow.build_records({"reports": reports}, texts)
        assert not issues and records[0]["group"] == "source-0"
        reports[0]["input_identity"] = "UNKNOWN"
        excluded, _ = shadow.build_records({"reports": reports}, texts)
        assert excluded[0]["excluded_from_fit"]
        run = subprocess.run([sys.executable, str(base / "shadow_detector_scorer.py"),
                              "--text-map", str(map_path), "--reports", str(report_path),
                              "--out", str(output), "--score-text", str(prose)],
                             capture_output=True, text=True, encoding="utf-8", env=env)
        assert run.returncode == 0, run.stdout + run.stderr
        result = json.loads(output.read_text(encoding="utf-8"))
        assert result["eligible_count"] == 12
        assert result["group_blocked_cv_metrics"]["count"] == 12
        assert result["result"] == "SHADOW_SURROGATE_INSUFFICIENT"
        assert result["arbitrary_text_score"]["score_kind"] == "SHADOW_PREDICTED_SCORE"
        mapping["sample-0"]["sha256"] = "0" * 64
        map_path.write_text(json.dumps(mapping), encoding="utf-8")
        try:
            shadow.mapped_texts(map_path)
        except ValueError:
            pass
        else:
            raise AssertionError("changed probe file was accepted")


def main() -> int:
    base = Path(__file__).resolve().parent
    script = base / "audit_prose.py"
    path = base / "self_test_fixture.txt"
    scene_path = base / "self_test_scene_fixture.txt"
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    run = subprocess.run(
        [sys.executable, str(script), str(path), "--mode", "fiction", "--structure", "--compact"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=child_env,
    )
    result = json.loads(run.stdout)
    if result.get("schema") != "natural_prose_audit_v3":
        raise SystemExit("audit schema identity changed unexpectedly")
    kinds = {item["type"] for item in result["findings"]}
    required = {
        "transition", "author_metaphor", "reversal_template", "repeated_sentence_start",
        "epistemic_limiter_cluster", "cognitive_audit_cycle_candidate",
        "dialogue_unit_test_run", "action_argument_pair_run",
        "action_immediate_interpretation_run", "exclusion_space_closure_candidate",
        "paragraph_tail_closure_run", "ending_dense_closure_candidate",
        "functional_micro_loop_candidate",
    }
    missing = sorted(required - kinds)
    if missing:
        raise SystemExit(f"missing expected findings: {missing}")
    if result["verdict"] != "warnings_only_no_detector_claim":
        raise SystemExit("verdict boundary changed")
    if any("score" in item for item in result["findings"]):
        raise SystemExit("structure proxies must not emit scores")
    if any(item.get("action") not in {
        "review_in_context", "read_aloud_then_keep_or_rephrase",
        "keep_if_scene_pressure_supports_it", "review_semantic_function", "review_flag",
    } for item in result["findings"]):
        raise SystemExit("unexpected automatic action")
    finding_ids = [item.get("finding_id") for item in result["findings"]]
    if any(not finding_id for finding_id in finding_ids) or len(finding_ids) != len(set(finding_ids)):
        raise SystemExit("project finding identities are missing or not unique")
    if any(item.get("project_disposition_class") not in {
        "LOGIC_CLOSURE_COUNTERFACTUAL", "REPAIR_REQUIRED",
    } for item in result["findings"]):
        raise SystemExit("project disposition classification is missing")

    scene_run = subprocess.run(
        [sys.executable, str(script), str(scene_path), "--mode", "fiction", "--structure", "--compact"],
        check=True, capture_output=True, text=True, encoding="utf-8", env=child_env,
    )
    scene_result = json.loads(scene_run.stdout)
    scene_kinds = {item["type"] for item in scene_result["findings"]}
    scene_required = {
        "adjacent_paragraph_overlap_candidate",
        "assembly_blank_gap_candidate",
        "late_unestablished_quote_candidate",
        "narrative_negation_proof_cluster_candidate",
        "background_foreground_beat_alignment_candidate",
        "dialogue_narration_syntax_convergence_candidate",
    }
    scene_missing = sorted(scene_required - scene_kinds)
    if scene_missing:
        raise SystemExit(f"missing scene-level regression findings: {scene_missing}")
    if any(item.get("action") != "review_flag" for item in scene_result["findings"] if item["type"] in scene_required):
        raise SystemExit("new scene-level findings must remain review-only")

    exemption_path = base / f".audit-exemptions-self-test-{os.getpid()}.json"
    try:
        exemption_path.write_text(json.dumps({
            "schema": "natural_prose_audit_exemptions_v1",
            "source": str(scene_path.resolve()),
            "exemptions": [{
                "line_start": 1,
                "line_end": 200,
                "finding_types": ["narrative_negation_proof_cluster_candidate"],
                "reason": "object_layer_test",
            }],
        }, ensure_ascii=False), encoding="utf-8")
        exempt_run = subprocess.run(
            [
                sys.executable, str(script), str(scene_path), "--mode", "fiction", "--structure",
                "--exemptions", str(exemption_path), "--compact",
            ],
            check=True, capture_output=True, text=True, encoding="utf-8", env=child_env,
        )
        exempted = json.loads(exempt_run.stdout)
        exempted_kinds = {item["type"] for item in exempted["findings"]}
        if "narrative_negation_proof_cluster_candidate" in exempted_kinds:
            raise SystemExit("line-bound object-layer exemption was not applied")
        if exempted.get("suppressed_finding_count", 0) < 1:
            raise SystemExit("exemption suppression was not recorded")
    finally:
        exemption_path.unlink(missing_ok=True)

    compare_run = subprocess.run(
        [
            sys.executable, str(script), str(path), "--mode", "fiction", "--structure",
            "--baseline", str(path),
            "--target-finding-type", "functional_micro_loop_candidate", "--compact",
        ],
        check=True, capture_output=True, text=True, encoding="utf-8", env=child_env,
    )
    compared = json.loads(compare_run.stdout)
    comparison = compared.get("comparison", {})
    if comparison.get("primary_finding_resolution") != "PRIMARY_FINDING_UNRESOLVED":
        raise SystemExit("baseline comparison failed to preserve unresolved target finding")
    if comparison.get("target_finding_count_before") != comparison.get("target_finding_count_after"):
        raise SystemExit("baseline comparison target counts changed unexpectedly")

    disposition_validator = base / "validate_project_finding_dispositions.py"
    disposition_root = base / f".finding-disposition-self-test-{os.getpid()}"
    if disposition_root.exists():
        raise SystemExit(f"finding disposition self-test path already exists: {disposition_root}")
    disposition_root.mkdir()
    initial_path = disposition_root / "initial.json"
    final_path = disposition_root / "final.json"
    initial_house_path = disposition_root / "initial-house.json"
    final_house_path = disposition_root / "final-house.json"
    disposition_path = disposition_root / "dispositions.json"
    report_paths = [disposition_root / f"exception-report-{index}.md" for index in range(1, 5)]
    science_report_path = disposition_root / "science-advisor-report.md"
    ruling_path = disposition_root / "controller-ruling.md"
    try:
        initial_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        closure = next(
            item for item in result["findings"]
            if item["project_disposition_class"] == "LOGIC_CLOSURE_COUNTERFACTUAL"
        )
        final_payload = json.loads(json.dumps(result, ensure_ascii=False))
        final_payload["findings"] = [closure]
        final_payload["finding_count"] = 1
        final_path.write_text(json.dumps(final_payload, ensure_ascii=False), encoding="utf-8")

        house_finding_id = "NPH-SELFTEST-HOUSE-0001"
        initial_house_payload = {
            "schema": "natural_prose_house_style_audit_v1",
            "strict_house_style": True,
            "findings": [{
                "finding_id": house_finding_id,
                "type": "synthetic_house_style_shape",
                "message": "synthetic house-style finding",
                "project_allowed_dispositions": ["FIXED", "CONTROLLER_EXCEPTION_APPROVED"],
            }],
        }
        final_house_payload = {
            "schema": "natural_prose_house_style_audit_v1",
            "strict_house_style": True,
            "findings": [],
        }
        initial_house_path.write_text(
            json.dumps(initial_house_payload, ensure_ascii=False), encoding="utf-8"
        )
        final_house_path.write_text(
            json.dumps(final_house_payload, ensure_ascii=False), encoding="utf-8"
        )

        import hashlib
        report_roles = [
            "NOVELIZATION_MAIN",
            "NOVELIZATION_SUBAGENT_1",
            "NOVELIZATION_SUBAGENT_2",
            "NOVELIZATION_SUBAGENT_3",
        ]
        report_bindings = []
        for index, (report_path, report_role) in enumerate(zip(report_paths, report_roles), start=1):
            report_path.write_text(
                "\n".join([
                    f"FINDING_ID={closure['finding_id']}",
                    f"REPORT_ROLE={report_role}",
                    "NARRATIVE_LOGIC_ASSESSMENT=synthetic causal handoff assessment",
                    "LITERARY_IRREPLACEABILITY_ASSESSMENT=synthetic voice assessment",
                    "COUNTERFACTUAL_WITHOUT_HIT=synthetic counterfactual",
                ]),
                encoding="utf-8",
            )
            report_bindings.append({
                "report_role": report_role,
                "task_id": f"self-test-task-{index}",
                "independent": True,
                "finding_id": closure["finding_id"],
                "conclusion": "IRREPLACEABLE",
                "narrative_logic_assessment": "synthetic causal handoff assessment",
                "literary_irreplaceability_assessment": "synthetic voice assessment",
                "counterfactual_without_hit": "synthetic counterfactual",
                "path": str(report_path.resolve()),
                "sha256": hashlib.sha256(report_path.read_bytes()).hexdigest().upper(),
            })
        report_hashes = [binding["sha256"] for binding in report_bindings]
        science_report_path.write_text(
            "\n".join([
                f"FINDING_ID={closure['finding_id']}",
                "REPORT_ROLE=SCIENCE_ADVISOR",
                "DECISION=SCIENCE_RIGOR_OVERRIDE_SUPPORTED",
                "SCIENTIFIC_RIGOR_ASSESSMENT=synthetic scientific-rigor assessment",
                "MECHANICAL_REMOVAL_HARM=synthetic loss of evidentiary precision",
            ]),
            encoding="utf-8",
        )
        science_report_sha = hashlib.sha256(science_report_path.read_bytes()).hexdigest().upper()
        ruling_path.write_text(
            "\n".join([
                f"FINDING_ID={closure['finding_id']}",
                "SIGNED_BY=CONTROLLER",
                "DECISION=APPROVE_EXCEPTION",
                *[f"REPORT_SHA256={report_sha}" for report_sha in report_hashes],
                f"SCIENCE_REPORT_SHA256={science_report_sha}",
            ]),
            encoding="utf-8",
        )

        dispositions = []
        for finding in result["findings"]:
            if finding["finding_id"] == closure["finding_id"]:
                dispositions.append({
                    "finding_id": finding["finding_id"],
                    "disposition": "CONTROLLER_EXCEPTION_APPROVED",
                    "science_involved": True,
                    "exception_reports": report_bindings,
                    "science_advisor_report": {
                        "report_role": "SCIENCE_ADVISOR",
                        "receiver_task_id": "self-test-science-advisor",
                        "finding_id": finding["finding_id"],
                        "decision": "SCIENCE_RIGOR_OVERRIDE_SUPPORTED",
                        "scientific_rigor_assessment": "synthetic scientific-rigor assessment",
                        "mechanical_removal_harm": "synthetic loss of evidentiary precision",
                        "path": str(science_report_path.resolve()),
                        "sha256": science_report_sha,
                    },
                    "controller_ruling": {
                        "path": str(ruling_path.resolve()),
                        "sha256": hashlib.sha256(ruling_path.read_bytes()).hexdigest().upper(),
                        "signed_by": "CONTROLLER",
                        "decision": "APPROVE_EXCEPTION",
                        "finding_id": finding["finding_id"],
                        "binding_report_sha256": report_hashes,
                        "binding_science_report_sha256": science_report_sha,
                    },
                })
            else:
                dispositions.append({
                    "finding_id": finding["finding_id"],
                    "disposition": "FIXED",
                    "repair_summary": "synthetic self-test removal",
                    "final_verification": "ABSENT_IN_FINAL_AUDIT",
                })
        dispositions.append({
            "finding_id": house_finding_id,
            "disposition": "FIXED",
            "repair_summary": "synthetic house-style finding removed",
            "final_verification": "ABSENT_IN_FINAL_AUDIT",
        })
        disposition_payload = {
            "schema": "natural_prose_project_finding_dispositions_v2",
            "initial_audit_sha256": hashlib.sha256(initial_path.read_bytes()).hexdigest().upper(),
            "final_audit_sha256": hashlib.sha256(final_path.read_bytes()).hexdigest().upper(),
            "initial_house_style_audit": {
                "path": str(initial_house_path.resolve()),
                "sha256": hashlib.sha256(initial_house_path.read_bytes()).hexdigest().upper(),
            },
            "final_house_style_audit": {
                "path": str(final_house_path.resolve()),
                "sha256": hashlib.sha256(final_house_path.read_bytes()).hexdigest().upper(),
            },
            "items": dispositions,
        }
        disposition_path.write_text(json.dumps(disposition_payload, ensure_ascii=False), encoding="utf-8")
        disposition_run = subprocess.run(
            [
                sys.executable, str(disposition_validator), str(initial_path), str(final_path),
                str(disposition_path), "--compact",
            ],
            check=False, capture_output=True, text=True, encoding="utf-8", env=child_env,
        )
        if disposition_run.returncode != 0:
            raise SystemExit(f"project disposition validation failed: {disposition_run.stdout}")
        disposition_result = json.loads(disposition_run.stdout)
        if disposition_result.get("result") != "PASS":
            raise SystemExit("project disposition validator did not pass the four-report exception fixture")
    finally:
        for temp_path in (
            disposition_path,
            ruling_path,
            science_report_path,
            *report_paths,
            final_house_path,
            initial_house_path,
            final_path,
            initial_path,
        ):
            temp_path.unlink(missing_ok=True)
        disposition_root.rmdir()
    test_unicode_layer_a(base, child_env)
    test_house_style_is_optional(base, child_env)
    test_redundant_modifier_stack(base, child_env)
    test_dual_subagent_review_templates(base)
    test_generic_production_tools(base, child_env)
    print("SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
