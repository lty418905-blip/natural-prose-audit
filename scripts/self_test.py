#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).with_name("audit_prose.py")
    path = Path(__file__).with_name("self_test_fixture.txt")
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    run = subprocess.run(
        [sys.executable, str(script), str(path), "--mode", "fiction", "--compact"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=child_env,
    )
    result = json.loads(run.stdout)
    kinds = {item["type"] for item in result["findings"]}
    required = {"transition", "author_metaphor", "reversal_template", "repeated_sentence_start"}
    missing = sorted(required - kinds)
    if missing:
        raise SystemExit(f"missing expected findings: {missing}")
    if result["verdict"] != "warnings_only_no_detector_claim":
        raise SystemExit("verdict boundary changed")

    skill_root = script.parent.parent
    contract_files = {
        "SKILL.md": (
            "SINGLE_AGENT_TWO_DRAFT",
            "two-draft-workflow.md",
            "voice-style-contract.md",
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
        "references/scene-level-audit.md": (
            "SCENE_EVIDENCE",
            "entry_state",
            "visible_change",
            "next_action_dependency",
            "closure_level",
        ),
    }
    project_markers = (
        "D:\\shipinzhizuo",
        "VOL1",
        "CH11",
        "call-writing-model",
        "Build-CorpusManifest",
        "Manage-ReviewDispatch",
        "FINAL_CANON_CONTEXT",
    )
    for relative, required in contract_files.items():
        file_path = skill_root / relative
        if not file_path.is_file():
            raise SystemExit(f"missing contract file: {relative}")
        content = file_path.read_text(encoding="utf-8")
        missing_contracts = [needle for needle in required if needle not in content]
        if missing_contracts:
            raise SystemExit(
                f"missing contract fields in {relative}: {missing_contracts}"
            )
        found_markers = [marker for marker in project_markers if marker in content]
        if found_markers:
            raise SystemExit(
                f"project-specific marker in generic file {relative}: {found_markers}"
            )
    structured = (skill_root / "references/structured-input-template.md").read_text(encoding="utf-8")
    checklist = (skill_root / "references/self-audit-checklist.md").read_text(encoding="utf-8")
    events = (skill_root / "references/life-event-library.md").read_text(encoding="utf-8")
    template = (skill_root / "assets/life-event-card.template.json").read_text(encoding="utf-8")
    closure_template = (skill_root / "assets/narrative-closure-audit-v1.template.json").read_text(encoding="utf-8")
    for label, content, required in (
        ("structured-input-template.md", structured, ("NATURAL_PROSE_STRUCTURED_INPUT_V1", "WRITING_INPUT", "life_event_call")),
        ("self-audit-checklist.md", checklist, ("SELF_AUDIT_ONLY", "Pass A", "Pass B", "MECHANICAL_FINDINGS")),
        ("life-event-library.md", events, ("Call chain", "state_out", "REJECTED_OR_MERGED", "2—6")),
        ("life-event-card.template.json", template, ("LIFE_EVENT_CARD_V1", "chain_steps", "forbidden_outcomes")),
        ("narrative-closure-audit-v1.template.json", closure_template, ("SCENE_EVIDENCE", "next_action_dependency", "counterfactual_items", "HARD_CAUSAL")),
    ):
        missing = [needle for needle in required if needle not in content]
        if missing:
            raise SystemExit(f"missing contract fields in {label}: {missing}")
        found_markers = [marker for marker in project_markers if marker in content]
        if found_markers:
            raise SystemExit(f"project-specific marker in generic file {label}: {found_markers}")
    validator = skill_root / "scripts/validate_life_event_chain.py"
    validator_run = subprocess.run(
        [sys.executable, str(validator), "--self-test"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=child_env,
    )
    if "SELF_TEST=PASS" not in validator_run.stdout:
        raise SystemExit("life-event validator self-test did not pass")
    print("SELF_TEST=PASS")
    print("GENERIC_CONTRACT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
