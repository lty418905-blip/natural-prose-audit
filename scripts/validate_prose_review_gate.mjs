#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
const sha256Buffer = (bytes) => createHash("sha256").update(bytes).digest("hex").toUpperCase();

export const RESULT_SCHEMA = "PROSE_REVIEW_GATE_RESULT_V1";
export const GATE_VERSION = "GENERIC_DUAL_INDEPENDENT_AUDIT-v1-SCENE_EVIDENCE_COUNTERFACTUAL";

export const OUTLINE_COMPLETION_AUDIT_SCHEMA = "OUTLINE_EXPRESSION_COVERAGE_AUDIT_V1";
export const NARRATIVE_CLOSURE_AUDIT_SCHEMA = "NARRATIVE_LOGIC_CLOSURE_AUDIT_V1";
export const SEGMENT_BOUNDARY_AUDIT_SCHEMA = "SEGMENT_BOUNDARY_SEMANTIC_CHECK_V2";

export const REQUIRED_CLOSURE_DIMENSIONS = Object.freeze([
  "ACTION_REASON_OVEREXPLANATION",
  "OBSERVATION_INFERENCE_CONCLUSION",
  "DIALOGUE_QUESTION_ANSWER_CLOSURE",
  "SELF_CORRECTION_TO_RIGHT_ANSWER",
  "UNKNOWN_ENUMERATION_AND_FUTURE_PLAN",
  "SETUP_PAYOFF_SUMMARY_UNIFORMITY",
  "EXTERNAL_INTERRUPTION_AND_RESIDUE",
]);
export const REQUIRED_SCENE_EVIDENCE_FIELDS = Object.freeze([
  "entry_state",
  "immediate_task",
  "resistance",
  "visible_change",
  "exit_state",
  "next_action_dependency",
  "unresolved_or_unknown",
  "closure_level",
]);
const ALLOWED_CLOSURE_LEVELS = new Set(["HARD_CAUSAL", "SOFT_FUNCTIONAL", "OPEN_RESIDUE"]);

const projectRoot = process.cwd();
const canonicalProjectRoot = fs.realpathSync.native(projectRoot);
const validatorPath = fileURLToPath(import.meta.url);

function isCjkIdeograph(codePoint) {
  return (
    (codePoint >= 0x3400 && codePoint <= 0x4dbf) ||
    (codePoint >= 0x4e00 && codePoint <= 0x9fff) ||
    (codePoint >= 0xf900 && codePoint <= 0xfaff) ||
    (codePoint >= 0x20000 && codePoint <= 0x2a6df) ||
    (codePoint >= 0x2a700 && codePoint <= 0x2b73f) ||
    (codePoint >= 0x2b740 && codePoint <= 0x2b81f) ||
    (codePoint >= 0x2b820 && codePoint <= 0x2ceaf) ||
    (codePoint >= 0x2ceb0 && codePoint <= 0x2ebef) ||
    (codePoint >= 0x2ebf0 && codePoint <= 0x2ee5f) ||
    (codePoint >= 0x2f800 && codePoint <= 0x2fa1f) ||
    (codePoint >= 0x30000 && codePoint <= 0x3134f) ||
    (codePoint >= 0x31350 && codePoint <= 0x323af)
  );
}

export function countCjk(text) {
  let count = 0;
  for (const character of text) {
    if (isCjkIdeograph(character.codePointAt(0))) count += 1;
  }
  return count;
}

function isInsideProject(candidate) {
  const relative = path.relative(canonicalProjectRoot, candidate);
  return relative !== ".." && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative);
}

function resolveProjectPath(input, label) {
  if (typeof input !== "string" || !input.trim()) throw new Error(`${label} must be non-empty.`);
  const resolved = path.isAbsolute(input) ? path.resolve(input) : path.resolve(projectRoot, input);
  const relative = path.relative(projectRoot, resolved);
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error(`${label} must stay inside the project root.`);
  }
  return resolved;
}

function assertExistingPathInsideProject(target, label) {
  const canonical = fs.realpathSync.native(target);
  if (!isInsideProject(canonical)) throw new Error(`${label} resolves outside the project root.`);
  return canonical;
}

function assertOutputParentInsideProject(target) {
  let ancestor = path.dirname(target);
  while (!fs.existsSync(ancestor)) {
    const parent = path.dirname(ancestor);
    if (parent === ancestor) throw new Error("result path has no existing project ancestor.");
    ancestor = parent;
  }
  assertExistingPathInsideProject(ancestor, "result path parent");
}

function samePath(left, right) {
  const normalizedLeft = path.resolve(left);
  const normalizedRight = path.resolve(right);
  return process.platform === "win32"
    ? normalizedLeft.toLowerCase() === normalizedRight.toLowerCase()
    : normalizedLeft === normalizedRight;
}



function isSha256(value) {
  return typeof value === "string" && /^[a-f0-9]{64}$/i.test(value);
}

function requireAuditField(condition, code, detail) {
  if (!condition) throw Object.assign(new Error(detail), { gateCode: code });
}

function requireSameStringSet(left, right, code, detail) {
  requireAuditField(Array.isArray(left) && Array.isArray(right), code, detail);
  const leftSet = new Set(left);
  const rightSet = new Set(right);
  requireAuditField(leftSet.size === left.length && rightSet.size === right.length, code, detail);
  requireAuditField(leftSet.size === rightSet.size && [...leftSet].every((value) => rightSet.has(value)), code, detail);
}

function requireDimensionEvidence(value, label) {
  requireAuditField(value && typeof value === "object" && !Array.isArray(value), "NARRATIVE_CLOSURE_AUDIT_DIMENSION_EVIDENCE_MISSING", `${label} must be an object.`);
  requireSameStringSet(
    Object.keys(value),
    REQUIRED_CLOSURE_DIMENSIONS,
    "NARRATIVE_CLOSURE_AUDIT_DIMENSION_EVIDENCE_MISSING",
    `${label} must contain exactly the seven required closure dimensions.`,
  );
  for (const dimension of REQUIRED_CLOSURE_DIMENSIONS) {
    requireAuditField(
      typeof value[dimension] === "string" && value[dimension].trim(),
      "NARRATIVE_CLOSURE_AUDIT_DIMENSION_EVIDENCE_MISSING",
      `${label}.${dimension} must contain non-empty scene-specific evidence.`,
    );
  }
}

function requireSceneEvidence(value, label) {
  requireAuditField(value && typeof value === "object" && !Array.isArray(value), "NARRATIVE_CLOSURE_AUDIT_SCENE_EVIDENCE_MISSING", `${label} must be an object.`);
  for (const field of REQUIRED_SCENE_EVIDENCE_FIELDS) {
    requireAuditField(typeof value[field] === "string" && value[field].trim(), "NARRATIVE_CLOSURE_AUDIT_SCENE_EVIDENCE_MISSING", `${label}.${field} must be non-empty.`);
  }
  requireAuditField(ALLOWED_CLOSURE_LEVELS.has(value.closure_level), "NARRATIVE_CLOSURE_AUDIT_SCENE_EVIDENCE_INVALID", `${label}.closure_level is invalid.`);
}

function requireCounterfactualItems(value, label) {
  requireAuditField(Array.isArray(value), "NARRATIVE_CLOSURE_AUDIT_COUNTERFACTUAL_MISSING", `${label} must be an array.`);
  for (const [index, item] of value.entries()) {
    const prefix = `${label}[${index}]`;
    requireAuditField(item && typeof item === "object" && !Array.isArray(item), "NARRATIVE_CLOSURE_AUDIT_COUNTERFACTUAL_INVALID", `${prefix} must be an object.`);
    for (const field of ["closure_risk_id", "evidence_location", "protected_function", "loosened_form", "narrative_integrity"]) {
      requireAuditField(typeof item[field] === "string" && item[field].trim(), "NARRATIVE_CLOSURE_AUDIT_COUNTERFACTUAL_INVALID", `${prefix}.${field} must be non-empty.`);
    }
    requireAuditField(["INTACT", "HARMED", "UNKNOWN"].includes(item.narrative_integrity), "NARRATIVE_CLOSURE_AUDIT_COUNTERFACTUAL_INVALID", `${prefix}.narrative_integrity is invalid.`);
    requireAuditField(typeof item.next_action_still_understandable === "string" && item.next_action_still_understandable.trim(), "NARRATIVE_CLOSURE_AUDIT_COUNTERFACTUAL_INVALID", `${prefix}.next_action_still_understandable must be non-empty.`);
    requireAuditField(Array.isArray(item.mechanical_finding_ids) && item.mechanical_finding_ids.every((id) => typeof id === "string" && id.trim()), "NARRATIVE_CLOSURE_AUDIT_COUNTERFACTUAL_INVALID", `${prefix}.mechanical_finding_ids must be an array of strings.`);
  }
}

function validateBoundFile(reference, label, code) {
  requireAuditField(reference?.path && typeof reference.path === "string", code, `${label}.path must be present.`);
  requireAuditField(isSha256(reference.sha256), code, `${label}.sha256 must be a SHA-256 value.`);
  const filePath = assertExistingPathInsideProject(resolveProjectPath(reference.path, `${label} path`), `${label} path`);
  requireAuditField(sha256Buffer(fs.readFileSync(filePath)) === reference.sha256, code, `${label}.sha256 does not match the bound file.`);
  return filePath;
}

function readOutlineCompletionAudit(auditPath, { objectId, chapterNumber, prosePath, proseSha256 }) {
  if (!auditPath) {
    throw Object.assign(
      new Error(`Controlled production requires --outline-completion-audit.`),
      { gateCode: "OUTLINE_COMPLETION_AUDIT_REQUIRED" },
    );
  }

  if (!fs.existsSync(auditPath) || !fs.lstatSync(auditPath).isFile()) {
    throw Object.assign(new Error("Outline completion audit record does not exist or is not a regular file."), {
      gateCode: "OUTLINE_COMPLETION_AUDIT_MISSING",
    });
  }

  const auditCanonical = assertExistingPathInsideProject(auditPath, "outline completion audit path");
  let audit;
  let auditBytes;
  try {
    auditBytes = fs.readFileSync(auditCanonical);
    audit = JSON.parse(auditBytes.toString("utf8"));
  } catch (error) {
    throw Object.assign(new Error(`Outline completion audit is not valid UTF-8 JSON: ${error.message}`), {
      gateCode: "OUTLINE_COMPLETION_AUDIT_INVALID",
    });
  }

  requireAuditField(
    audit?.schema_version === OUTLINE_COMPLETION_AUDIT_SCHEMA || audit?.schema === "outline_expression_coverage_audit_v2",
    "OUTLINE_COMPLETION_AUDIT_SCHEMA_INVALID",
    `audit.schema_version must be ${OUTLINE_COMPLETION_AUDIT_SCHEMA}.`,
  );
  if (audit.schema === "outline_expression_coverage_audit_v2") {
    requireAuditField(audit.independence?.execution_mode === "PARALLEL_INDEPENDENT" && audit.independence?.peer_report_read === false && audit.independence?.same_source_allowlist_as_peer === true,
      "OUTLINE_COMPLETION_AUDIT_INDEPENDENCE_INVALID", "v2 coverage requires independent, peer-blind execution with the same source allowlist.");
    requireAuditField(Array.isArray(audit.scene_coverage), "OUTLINE_COMPLETION_AUDIT_MATRIX_MISSING", "scene_coverage must be an array.");
    audit.matrix = audit.scene_coverage.map((item) => ({ ...item, status: item.status === "PRESENT" ? "COVERED" : item.status }));
    audit.auditor = {
      kind: "INDEPENDENT_SUBAGENT", independence: "INDEPENDENT_CONTEXT",
      task_id: audit.task_id, context_id: audit.context_id, one_time: audit.one_time, closed: audit.closed,
      execution_mode: audit.independence.execution_mode, peer_report_read: audit.independence.peer_report_read,
    };
  }
  requireAuditField(audit.auditor?.execution_mode === "PARALLEL_INDEPENDENT" && audit.auditor?.peer_report_read === false,
    "OUTLINE_COMPLETION_AUDIT_INDEPENDENCE_INVALID", "coverage report must declare peer-blind parallel execution.");
  requireAuditField(typeof audit.audit_id === "string" && audit.audit_id.trim(), "OUTLINE_COMPLETION_AUDIT_ID_INVALID", "audit.audit_id must be non-empty.");
  requireAuditField(audit.object_id === objectId, "OUTLINE_COMPLETION_AUDIT_OBJECT_MISMATCH", "audit.object_id does not match --object-id.");
  requireAuditField(audit.coverage_result === "PASS", "OUTLINE_COMPLETION_AUDIT_NOT_PASS", "audit.coverage_result must be PASS.");
  requireAuditField(Array.isArray(audit.matrix) && audit.matrix.length > 0, "OUTLINE_COMPLETION_AUDIT_MATRIX_MISSING", "audit.matrix must contain at least one coverage item.");
  const allowedStatuses = new Set(["COVERED", "PARTIAL", "ABSENT", "CONFLICTING", "NOT_APPLICABLE"]);
  const unresolvedStatuses = new Set(["PARTIAL", "ABSENT", "CONFLICTING"]);
  for (const [index, item] of audit.matrix.entries()) {
    requireAuditField(item && typeof item === "object", "OUTLINE_COMPLETION_AUDIT_MATRIX_INVALID", `audit.matrix[${index}] must be an object.`);
    requireAuditField(typeof item.item_id === "string" && item.item_id.trim(), "OUTLINE_COMPLETION_AUDIT_MATRIX_INVALID", `audit.matrix[${index}].item_id must be non-empty.`);
    requireAuditField(allowedStatuses.has(item.status), "OUTLINE_COMPLETION_AUDIT_MATRIX_INVALID", `audit.matrix[${index}].status is invalid.`);
    requireAuditField(!unresolvedStatuses.has(item.status), "OUTLINE_COMPLETION_AUDIT_UNRESOLVED_COVERAGE", `audit.matrix[${index}] cannot be ${item.status} when coverage_result=PASS.`);
    requireAuditField(typeof item.evidence === "string" && item.evidence.trim() && typeof item.prose_location === "string" && item.prose_location.trim(),
      "OUTLINE_COMPLETION_AUDIT_MATRIX_INVALID", `audit.matrix[${index}] requires evidence and a prose location (or an explicit N/A reason).`);
  }
  requireAuditField(audit.outline_change_required === false, "OUTLINE_COMPLETION_AUDIT_BLOCKERS_PRESENT", "audit.outline_change_required must be false when coverage_result=PASS.");
  requireAuditField(Array.isArray(audit.blocked_scope) && audit.blocked_scope.length === 0, "OUTLINE_COMPLETION_AUDIT_BLOCKERS_PRESENT", "audit.blocked_scope must be an explicit empty array when coverage_result=PASS.");
  requireAuditField(audit.auditor?.kind === "INDEPENDENT_SUBAGENT", "OUTLINE_COMPLETION_AUDIT_INDEPENDENCE_INVALID", "audit.auditor.kind must be INDEPENDENT_SUBAGENT.");
  requireAuditField(audit.auditor?.independence === "INDEPENDENT_CONTEXT", "OUTLINE_COMPLETION_AUDIT_INDEPENDENCE_INVALID", "audit.auditor.independence must be INDEPENDENT_CONTEXT.");
  requireAuditField(typeof audit.auditor?.task_id === "string" && audit.auditor.task_id.trim(), "OUTLINE_COMPLETION_AUDIT_INDEPENDENCE_INVALID", "audit.auditor.task_id must be non-empty.");
  requireAuditField(typeof audit.auditor?.context_id === "string" && audit.auditor.context_id.trim(), "OUTLINE_COMPLETION_AUDIT_INDEPENDENCE_INVALID", "audit.auditor.context_id must be non-empty.");
  requireAuditField(audit.auditor?.one_time === true, "OUTLINE_COMPLETION_AUDIT_ONE_TIME_INVALID", "audit.auditor.one_time must be true.");
  requireAuditField(audit.auditor?.closed === true, "OUTLINE_COMPLETION_AUDIT_NOT_CLOSED", "audit.auditor.closed must be true before prose review dispatch.");
  requireAuditField(audit.prose?.path && typeof audit.prose.path === "string", "OUTLINE_COMPLETION_AUDIT_PROSE_BINDING_INVALID", "audit.prose.path must be present.");
  requireAuditField(samePath(resolveProjectPath(audit.prose.path, "audit prose path"), prosePath), "OUTLINE_COMPLETION_AUDIT_PROSE_MISMATCH", "audit.prose.path does not match the submitted prose path.");
  requireAuditField(audit.prose.sha256 === proseSha256, "OUTLINE_COMPLETION_AUDIT_PROSE_MISMATCH", "audit.prose.sha256 does not match the submitted prose SHA-256.");
  requireAuditField(audit.outline?.path && typeof audit.outline.path === "string", "OUTLINE_COMPLETION_AUDIT_OUTLINE_BINDING_INVALID", "audit.outline.path must be present.");
  const outlinePath = assertExistingPathInsideProject(resolveProjectPath(audit.outline.path, "audit outline path"), "audit outline path");
  requireAuditField(isSha256(audit.outline.sha256), "OUTLINE_COMPLETION_AUDIT_OUTLINE_BINDING_INVALID", "audit.outline.sha256 must be a SHA-256 value.");
  const actualOutlineSha = sha256Buffer(fs.readFileSync(outlinePath));
  requireAuditField(actualOutlineSha === audit.outline.sha256, "OUTLINE_COMPLETION_AUDIT_OUTLINE_MISMATCH", "audit.outline.sha256 does not match the bound outline file.");

  return {
    path: auditCanonical,
    sha256: sha256Buffer(auditBytes),
    audit_id: audit.audit_id,
    outline_path: outlinePath,
    outline_sha256: audit.outline.sha256,
    auditor_task_id: audit.auditor.task_id,
    auditor_context_id: audit.auditor.context_id,
  };
}

function readNarrativeClosureAudit(auditPath, { objectId, chapterNumber, prosePath, proseSha256 }) {
  if (!auditPath) {
    throw Object.assign(
      new Error(`Controlled production requires --narrative-closure-audit.`),
      { gateCode: "NARRATIVE_CLOSURE_AUDIT_REQUIRED" },
    );
  }

  if (!fs.existsSync(auditPath) || !fs.lstatSync(auditPath).isFile()) {
    throw Object.assign(new Error("Narrative closure audit record does not exist or is not a regular file."), {
      gateCode: "NARRATIVE_CLOSURE_AUDIT_MISSING",
    });
  }

  const auditCanonical = assertExistingPathInsideProject(auditPath, "narrative closure audit path");
  let audit;
  let auditBytes;
  try {
    auditBytes = fs.readFileSync(auditCanonical);
    audit = JSON.parse(auditBytes.toString("utf8"));
  } catch (error) {
    throw Object.assign(new Error(`Narrative closure audit is not valid UTF-8 JSON: ${error.message}`), {
      gateCode: "NARRATIVE_CLOSURE_AUDIT_INVALID",
    });
  }

  requireAuditField(
    audit?.schema_version === NARRATIVE_CLOSURE_AUDIT_SCHEMA,
    "NARRATIVE_CLOSURE_AUDIT_SCHEMA_INVALID",
    `audit.schema_version must be ${NARRATIVE_CLOSURE_AUDIT_SCHEMA}.`,
  );
  requireAuditField(typeof audit.audit_id === "string" && audit.audit_id.trim(), "NARRATIVE_CLOSURE_AUDIT_ID_INVALID", "audit.audit_id must be non-empty.");
  requireAuditField(audit.object_id === objectId, "NARRATIVE_CLOSURE_AUDIT_OBJECT_MISMATCH", "audit.object_id does not match --object-id.");
  requireAuditField(audit.report_scope === "FULL_PROSE_BY_SCENE", "NARRATIVE_CLOSURE_AUDIT_SCOPE_INVALID", "audit.report_scope must be FULL_PROSE_BY_SCENE.");
  requireAuditField(audit.auditor?.execution_mode === "PARALLEL_INDEPENDENT" && audit.auditor?.peer_report_read === false,
    "NARRATIVE_CLOSURE_AUDIT_INDEPENDENCE_INVALID", "closure report must declare peer-blind parallel execution.");
  requireAuditField(audit.detector_materials_read === false, "NARRATIVE_CLOSURE_AUDIT_NOT_BLIND", "audit.detector_materials_read must be false.");
  requireAuditField(audit.result === "PASS", "NARRATIVE_CLOSURE_AUDIT_NOT_PASS", "audit.result must be PASS.");
  requireSameStringSet(audit.scene_ids, audit.audited_scene_ids, "NARRATIVE_CLOSURE_AUDIT_SCENE_COVERAGE_INVALID", "audit.scene_ids and audit.audited_scene_ids must be the same non-duplicated set.");
  requireAuditField(audit.scene_ids.length > 0, "NARRATIVE_CLOSURE_AUDIT_SCENE_COVERAGE_INVALID", "audit.scene_ids must not be empty.");
  requireSameStringSet(
    audit.dimensions_checked,
    REQUIRED_CLOSURE_DIMENSIONS,
    "NARRATIVE_CLOSURE_AUDIT_DIMENSIONS_MISSING",
    "audit.dimensions_checked must contain exactly the seven required closure dimensions without duplicates.",
  );
  requireAuditField(Array.isArray(audit.scene_matrix), "NARRATIVE_CLOSURE_AUDIT_MATRIX_MISSING", "audit.scene_matrix must be an array.");
  requireAuditField(audit.scene_matrix.length === audit.scene_ids.length, "NARRATIVE_CLOSURE_AUDIT_SCENE_COVERAGE_INVALID", "audit.scene_matrix must contain one item per scene_id.");

  const sceneIds = new Set(audit.scene_ids);
  const seenScenes = new Set();
  const allowedRiskStatuses = new Set([
    "CLEAR",
    "KEY_SCIENCE_ALLOWED",
    "NON_SCIENCE_REVIEW_REQUIRED",
    "NON_SCIENCE_RETAINED_NARRATIVE_INTEGRITY",
  ]);
  const allowedScienceScopes = new Set(["NON_SCIENCE", "KEY_SCIENCE", "MIXED"]);
  for (const [index, item] of audit.scene_matrix.entries()) {
    const prefix = `audit.scene_matrix[${index}]`;
    requireAuditField(item && typeof item === "object", "NARRATIVE_CLOSURE_AUDIT_MATRIX_INVALID", `${prefix} must be an object.`);
    requireAuditField(typeof item.scene_id === "string" && sceneIds.has(item.scene_id) && !seenScenes.has(item.scene_id), "NARRATIVE_CLOSURE_AUDIT_SCENE_COVERAGE_INVALID", `${prefix}.scene_id must identify one unreported scene.`);
    seenScenes.add(item.scene_id);
    requireAuditField(typeof item.prose_location === "string" && item.prose_location.trim(), "NARRATIVE_CLOSURE_AUDIT_MATRIX_INVALID", `${prefix}.prose_location must be non-empty.`);
    requireSceneEvidence(item.scene_evidence, `${prefix}.scene_evidence`);
    requireAuditField(allowedScienceScopes.has(item.science_scope), "NARRATIVE_CLOSURE_AUDIT_MATRIX_INVALID", `${prefix}.science_scope is invalid.`);
    requireAuditField(allowedRiskStatuses.has(item.risk_status), "NARRATIVE_CLOSURE_AUDIT_MATRIX_INVALID", `${prefix}.risk_status is invalid.`);
    requireSameStringSet(
      item.dimensions_checked,
      REQUIRED_CLOSURE_DIMENSIONS,
      "NARRATIVE_CLOSURE_AUDIT_DIMENSIONS_MISSING",
      `${prefix}.dimensions_checked must contain exactly the seven required closure dimensions without duplicates.`,
    );
    requireDimensionEvidence(item.dimension_evidence, `${prefix}.dimension_evidence`);
    requireAuditField(item.dialogue_action_handshake && typeof item.dialogue_action_handshake === "object" && !Array.isArray(item.dialogue_action_handshake), "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_MISSING", `${prefix}.dialogue_action_handshake must be an object.`);
    const handshake = item.dialogue_action_handshake;
    requireAuditField(handshake.status === "PASS", "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${prefix}.dialogue_action_handshake.status must be PASS.`);
    requireAuditField(typeof handshake.dialogue_present === "boolean", "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${prefix}.dialogue_action_handshake.dialogue_present must be boolean.`);
    requireAuditField(handshake.unresolved_turn_count === 0, "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${prefix}.dialogue_action_handshake.unresolved_turn_count must be 0.`);
    requireAuditField(Array.isArray(handshake.turns), "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${prefix}.dialogue_action_handshake.turns must be an array.`);
    if (handshake.dialogue_present) {
      requireAuditField(handshake.turns.length > 0, "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${prefix}.dialogue_action_handshake.turns must not be empty when dialogue_present=true.`);
      for (const [turnIndex, turn] of handshake.turns.entries()) {
        const turnPrefix = `${prefix}.dialogue_action_handshake.turns[${turnIndex}]`;
        requireAuditField(turn && typeof turn === "object", "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${turnPrefix} must be an object.`);
        for (const field of ["turn_id", "speaker", "agenda", "knowledge_scope", "adjacent_action", "post_turn_state"]) {
          requireAuditField(typeof turn[field] === "string" && turn[field].trim(), "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${turnPrefix}.${field} must be non-empty.`);
        }
      }
    } else {
      requireAuditField(handshake.turns.length === 0, "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${prefix}.dialogue_action_handshake.turns must be empty when dialogue_present=false.`);
      requireAuditField(typeof handshake.no_dialogue_reason === "string" && handshake.no_dialogue_reason.trim(), "NARRATIVE_CLOSURE_AUDIT_DIALOGUE_HANDSHAKE_INVALID", `${prefix}.dialogue_action_handshake.no_dialogue_reason must be non-empty.`);
    }
    requireAuditField(typeof item.evidence === "string" && item.evidence.trim(), "NARRATIVE_CLOSURE_AUDIT_MATRIX_INVALID", `${prefix}.evidence must be non-empty.`);
    requireCounterfactualItems(item.counterfactual_items, `${prefix}.counterfactual_items`);
    if (item.risk_status !== "CLEAR") {
      requireAuditField(item.counterfactual_items.length > 0, "NARRATIVE_CLOSURE_AUDIT_COUNTERFACTUAL_MISSING", `${prefix}.counterfactual_items must contain an item for every non-CLEAR risk.`);
    }
    requireAuditField(Array.isArray(item.mechanical_finding_ids_in_scope), "NARRATIVE_CLOSURE_AUDIT_MATRIX_INVALID", `${prefix}.mechanical_finding_ids_in_scope must be an array.`);
    requireAuditField(
      new Set(item.mechanical_finding_ids_in_scope).size === item.mechanical_finding_ids_in_scope.length && item.mechanical_finding_ids_in_scope.every((findingId) => typeof findingId === "string" && findingId.trim()),
      "NARRATIVE_CLOSURE_AUDIT_MATRIX_INVALID",
      `${prefix}.mechanical_finding_ids_in_scope must contain unique non-empty strings.`,
    );

    requireAuditField(item.risk_status !== "NON_SCIENCE_REVIEW_REQUIRED", "NARRATIVE_CLOSURE_AUDIT_UNRESOLVED", `${prefix} contains unresolved non-science closure risk.`);
    if (item.risk_status === "KEY_SCIENCE_ALLOWED") {
      requireAuditField(item.science_scope === "KEY_SCIENCE", "NARRATIVE_CLOSURE_AUDIT_SCIENCE_EXCEPTION_INVALID", `${prefix}.science_scope must be KEY_SCIENCE.`);
      requireAuditField(item.mechanical_finding_ids_in_scope.length === 0, "NARRATIVE_CLOSURE_AUDIT_SCIENCE_EXCEPTION_INVALID", `${prefix} cannot use direct science allowance when a mechanical finding exists.`);
      requireAuditField(Array.isArray(item.science_sources) && item.science_sources.length > 0, "NARRATIVE_CLOSURE_AUDIT_SCIENCE_EXCEPTION_INVALID", `${prefix}.science_sources must not be empty.`);
      item.science_sources.forEach((reference, sourceIndex) => validateBoundFile(reference, `${prefix}.science_sources[${sourceIndex}]`, "NARRATIVE_CLOSURE_AUDIT_SCIENCE_EXCEPTION_INVALID"));
      requireAuditField(typeof item.scientific_function === "string" && item.scientific_function.trim(), "NARRATIVE_CLOSURE_AUDIT_SCIENCE_EXCEPTION_INVALID", `${prefix}.scientific_function must be non-empty.`);
    }
    if (item.risk_status === "NON_SCIENCE_RETAINED_NARRATIVE_INTEGRITY") {
      requireAuditField(item.science_scope === "NON_SCIENCE", "NARRATIVE_CLOSURE_AUDIT_RETENTION_INVALID", `${prefix}.science_scope must be NON_SCIENCE.`);
      requireAuditField(item.mechanical_finding_ids_in_scope.length === 0, "NARRATIVE_CLOSURE_AUDIT_RETENTION_INVALID", `${prefix} cannot use single-agent retention when a mechanical finding exists.`);
      validateBoundFile(item.retention_evidence, `${prefix}.retention_evidence`, "NARRATIVE_CLOSURE_AUDIT_RETENTION_INVALID");
      requireAuditField(item.counterfactual?.harms_narrative_integrity === true, "NARRATIVE_CLOSURE_AUDIT_RETENTION_INVALID", `${prefix}.counterfactual.harms_narrative_integrity must be true.`);
      requireAuditField(typeof item.counterfactual?.loosened_form === "string" && item.counterfactual.loosened_form.trim(), "NARRATIVE_CLOSURE_AUDIT_RETENTION_INVALID", `${prefix}.counterfactual.loosened_form must be non-empty.`);
      requireAuditField(typeof item.counterfactual?.harm === "string" && item.counterfactual.harm.trim(), "NARRATIVE_CLOSURE_AUDIT_RETENTION_INVALID", `${prefix}.counterfactual.harm must be non-empty.`);
    }
  }
  requireAuditField(audit.unresolved_non_science_count === 0, "NARRATIVE_CLOSURE_AUDIT_UNRESOLVED", "audit.unresolved_non_science_count must be 0 when result=PASS.");
  requireAuditField(audit.auditor?.kind === "INDEPENDENT_SUBAGENT", "NARRATIVE_CLOSURE_AUDIT_INDEPENDENCE_INVALID", "audit.auditor.kind must be INDEPENDENT_SUBAGENT.");
  requireAuditField(audit.auditor?.independence === "INDEPENDENT_CONTEXT", "NARRATIVE_CLOSURE_AUDIT_INDEPENDENCE_INVALID", "audit.auditor.independence must be INDEPENDENT_CONTEXT.");
  requireAuditField(typeof audit.auditor?.task_id === "string" && audit.auditor.task_id.trim(), "NARRATIVE_CLOSURE_AUDIT_INDEPENDENCE_INVALID", "audit.auditor.task_id must be non-empty.");
  requireAuditField(typeof audit.auditor?.context_id === "string" && audit.auditor.context_id.trim(), "NARRATIVE_CLOSURE_AUDIT_INDEPENDENCE_INVALID", "audit.auditor.context_id must be non-empty.");
  requireAuditField(audit.auditor?.one_time === true, "NARRATIVE_CLOSURE_AUDIT_ONE_TIME_INVALID", "audit.auditor.one_time must be true.");
  requireAuditField(audit.auditor?.closed === true, "NARRATIVE_CLOSURE_AUDIT_NOT_CLOSED", "audit.auditor.closed must be true before prose review dispatch.");
  requireAuditField(audit.prose?.path && typeof audit.prose.path === "string", "NARRATIVE_CLOSURE_AUDIT_PROSE_BINDING_INVALID", "audit.prose.path must be present.");
  requireAuditField(samePath(resolveProjectPath(audit.prose.path, "narrative audit prose path"), prosePath), "NARRATIVE_CLOSURE_AUDIT_PROSE_MISMATCH", "audit.prose.path does not match the submitted prose path.");
  requireAuditField(audit.prose.sha256 === proseSha256, "NARRATIVE_CLOSURE_AUDIT_PROSE_MISMATCH", "audit.prose.sha256 does not match the submitted prose SHA-256.");
  const outlinePath = validateBoundFile(audit.outline, "narrative audit outline", "NARRATIVE_CLOSURE_AUDIT_OUTLINE_BINDING_INVALID");

  return {
    path: auditCanonical,
    sha256: sha256Buffer(auditBytes),
    audit_id: audit.audit_id,
    outline_path: outlinePath,
    outline_sha256: audit.outline.sha256,
    auditor_task_id: audit.auditor.task_id,
    auditor_context_id: audit.auditor.context_id,
    scene_count: audit.scene_ids.length,
    required_dimensions: REQUIRED_CLOSURE_DIMENSIONS,
  };
}

function readSegmentBoundaryAudit(auditPath, { chapterNumber, prosePath, proseSha256 }) {
  if (!auditPath) {
    throw Object.assign(
      new Error(`Controlled production requires --segment-boundary-audit.`),
      { gateCode: "SEGMENT_BOUNDARY_AUDIT_REQUIRED" },
    );
  }
  if (!fs.existsSync(auditPath) || !fs.lstatSync(auditPath).isFile()) {
    throw Object.assign(new Error("Segment boundary audit record does not exist or is not a regular file."), {
      gateCode: "SEGMENT_BOUNDARY_AUDIT_MISSING",
    });
  }

  const auditCanonical = assertExistingPathInsideProject(auditPath, "segment boundary audit path");
  let audit;
  let auditBytes;
  try {
    auditBytes = fs.readFileSync(auditCanonical);
    audit = JSON.parse(auditBytes.toString("utf8"));
  } catch (error) {
    throw Object.assign(new Error(`Segment boundary audit is not valid UTF-8 JSON: ${error.message}`), {
      gateCode: "SEGMENT_BOUNDARY_AUDIT_INVALID",
    });
  }

  requireAuditField(audit?.schema === SEGMENT_BOUNDARY_AUDIT_SCHEMA, "SEGMENT_BOUNDARY_AUDIT_SCHEMA_INVALID", `audit.schema must be ${SEGMENT_BOUNDARY_AUDIT_SCHEMA}.`);
  requireAuditField(audit.result === "PASS", "SEGMENT_BOUNDARY_AUDIT_NOT_PASS", "audit.result must be PASS with no semantic review flags.");
  requireAuditField(audit.boundary_unit === "UTF8_BYTES", "SEGMENT_BOUNDARY_AUDIT_UNIT_INVALID", "audit.boundary_unit must be UTF8_BYTES.");
  requireAuditField(audit.coverage_mode === "FULL_DOCUMENT", "SEGMENT_BOUNDARY_AUDIT_SCOPE_INVALID", "audit.coverage_mode must be FULL_DOCUMENT.");
  requireAuditField(typeof audit.submission_path === "string" && samePath(resolveProjectPath(audit.submission_path, "segment submission path"), prosePath), "SEGMENT_BOUNDARY_AUDIT_PROSE_MISMATCH", "audit.submission_path does not match the submitted prose path.");
  requireAuditField(audit.submission_sha256 === proseSha256, "SEGMENT_BOUNDARY_AUDIT_PROSE_MISMATCH", "audit.submission_sha256 does not match the submitted prose SHA-256.");
  const submissionBytes = fs.readFileSync(prosePath);
  requireAuditField(audit.submission_bytes === submissionBytes.byteLength, "SEGMENT_BOUNDARY_AUDIT_PROSE_MISMATCH", "audit.submission_bytes does not match the submitted prose bytes.");
  requireAuditField(audit.review_flag_count === 0 && audit.boundary_review_flag_count === 0 && audit.identity_review_flag_count === 0, "SEGMENT_BOUNDARY_AUDIT_FLAGS_PRESENT", "segment boundary audit contains review flags.");
  requireAuditField(Array.isArray(audit.segments) && audit.segments.length > 0, "SEGMENT_BOUNDARY_AUDIT_SEGMENTS_INVALID", "audit.segments must be a non-empty array.");
  requireAuditField(audit.segment_count === audit.segments.length, "SEGMENT_BOUNDARY_AUDIT_SEGMENTS_INVALID", "audit.segment_count must match audit.segments.length.");
  let previousEnd = 0;
  for (const [index, segment] of audit.segments.entries()) {
    requireAuditField(Number.isInteger(segment?.utf8_start) && Number.isInteger(segment?.utf8_end) && segment.utf8_start === previousEnd && segment.utf8_end > segment.utf8_start, "SEGMENT_BOUNDARY_AUDIT_SEGMENTS_INVALID", `audit.segments[${index}] is not contiguous.`);
    previousEnd = segment.utf8_end;
  }
  requireAuditField(previousEnd === submissionBytes.byteLength, "SEGMENT_BOUNDARY_AUDIT_SEGMENTS_INVALID", "audit.segments must cover the complete submission byte range.");
  requireAuditField(Array.isArray(audit.boundaries) && audit.boundaries.every((boundary) => boundary?.review_flag === false), "SEGMENT_BOUNDARY_AUDIT_FLAGS_PRESENT", "audit.boundaries contains a review flag.");

  return {
    path: auditCanonical,
    sha256: sha256Buffer(auditBytes),
    schema: audit.schema,
    result: audit.result,
    segment_count: audit.segments.length,
    submission_sha256: audit.submission_sha256,
    submission_bytes: audit.submission_bytes,
  };
}

function parseArgs(argv) {
  const parsed = { prose: null, objectId: null, result: null, outlineCompletionAudit: null, narrativeClosureAudit: null, segmentBoundaryAudit: null, minimumCjk: null };
  const names = new Map([
    ["--prose", "prose"],
    ["--minimum-cjk", "minimumCjk"],
    ["--object-id", "objectId"],
    ["--result", "result"],
    ["--outline-completion-audit", "outlineCompletionAudit"],
    ["--narrative-closure-audit", "narrativeClosureAudit"],
    ["--segment-boundary-audit", "segmentBoundaryAudit"],
  ]);
  const seen = new Set();

  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    const field = names.get(key);
    if (!field) throw new Error(`Unsupported argument: ${key}`);
    if (seen.has(key)) throw new Error(`Duplicate argument: ${key}`);
    const value = argv[index + 1];
    if (value === undefined || names.has(value)) throw new Error(`${key} requires a value.`);
    parsed[field] = value;
    seen.add(key);
    index += 1;
  }

  if (!parsed.prose) throw new Error("--prose is required.");
  if (!parsed.objectId?.trim()) throw new Error("--object-id is required.");
  if (!parsed.result) throw new Error("--result is required for versioned gate evidence.");
  if (parsed.minimumCjk !== null) {
    if (!/^\d+$/.test(parsed.minimumCjk)) throw new Error("--minimum-cjk must be a nonnegative integer explicitly requested by the user.");
    parsed.minimumCjk = Number(parsed.minimumCjk);
    if (!Number.isSafeInteger(parsed.minimumCjk)) throw new Error("--minimum-cjk is outside the supported integer range.");
  }
  return parsed;
}

function payloadText(payload) {
  return `${JSON.stringify(payload, null, 2)}\n`;
}

function writeEvidenceExclusive(resultPath, payload) {
  fs.mkdirSync(path.dirname(resultPath), { recursive: true });
  assertOutputParentInsideProject(resultPath);
  if (fs.existsSync(resultPath)) throw new Error("result evidence already exists; choose a new versioned result path.");

  const temporary = `${resultPath}.tmp-${process.pid}-${Date.now()}`;
  try {
    fs.writeFileSync(temporary, payloadText(payload), { encoding: "utf8", flag: "wx" });
    fs.linkSync(temporary, resultPath);
  } finally {
    if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
  }
}

function publishResult(resultPath, payload, stdout) {
  try {
    writeEvidenceExclusive(resultPath, payload);
    stdout.write(payloadText(payload));
    return true;
  } catch (error) {
    stdout.write(payloadText({
      schema_version: RESULT_SCHEMA,
      gate_version: GATE_VERSION,
      result: "INVALID_GATE_INVOCATION",
      error_code: "EVIDENCE_WRITE_ERROR",
      detail: error.message,
    }));
    return false;
  }
}

function invalidPayload(errorCode, detail) {
  return {
    schema_version: RESULT_SCHEMA,
    gate_version: GATE_VERSION,
    result: "INVALID_GATE_INVOCATION",
    error_code: errorCode,
    detail,
  };
}

export function runCli(argv, io = { stdout: process.stdout }) {
  let args;
  try {
    args = parseArgs(argv);
  } catch (error) {
    io.stdout.write(payloadText(invalidPayload("ARGUMENT_ERROR", error.message)));
    return 2;
  }

  let prosePath;
  let resultPath;
  let outlineCompletionAuditPath = null;
  let narrativeClosureAuditPath = null;
  let segmentBoundaryAuditPath = null;
  try {
    prosePath = resolveProjectPath(args.prose, "prose path");
    resultPath = resolveProjectPath(args.result, "result path");
    if (args.outlineCompletionAudit) outlineCompletionAuditPath = resolveProjectPath(args.outlineCompletionAudit, "outline completion audit path");
    if (args.narrativeClosureAudit) narrativeClosureAuditPath = resolveProjectPath(args.narrativeClosureAudit, "narrative closure audit path");
    if (args.segmentBoundaryAudit) segmentBoundaryAuditPath = resolveProjectPath(args.segmentBoundaryAudit, "segment boundary audit path");
    if (outlineCompletionAuditPath && narrativeClosureAuditPath && samePath(outlineCompletionAuditPath, narrativeClosureAuditPath)) {
      throw Object.assign(new Error("outline and narrative closure audits must be separate files."), { gateCode: "AUDIT_REPORT_PATH_COLLISION" });
    }
    const auditPaths = [outlineCompletionAuditPath, narrativeClosureAuditPath, segmentBoundaryAuditPath].filter(Boolean);
    if (new Set(auditPaths.map((auditPath) => path.resolve(auditPath).toLowerCase())).size !== auditPaths.length) {
      throw Object.assign(new Error("outline, narrative closure, and segment boundary audits must be separate files."), { gateCode: "AUDIT_REPORT_PATH_COLLISION" });
    }
    if (samePath(prosePath, resultPath)) throw Object.assign(new Error("prose path and result path must be different."), { gateCode: "PROSE_RESULT_PATH_COLLISION" });
    assertOutputParentInsideProject(resultPath);
    if (fs.existsSync(resultPath)) throw Object.assign(new Error("result evidence already exists; choose a new versioned result path."), { gateCode: "RESULT_EVIDENCE_EXISTS" });
    if (!fs.existsSync(prosePath) || !fs.lstatSync(prosePath).isFile()) throw new Error("Bound prose file does not exist or is not a regular file.");
    assertExistingPathInsideProject(prosePath, "prose path");
  } catch (error) {
    const payload = invalidPayload(error.gateCode ?? "PROSE_OR_RESULT_PATH_INVALID", error.message);
    if (resultPath && !samePath(prosePath ?? resultPath, resultPath) && !fs.existsSync(resultPath)) {
      publishResult(resultPath, payload, io.stdout);
      return 2;
    }
    io.stdout.write(payloadText(payload));
    return 2;
  }

  const proseBytes = fs.readFileSync(prosePath);
  const actualCjk = countCjk(proseBytes.toString("utf8"));
  const common = {
    schema_version: RESULT_SCHEMA,
    gate_version: GATE_VERSION,
    generated_at_utc: new Date().toISOString(),
    object_id: args.objectId.trim(),
    review_scope: "FULL_PROSE_DUAL_REVIEW",
    prose_path: prosePath,
    prose_sha256: sha256Buffer(proseBytes),
    prose_size_bytes: proseBytes.byteLength,
    actual_cjk: actualCjk,
    minimum_cjk: args.minimumCjk,
    validator_path: validatorPath,
    validator_sha256: sha256Buffer(fs.readFileSync(validatorPath)),
    hash_implementation: "node:crypto/createHash/sha256",
  };

  const chapterNumber = null;
  const outlineCompletionAuditRequired = true;
  let outlineCompletionAudit = null;
  let narrativeClosureAudit = null;
  let segmentBoundaryAudit = null;

  // Short prose returns for expansion before final, SHA-bound audits are made.
  if (args.minimumCjk !== null && actualCjk < args.minimumCjk) {
    const written = publishResult(resultPath, {
      ...common,
      result: "ILLEGAL_REVIEW_REQUEST",
      error_code: "PROSE_CJK_BELOW_USER_MINIMUM",
      length_floor_status: "LENGTH_FLOOR_NOT_MET",
      deficit_cjk: args.minimumCjk - actualCjk,
      chapter_number: chapterNumber,
      outline_completion_audit_required: outlineCompletionAuditRequired,
      outline_completion_audit: null,
      narrative_closure_audit_required: outlineCompletionAuditRequired,
      narrative_closure_audit: null,
      segment_boundary_audit_required: outlineCompletionAuditRequired,
      segment_boundary_audit: null,
      independent_audit_pair: null,
      next_action: "RETURN_TO_NOVELIZATION_FOR_EXPANSION_OR_REAUTHORING",
    }, io.stdout);
    return written ? 3 : 2;
  }

  if (outlineCompletionAuditRequired) {
    try {
      outlineCompletionAudit = readOutlineCompletionAudit(outlineCompletionAuditPath, {
        objectId: args.objectId.trim(),
        chapterNumber,
        prosePath,
        proseSha256: common.prose_sha256,
      });
      narrativeClosureAudit = readNarrativeClosureAudit(narrativeClosureAuditPath, {
        objectId: args.objectId.trim(),
        chapterNumber,
        prosePath,
        proseSha256: common.prose_sha256,
      });
      segmentBoundaryAudit = readSegmentBoundaryAudit(segmentBoundaryAuditPath, {
        chapterNumber,
        prosePath,
        proseSha256: common.prose_sha256,
      });
      requireAuditField(
        samePath(outlineCompletionAudit.outline_path, narrativeClosureAudit.outline_path) && outlineCompletionAudit.outline_sha256 === narrativeClosureAudit.outline_sha256,
        "AUDIT_REPORT_PAIR_OUTLINE_MISMATCH",
        "Outline coverage and narrative closure audits must bind the same outline path and SHA-256.",
      );
      requireAuditField(
        outlineCompletionAudit.audit_id !== narrativeClosureAudit.audit_id,
        "AUDIT_REPORT_PAIR_ID_COLLISION",
        "Outline coverage and narrative closure audits must have different audit IDs.",
      );
      requireAuditField(
        outlineCompletionAudit.auditor_task_id !== narrativeClosureAudit.auditor_task_id,
        "AUDIT_REPORT_PAIR_TASK_ID_COLLISION",
        "Two different independent subagents must issue the reports; auditor.task_id values cannot match.",
      );
      requireAuditField(
        outlineCompletionAudit.auditor_context_id !== narrativeClosureAudit.auditor_context_id,
        "AUDIT_REPORT_PAIR_CONTEXT_ID_COLLISION",
        "The two audit reports must come from different independent contexts; auditor.context_id values cannot match.",
      );
    } catch (error) {
      const written = publishResult(resultPath, {
        ...common,
        chapter_number: chapterNumber,
        outline_completion_audit_required: true,
        narrative_closure_audit_required: true,
        segment_boundary_audit_required: true,
        result: "ILLEGAL_REVIEW_REQUEST",
        error_code: error.gateCode ?? "OUTLINE_COMPLETION_AUDIT_INVALID",
        detail: error.message,
        next_action: "RETURN_TO_NOVELIZATION_FOR_TWO_DISTINCT_INDEPENDENT_AUDITS",
      }, io.stdout);
      return written ? 4 : 2;
    }
  }

  const written = publishResult(resultPath, {
    ...common,
    result: "PASS",
    error_code: null,
    length_floor_status: args.minimumCjk === null ? "UNSPECIFIED" : "LENGTH_FLOOR_MET",
    internal_target_status: "NOT_CONFIGURED",
    deficit_cjk: 0,
    chapter_number: chapterNumber,
    outline_completion_audit_required: outlineCompletionAuditRequired,
    outline_completion_audit: outlineCompletionAudit,
    narrative_closure_audit_required: outlineCompletionAuditRequired,
    narrative_closure_audit: narrativeClosureAudit,
    segment_boundary_audit_required: outlineCompletionAuditRequired,
    segment_boundary_audit: segmentBoundaryAudit,
    independent_audit_pair: outlineCompletionAuditRequired ? {
      requirement: "TWO_DISTINCT_INDEPENDENT_SUBAGENTS",
      outline_completion_audit_sha256: outlineCompletionAudit.sha256,
      narrative_closure_audit_sha256: narrativeClosureAudit.sha256,
      auditor_task_ids_distinct: true,
      auditor_context_ids_distinct: true,
    } : null,
    next_action: "REVIEW_INTAKE_ALLOWED",
  }, io.stdout);
  return written ? 0 : 2;
}

const invokedScriptUrl = process.argv[1] ? pathToFileURL(path.resolve(process.argv[1])).href : null;
if (import.meta.url === invokedScriptUrl) process.exitCode = runCli(process.argv.slice(2));
