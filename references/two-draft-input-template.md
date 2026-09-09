# DRAFT_2_INPUT 模板


这是给同一活动 agent 的第二份完整输入包。删除不适用的示例值，但不要删除字段；未知写 `UNKNOWN`，不适用写 `NOT_APPLICABLE`。模板只规定信息结构，不要求把字段名称写进最终正文。

```yaml
schema: NATURAL_PROSE_TWO_DRAFT_INPUT_V1
workflow_mode: SINGLE_AGENT_TWO_DRAFT
draft_id: DRAFT_2
draft_source_policy: "REVISE_FROM_DRAFT_1 | REAUTHOR_WITHOUT_DRAFT_1"

writing_contract:
  deliverable: ""
  audience: ""
  form: ""
  source_status: "REALITY | FICTION | HYBRID"
  facts_and_sources:
    - fact: ""
      source_or_authority: ""
      certainty: "FACT | ATTRIBUTED | INFERENCE | UNKNOWN | ALLOWED_INVENTION"
  structure_requirements: []
  character_or_author_position: []
  unknowns_and_do_not_infer: []
  non_negotiables: []
  output_contract:
    complete_standalone_text: true
    include_process_notes: false
    include_diff_or_patch: false
    title_and_format: ""

voice_style:
  schema: VOICE_STYLE_LAYERED_V1
  PRIMARY_MODE: ""
  DOMINANT_LAYER: "WEB_BASELINE | LITERARY_BASELINE | USER_DEFINED"
  GENRE_BASELINE: ""
  WEB_NARRATIVE_PROFILE:
    status: "ACTIVE | NOT_APPLICABLE"
    READER_CONTRACT: ""
    RETENTION_ENGINE: ""
    CONCRETE_CONTAINER: []
    INFORMATION_RELEASE: ""
    RHYTHM_DRIVER: ""
    DIALOGUE_FUNCTION: []
    MICRO_PAYOFF: []
    TURN_PLACEMENT: ""
    EXIT_PULL: ""
    humor_permission: "allowed | limited | forbidden"
  LITERARY_MODULATION:
    status: "NONE | SELECTED"
    max_active_groups: 1
    neutral_parameters:
      narrative_distance: "close | medium | distant | MIXED"
      emotional_explicitness: "explicit | restrained | MIXED"
      syntax: "compressed | spacious | MIXED"
      image_density: "low | medium | high | MIXED"
      dialogue_exposure: "explicit | evasive | MIXED"
      ellipsis_and_silence: "allowed | limited | forbidden"
    scope_window: ""
    function: ""
    disabled_when: []
    do_not_import: []
  SOURCE_BINDINGS:
    - path: ""
      sha256: ""
      locator: ""
      relevance: ""
      source_language: ""
      translation_status: "ORIGINAL | TRANSLATED | UNKNOWN"
      adoption_status: "REFERENCE_ONLY | SELECTED | REJECTED | UNKNOWN"
  PROCESS_GUARDS:
    explanation_policy: "ALLOW_WHEN_CAUSALITY_REQUIRES / REVIEW_REPEATED_TAILS"
    dialogue_completion_policy: "ALLOW_PARTIAL_EVASIVE_INTERRUPTED_RESPONSES"
    seam_policy: "CONTINUE_WITHOUT_RESET_OR_RECAP"
    cross_character_voice_protection: []
    detector_material_in_generation_prompt: false
  PRIORITY_ORDER:
    - FACTS_AND_USER_CONSTRAINTS
    - VIEWPOINT_AND_PSYCHOLOGY_BOUNDARY
    - GENRE_BASELINE
    - LOCAL_LITERARY_MODULATION
    - RHETORICAL_PREFERENCE
  RETURN_INTERFACE:
    fallback: ""
    unresolved: []

keep_functions:
  - id: S-01
    location: ""
    function: ""
    preserve_action: "KEEP | TRANSFER_FUNCTION | REBUILD_IF_NEEDED"
    risk_if_lost: []

primary_finding:
  id: "PF-01 | NONE_WITH_REASON"
  source_sha256: ""
  class: "STRUCTURE | DISTRIBUTED_VOICE | RHYTHM | EXPLANATION | SEAM | OTHER"
  scope: "LOCAL | MULTI_SCENE | WHOLE_TEXT"
  evidence_ranges: []
  voice_protection: []
  authorized_action: "AUDIT_ONLY | BOUNDED_REVISION | REAUTHOR_WITHOUT_DRAFT_1"
  detector_independent_reason: ""

required_repairs:
  - id: F-01
    location: ""
    class: "FACT | VIEWPOINT | CAUSALITY | STRUCTURE | VOICE | RHYTHM | REPETITION | EXPLANATION | FORMAT"
    observed_problem: ""
    reader_or_story_effect: ""
    fix_action: "DELETE_TAIL | BOUNDED_REPHRASE | REORDER | REBUILD_SCENE | REVIEW_FLAG"
    priority: "MUST_FIX | SHOULD_FIX | OPTIONAL"
    do_not_change: []

regression_guards:
  - "不得新增未经授权的事实、引语、数据、经历或后台知识"
  - "不得改变人物视角、时间顺序、因果、关系阶段或用户指定结构"
  - "不得把文学调制变成频率、句长、段长或意象配额"
  - "不得在正文中出现审计术语、检测分数或过程说明"
  - "不得把检测器名称、阈值、分段分值、规避假说或目标百分比传入第二稿"

draft_1_source:
  available: "true | false"
  path_or_inline_reference: ""
  use_mode: "READ_AS_MATERIAL | DO_NOT_READ_FULL_TEXT"

output_instructions: |
  写出从开头到结尾的一份完整第二稿。保留 keep_functions 的有效功能，逐项处理与 primary_finding 有明确关系的 required_repairs，遵守 regression_guards。
  只输出正文及 output_contract 要求的格式；不要输出补丁、差异、审计解释或“其余同上”。
```

若 `draft_source_policy=REAUTHOR_WITHOUT_DRAFT_1`，将 `draft_1_source.available` 设为 `false` 或 `use_mode=DO_NOT_READ_FULL_TEXT`，并确保 `keep_functions` 与 `required_repairs` 已经足够说明任务；不要在第二稿里引用第一稿的专有句子。若审计发现事实或结构仍不确定，优先保留 `UNKNOWN` 并在最终核验中报告，不用文字扩写掩盖缺口。
