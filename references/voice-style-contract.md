# VOICE_STYLE 中性分层契约


这份契约用于写作提示词、审计卡或第二稿输入包。它把主导体裁机制和局部文学调制分开，方便把连载／类型文本的可读性与现实文学取向的局部质感组合起来，而不把它们混成作者仿写要求。项目或用户可以把自己的来源绑定编译进这些字段；本通用 Skill 不预置任何项目路径、作者名或作品名。

## 字段

```yaml
voice_style:
  schema: VOICE_STYLE_LAYERED_V1
  PRIMARY_MODE: ""                 # 当前交付是小说、长帖、评论、对白等
  DOMINANT_LAYER: "WEB_BASELINE | LITERARY_BASELINE | USER_DEFINED"
  GENRE_BASELINE: ""               # 主导体裁或叙事基线；不写作者姓名
  WEB_NARRATIVE_PROFILE:            # 非连载/非类型任务填 status: NOT_APPLICABLE
    status: "ACTIVE | NOT_APPLICABLE"
    READER_CONTRACT: ""             # 读者此刻应获得什么推进或理解
    RETENTION_ENGINE: ""             # 目标—阻力—选择—后果，或该任务的等价推进链
    CONCRETE_CONTAINER: []            # 人、物、劳动、关系、制度、空间、具体问题
    INFORMATION_RELEASE: ""          # 何时让读者知道何事；不得偷渡后台知识
    RHYTHM_DRIVER: ""                # 由行动、压力、信息变化驱动，不用频率配额
    DIALOGUE_FUNCTION: []             # 试探、遮掩、说服、拖延、靠近、推开、保全面子等
    MICRO_PAYOFF: []                  # 局部行动或理解的可见回报
    TURN_PLACEMENT: ""               # 一次必要转折及其可见后果；没有则 NONE
    EXIT_PULL: ""                    # 结尾留下的动作、问题、关系或代价
    humor_permission: "allowed | limited | forbidden"
  LITERARY_MODULATION:               # 不适用或未选时明确写 NONE
    status: "NONE | SELECTED"
    max_active_groups: 1              # 同一局部默认只启用一个调制组
    neutral_parameters:
      narrative_distance: "close | medium | distant | MIXED"
      emotional_explicitness: "explicit | restrained | MIXED"
      syntax: "compressed | spacious | MIXED"
      image_density: "low | medium | high | MIXED"
      dialogue_exposure: "explicit | evasive | MIXED"
      ellipsis_and_silence: "allowed | limited | forbidden"
    scope_window: ""                # 具体场景、段落、转场或任务
    function: ""                    # 该调制帮助解决什么局部表达问题
    disabled_when: []                # 触发时立即回到主导层
      do_not_import: []                # 不带入的事实、语气、术语、情节或成句
  WEB_DISTILLED_CONTRAST:             # 可选的局部网文蒸馏反差；不等于作者仿写
    status: "NONE | SELECTED"
    scope_window: ""
    setup: ""
    contrast_carrier: "ACTION | DIALOGUE | OBJECT | SOCIAL_FRICTION | ORDINARY_TASK"
    release: ""
    aftereffect: ""
    disabled_when: []
  SYNTAX_GUARDS:                      # 只在审计／有界改稿窗口启用
    status: "NONE | SELECTED"
    scope_window: ""
    target_mechanism: ""
    allowed_operations: []             # MERGE / SPLIT / CLAUSE_ORDER / DEFER / DIALOGUE_ACTION / CONCRETE_LANDING
    forbidden_operations: []
    invariants: ["FACTS", "CAUSALITY", "VIEWPOINT", "KNOWLEDGE", "RELATION_STAGE", "ENDING_INTERFACE"]
  SOURCE_BINDINGS:
    - path: ""
      sha256: ""
      locator: ""
      relevance: ""
      source_language: ""             # 便于区分原文、译文与未知来源
      translation_status: "ORIGINAL | TRANSLATED | UNKNOWN"
      adoption_status: "REFERENCE_ONLY | SELECTED | REJECTED | UNKNOWN"
  PROCESS_GUARDS:
    explanation_policy: "ALLOW_WHEN_CAUSALITY_REQUIRES / REVIEW_REPEATED_TAILS"
    dialogue_completion_policy: "ALLOW_PARTIAL_EVASIVE_INTERRUPTED_RESPONSES"
    seam_policy: "CONTINUE_WITHOUT_RESET_OR_RECAP"
    cross_character_voice_protection: []
    detector_material_in_generation_prompt: false
    objective_mode: "AIGC_LITERARY_DUAL | LITERARY_ONLY"
    aigc_compatibility_target: ""
    detector_evidence_level: "D0_NO_REPORT | D1_SINGLE_RUN | D2_REPEATED_SAME_INPUT | D3_CONTROLLED_AB | ORDERING_ONLY"
  PRIORITY_ORDER:
    - FACTS_AND_USER_CONSTRAINTS
    - VIEWPOINT_AND_PSYCHOLOGY_BOUNDARY
    - GENRE_BASELINE
    - LITERARY_FUNCTION_AND_AIGC_COMPATIBILITY
    - LOCAL_LITERARY_MODULATION
    - RHETORICAL_PREFERENCE
  RETURN_INTERFACE:
    fallback: "回到主导体裁的清晰动作、具体锚点和自然停顿"
    unresolved: []
```

## 使用顺序

1. 先填 `PRIMARY_MODE`、`DOMINANT_LAYER`、`GENRE_BASELINE` 与 `WEB_NARRATIVE_PROFILE`。网文层负责读者契约、场景推进、信息释放、对白功能、局部回报和结尾牵引；非连载任务标为 `NOT_APPLICABLE`，不得自行补一个连载钩子。现实文学取向可以作为基线的一部分，但不能用抽象“高级感”替代场景任务。
2. 再填 `LITERARY_MODULATION`、可选的 `WEB_DISTILLED_CONTRAST`，以及仅在审计窗口启用的 `SYNTAX_GUARDS`。叙述距离、情绪显露度、句法舒展度、意象密度、对白显露或回避、沉默与省略、反差笑点和句式操作，都必须有 `scope_window` 和 `function`；句式护栏不得扩展为全章配额。整篇不需要时写 `status: NONE`，不得为了显得有风格或降低检测值而全篇套用。
3. 以 `SOURCE_BINDINGS` 记录实际参考资料的位置、SHA、定位、语言/译本状态和采用状态。若没有可核验文件，写 `UNKNOWN` 或 `REFERENCE_ONLY`，不得凭记忆补精确内容。
4. `PROCESS_GUARDS`保护叙述程序，同时允许记录结构化的 AIGC 适配目标。必要因果解释可以保留；对话可以完整回答，也可以由人物任务自然地产生偏题、搁置或打断；分段续接不得重开场或复述前文。只把机制类别、提交剖面和用户验收目标放入受控返工卡，不把私有阈值、逐句词表或标题伪装放入生成提示。
5. 最终按 `PRIORITY_ORDER` 决策。调制导致事实、因果、视角、人物知识、关系阶段、格式或可读性受损时，调用 `RETURN_INTERFACE.fallback` 并记录 `unresolved`；若文学性通过但 AIGC 适配失败，保留 `AIGC_COMPATIBILITY_TARGETED_WITH_GUARDS` 的最小候选，不得把它误写成文学改善。

## 禁止误用

- 不把 `image_density`、短句数量、段落长度、幽默次数或情绪强度写成配额。
- 不在提示词中要求“写成某位作者／某部现实文学作品的风格”，不拼接长引文；用户提供的风格参考应转译为上述中性参数。
- 不让文学调制取得事实权、来源权、心理诊断权或结构改写权；它不能覆盖用户要求、现实证据或人物视角。
- 不把连载／类型层的牵引机制误写成廉价悬念，也不把现实文学的留白误写成信息缺失。`RETENTION_ENGINE`不得变成“每段反转”或固定钩子间隔；必要意思必须能从动作、关系或已给材料恢复。
- 不把自然度审计结果当成风格真伪或普适检测器结论。调制是否保留，以作品目标、上下文、可比检测证据和最终冷读共同决定；反差窗口不得抹掉严肃后果或变成固定笑点配额。
