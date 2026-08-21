# Structured Writing Input

Use this template for `SINGLE_AGENT_STRUCTURED_DRAFT`. The same agent creates a `WRITING_INPUT`, checks it, then rereads it before writing. It is an instruction boundary, not a substitute for source material.

```yaml
schema: NATURAL_PROSE_STRUCTURED_INPUT_V1
workflow_mode: SINGLE_AGENT_STRUCTURED_DRAFT
task:
  deliverable: ""
  audience: ""
  form: ""
  language: "zh-CN"
source_boundary:
  source_status: "REALITY | FICTION | MIXED | USER_AUTHORIZED_INVENTION"
  bindings:
    - id: ""
      locator: ""
      version_or_date: ""
      sha256: ""
      relevance: ""
  facts_to_preserve: []
  allowed_inventions: []
  unknowns: []
  do_not_infer: []
viewpoint:
  narrator: ""
  tense: ""
  knowledge_boundary: []
characters:
  - id: ""
    immediate_goal: ""
    pressure: ""
    relationship_state: ""
    permitted_knowledge: []
scene_chain:
  - scene_id: ""
    entry_state: ""
    task_or_desire: ""
    resistance: ""
    visible_change: ""
    exit_state: ""
    required_beats: []
    can_remain_unknown: []
voice_style:
  dominant_mode: ""
  rhythm: ""
  dialogue_function: []
  humor_or_seriousness: ""
  local_modulation: []
life_event_call:
  library_source: "NOT_USED | INLINE_CANDIDATES | AUTHORIZED_FILE"
  selected_event_ids: []
  selection_reason: ""
  max_autonomous_units: 5
  forbidden_event_effects: []
output_contract:
  must_include: []
  must_not_include: []
  format: ""
  title_policy: ""
validation:
  required_fields_checked: true
  source_bindings_checked: true
  event_call_checked: true
  self_audit_status: "PENDING"
```

Rules:

- Keep unavailable facts as `UNKNOWN`; never fill them from genre memory.
- Every selected event ID must resolve to an event card or be explicitly marked `INLINE_CANDIDATE`.
- A structured input must be complete enough to write from, but it should not contain the entire source corpus by default.
- After rereading the input, generate the complete article. Do not emit a plan, delta, or “same as above”.
