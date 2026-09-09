#!/usr/bin/env python3
"""Validate project finding disposition closure for natural-prose audits.

This validator never edits prose. It proves that every initial finding was
handled. Any finding that survives the final audit requires four independent
reports (novelization main plus three subagents) and a controller-signed ruling
bound to all four report hashes. If the disputed finding involves science, a
science-advisor rigor-exemption report is additionally required. Direct
science exemption belongs only to outline risks without a mechanical finding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "natural_prose_project_finding_dispositions_v2"
SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
EXPECTED_EXCEPTION_REPORT_ROLES = {
    "NOVELIZATION_MAIN",
    "NOVELIZATION_SUBAGENT_1",
    "NOVELIZATION_SUBAGENT_2",
    "NOVELIZATION_SUBAGENT_3",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_bound_file(
    binding: object,
    label: str,
    finding_id: str,
    errors: list[dict],
) -> tuple[Path | None, str | None]:
    if not isinstance(binding, dict):
        errors.append({"code": f"{label}_object_required", "finding_id": finding_id})
        return None, None
    raw_path = binding.get("path")
    declared_sha = str(binding.get("sha256", "")).upper()
    if not nonempty(raw_path):
        errors.append({"code": f"{label}_path_required", "finding_id": finding_id})
        return None, declared_sha or None
    if not SHA256_RE.fullmatch(declared_sha):
        errors.append({"code": f"{label}_sha256_invalid", "finding_id": finding_id})
        return Path(raw_path), declared_sha or None
    path = Path(raw_path)
    if not path.is_file():
        errors.append({"code": f"{label}_file_not_found", "finding_id": finding_id})
        return path, declared_sha
    if sha256_file(path) != declared_sha:
        errors.append({"code": f"{label}_sha256_mismatch", "finding_id": finding_id})
    return path, declared_sha


def validate_controller_exception(item: dict, finding_id: str, errors: list[dict]) -> None:
    reports = item.get("exception_reports")
    if not isinstance(reports, list) or len(reports) != 4:
        errors.append({"code": "exception_exactly_four_reports_required", "finding_id": finding_id})
        reports = reports if isinstance(reports, list) else []

    roles: set[str] = set()
    task_ids: set[str] = set()
    report_paths: set[str] = set()
    report_hashes: list[str] = []
    for index, report in enumerate(reports):
        label = f"exception_report_{index + 1}"
        if not isinstance(report, dict):
            errors.append({"code": f"{label}_object_required", "finding_id": finding_id})
            continue
        role = report.get("report_role")
        if role not in EXPECTED_EXCEPTION_REPORT_ROLES:
            errors.append({"code": f"{label}_role_invalid", "finding_id": finding_id})
        elif role in roles:
            errors.append({"code": "exception_report_role_duplicate", "finding_id": finding_id})
        else:
            roles.add(role)
        task_id = report.get("task_id")
        if not nonempty(task_id):
            errors.append({"code": f"{label}_task_id_required", "finding_id": finding_id})
        elif task_id in task_ids:
            errors.append({"code": "exception_report_task_id_duplicate", "finding_id": finding_id})
        else:
            task_ids.add(task_id)
        if report.get("independent") is not True:
            errors.append({"code": f"{label}_independent_true_required", "finding_id": finding_id})
        if report.get("finding_id") != finding_id:
            errors.append({"code": f"{label}_finding_id_mismatch", "finding_id": finding_id})
        if report.get("conclusion") not in {"IRREPLACEABLE", "REPLACEABLE", "MIXED"}:
            errors.append({"code": f"{label}_conclusion_invalid", "finding_id": finding_id})
        for field in (
            "narrative_logic_assessment",
            "literary_irreplaceability_assessment",
            "counterfactual_without_hit",
        ):
            if not nonempty(report.get(field)):
                errors.append({"code": f"{label}_{field}_required", "finding_id": finding_id})
        report_path, report_sha = validate_bound_file(report, label, finding_id, errors)
        if report_path is not None:
            resolved = str(report_path.resolve())
            if resolved in report_paths:
                errors.append({"code": "exception_report_path_duplicate", "finding_id": finding_id})
            report_paths.add(resolved)
            if report_path.is_file():
                report_text = report_path.read_text(encoding="utf-8")
                if finding_id not in report_text:
                    errors.append({"code": f"{label}_file_missing_finding_id", "finding_id": finding_id})
        if report_sha:
            report_hashes.append(report_sha)

    if roles != EXPECTED_EXCEPTION_REPORT_ROLES:
        errors.append({
            "code": "exception_report_role_set_mismatch",
            "finding_id": finding_id,
            "actual_roles": sorted(roles),
        })
    if len(set(report_hashes)) != 4:
        errors.append({"code": "exception_report_sha256_not_four_unique", "finding_id": finding_id})

    science_involved = item.get("science_involved")
    science_report_sha: str | None = None
    if not isinstance(science_involved, bool):
        errors.append({"code": "exception_science_involved_boolean_required", "finding_id": finding_id})
    elif science_involved:
        science_report = item.get("science_advisor_report")
        science_path, science_report_sha = validate_bound_file(
            science_report, "science_advisor_report", finding_id, errors
        )
        if not isinstance(science_report, dict):
            science_report = {}
        if science_report.get("report_role") != "SCIENCE_ADVISOR":
            errors.append({"code": "science_advisor_report_role_invalid", "finding_id": finding_id})
        if science_report.get("finding_id") != finding_id:
            errors.append({"code": "science_advisor_report_finding_id_mismatch", "finding_id": finding_id})
        if science_report.get("decision") != "SCIENCE_RIGOR_OVERRIDE_SUPPORTED":
            errors.append({"code": "science_advisor_report_decision_invalid", "finding_id": finding_id})
        for field in ("receiver_task_id", "scientific_rigor_assessment", "mechanical_removal_harm"):
            if not nonempty(science_report.get(field)):
                errors.append({"code": f"science_advisor_report_{field}_required", "finding_id": finding_id})
        if science_path and science_path.is_file():
            science_text = science_path.read_text(encoding="utf-8")
            science_upper = science_text.upper()
            if finding_id not in science_text:
                errors.append({"code": "science_advisor_report_file_missing_finding_id", "finding_id": finding_id})
            if "SCIENCE_RIGOR_OVERRIDE_SUPPORTED" not in science_upper:
                errors.append({"code": "science_advisor_report_file_missing_decision", "finding_id": finding_id})
    elif item.get("science_advisor_report") is not None:
        errors.append({"code": "science_advisor_report_for_non_science_exception", "finding_id": finding_id})

    ruling = item.get("controller_ruling")
    ruling_path, _ = validate_bound_file(ruling, "controller_ruling", finding_id, errors)
    if not isinstance(ruling, dict):
        return
    if ruling.get("signed_by") != "CONTROLLER":
        errors.append({"code": "controller_ruling_signature_invalid", "finding_id": finding_id})
    if ruling.get("decision") != "APPROVE_EXCEPTION":
        errors.append({"code": "controller_ruling_decision_invalid", "finding_id": finding_id})
    if ruling.get("finding_id") != finding_id:
        errors.append({"code": "controller_ruling_finding_id_mismatch", "finding_id": finding_id})
    bound_hashes = ruling.get("binding_report_sha256")
    if not isinstance(bound_hashes, list) or sorted(str(x).upper() for x in bound_hashes) != sorted(report_hashes):
        errors.append({"code": "controller_ruling_report_hash_binding_mismatch", "finding_id": finding_id})
    bound_science_sha = ruling.get("binding_science_report_sha256")
    if science_involved is True:
        if bound_science_sha != science_report_sha:
            errors.append({"code": "controller_ruling_science_report_hash_binding_mismatch", "finding_id": finding_id})
    elif bound_science_sha is not None:
        errors.append({"code": "controller_ruling_unexpected_science_report_hash", "finding_id": finding_id})
    if ruling_path and ruling_path.is_file():
        ruling_text = ruling_path.read_text(encoding="utf-8")
        ruling_upper = ruling_text.upper()
        if finding_id not in ruling_text:
            errors.append({"code": "controller_ruling_file_missing_finding_id", "finding_id": finding_id})
        if not re.search(r"SIGNED_BY\s*[:=]\s*CONTROLLER", ruling_upper):
            errors.append({"code": "controller_ruling_file_missing_signature", "finding_id": finding_id})
        if not re.search(r"DECISION\s*[:=]\s*APPROVE_EXCEPTION", ruling_upper):
            errors.append({"code": "controller_ruling_file_missing_decision", "finding_id": finding_id})
        for report_sha in report_hashes:
            if report_sha not in ruling_upper:
                errors.append({"code": "controller_ruling_file_missing_report_sha", "finding_id": finding_id})
        if science_report_sha and science_report_sha not in ruling_upper:
            errors.append({"code": "controller_ruling_file_missing_science_report_sha", "finding_id": finding_id})


def validate_audit(
    audit: dict,
    label: str,
    errors: list[dict],
    expected_schema: str = "natural_prose_audit_v3",
) -> dict[str, dict]:
    if audit.get("schema") != expected_schema:
        errors.append({"code": f"{label}_audit_schema_invalid"})
    findings = audit.get("findings")
    if not isinstance(findings, list):
        errors.append({"code": f"{label}_findings_array_required"})
        return {}
    indexed: dict[str, dict] = {}
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append({"code": f"{label}_finding_object_required", "index": index})
            continue
        finding_id = finding.get("finding_id")
        if not nonempty(finding_id):
            errors.append({"code": f"{label}_finding_id_required", "index": index})
            continue
        if finding_id in indexed:
            errors.append({"code": f"{label}_finding_id_duplicate", "finding_id": finding_id})
            continue
        indexed[finding_id] = finding
    return indexed


def load_house_style_audit(
    dispositions: dict,
    phase: str,
    errors: list[dict],
) -> tuple[dict[str, dict], str | None, str | None]:
    binding = dispositions.get(f"{phase}_house_style_audit")
    path, declared_sha = validate_bound_file(
        binding,
        f"{phase}_house_style_audit",
        "__HOUSE_STYLE_AUDIT__",
        errors,
    )
    if path is None or not path.is_file():
        return {}, str(path.resolve()) if path else None, declared_sha
    try:
        audit = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append({"code": f"{phase}_house_style_audit_unreadable", "detail": str(exc)})
        return {}, str(path.resolve()), declared_sha
    if audit.get("strict_house_style") is not True:
        errors.append({"code": f"{phase}_house_style_strict_mode_required"})
    findings = validate_audit(
        audit,
        f"{phase}_house_style",
        errors,
        expected_schema="natural_prose_house_style_audit_v1",
    )
    return findings, str(path.resolve()), declared_sha


def validate(initial_path: Path, final_path: Path, disposition_path: Path) -> tuple[dict, int]:
    errors: list[dict] = []
    initial = load_json(initial_path)
    final = load_json(final_path)
    dispositions = load_json(disposition_path)

    initial_findings = validate_audit(initial, "initial", errors)
    final_findings = validate_audit(final, "final", errors)

    if dispositions.get("schema") != SCHEMA:
        errors.append({"code": "disposition_schema_invalid"})
    declared_initial_sha = dispositions.get("initial_audit_sha256")
    declared_final_sha = dispositions.get("final_audit_sha256")
    actual_initial_sha = sha256_file(initial_path)
    actual_final_sha = sha256_file(final_path)
    if declared_initial_sha != actual_initial_sha:
        errors.append({"code": "initial_audit_sha256_mismatch"})
    if declared_final_sha != actual_final_sha:
        errors.append({"code": "final_audit_sha256_mismatch"})

    initial_house_findings, initial_house_path, initial_house_sha = load_house_style_audit(
        dispositions, "initial", errors
    )
    final_house_findings, final_house_path, final_house_sha = load_house_style_audit(
        dispositions, "final", errors
    )
    for finding_id, finding in initial_house_findings.items():
        if finding_id in initial_findings:
            errors.append({"code": "initial_cross_audit_finding_id_duplicate", "finding_id": finding_id})
        initial_findings[finding_id] = finding
    for finding_id, finding in final_house_findings.items():
        if finding_id in final_findings:
            errors.append({"code": "final_cross_audit_finding_id_duplicate", "finding_id": finding_id})
        final_findings[finding_id] = finding

    items = dispositions.get("items")
    if not isinstance(items, list):
        errors.append({"code": "disposition_items_array_required"})
        items = []
    indexed_items: dict[str, dict] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append({"code": "disposition_item_object_required", "index": index})
            continue
        finding_id = item.get("finding_id")
        if not nonempty(finding_id):
            errors.append({"code": "disposition_finding_id_required", "index": index})
            continue
        if finding_id in indexed_items:
            errors.append({"code": "disposition_finding_id_duplicate", "finding_id": finding_id})
            continue
        indexed_items[finding_id] = item

    all_known_ids = set(initial_findings) | set(final_findings)
    for finding_id in sorted(set(indexed_items) - all_known_ids):
        errors.append({"code": "disposition_unknown_finding_id", "finding_id": finding_id})
    for finding_id in sorted(set(initial_findings) - set(indexed_items)):
        errors.append({"code": "initial_finding_without_disposition", "finding_id": finding_id})
    for finding_id in sorted(set(final_findings) - set(indexed_items)):
        errors.append({"code": "final_finding_without_disposition", "finding_id": finding_id})

    for finding_id, item in indexed_items.items():
        finding = final_findings.get(finding_id) or initial_findings.get(finding_id)
        if finding is None:
            continue
        disposition = item.get("disposition")
        if disposition == "FIXED":
            if finding_id not in initial_findings:
                errors.append({"code": "fixed_finding_not_in_initial_audit", "finding_id": finding_id})
            if finding_id in final_findings:
                errors.append({"code": "fixed_finding_still_present", "finding_id": finding_id})
            if not nonempty(item.get("repair_summary")):
                errors.append({"code": "fixed_repair_summary_required", "finding_id": finding_id})
            if item.get("final_verification") != "ABSENT_IN_FINAL_AUDIT":
                errors.append({"code": "fixed_final_verification_invalid", "finding_id": finding_id})
        elif disposition == "CONTROLLER_EXCEPTION_APPROVED":
            if finding_id not in final_findings:
                errors.append({"code": "controller_exception_finding_missing_from_final_audit", "finding_id": finding_id})
            validate_controller_exception(item, finding_id, errors)
        else:
            errors.append({"code": "invalid_disposition", "finding_id": finding_id})

    for finding_id, finding in final_findings.items():
        item = indexed_items.get(finding_id, {})
        if item.get("disposition") not in {
            "CONTROLLER_EXCEPTION_APPROVED",
        }:
            errors.append({"code": "final_finding_not_legally_retained", "finding_id": finding_id})

    result = {
        "schema": "natural_prose_project_finding_disposition_validation_v2",
        "policy_id": "PROJECT_FINDING_DISPOSITION_CLOSURE_V2_FOUR_REPORT_EXCEPTION",
        "initial_audit": str(initial_path.resolve()),
        "initial_audit_sha256": actual_initial_sha,
        "final_audit": str(final_path.resolve()),
        "final_audit_sha256": actual_final_sha,
        "initial_house_style_audit": initial_house_path,
        "initial_house_style_audit_sha256": initial_house_sha,
        "final_house_style_audit": final_house_path,
        "final_house_style_audit_sha256": final_house_sha,
        "dispositions": str(disposition_path.resolve()),
        "initial_finding_count": len(initial_findings),
        "final_finding_count": len(final_findings),
        "result": "PASS" if not errors else "BLOCKED",
        "error_count": len(errors),
        "errors": errors,
        "note": (
            "PASS proves disposition completeness only; it does not prove authorship, "
            "external-detector acceptance, fact accuracy, or professional review approval."
        ),
    }
    return result, 0 if not errors else 3


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate project natural-prose finding dispositions")
    parser.add_argument("initial_audit", type=Path)
    parser.add_argument("final_audit", type=Path)
    parser.add_argument("dispositions", type=Path)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    for path in (args.initial_audit, args.final_audit, args.dispositions):
        if not path.is_file():
            parser.error(f"file not found: {path}")
    try:
        result, exit_code = validate(args.initial_audit, args.final_audit, args.dispositions)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
