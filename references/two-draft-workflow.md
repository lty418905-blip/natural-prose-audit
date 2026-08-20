# 同一 agent 双稿工作流

本流程适用于用户明确需要“先出一稿，再根据自审重写一稿”的中文虚构或非虚构任务。它是一个单 agent 的串行工作流：同一个活动 agent 负责冻结约束、完成第一稿、完整阅读并结构化审计、构造第二份输入包、完成第二稿和最终核验。不得创建子智能体，不得把另一个模型的意见伪装成独立审稿，也不依赖特定项目的调用器、注册表或门禁。

## 阶段 0：冻结写作合同

在第一稿前，先在内部建立 `WRITING_CONTRACT`。用户未提供的字段要写成 `UNKNOWN`、`NOT_APPLICABLE` 或待确认，不要默默补齐。

```yaml
workflow_mode: SINGLE_AGENT_TWO_DRAFT
deliverable:                 # 要交回答、故事、章节、评论、教程等
audience:                    # 读者与预期知识水平
form:                        # 文体、视角、时态、格式、语言
source_status:               # 现实材料、用户材料、虚构授权、混合边界
facts_and_sources: []        # 事实、来源、证据等级；虚构可写 ALLOWED_INVENTION
structure_requirements: []  # 必须出现、顺序、结尾、长度或平台限制
character_or_author_position: []
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
  PRIORITY_ORDER:
    - FACTS_AND_USER_CONSTRAINTS
    - VIEWPOINT_AND_PSYCHOLOGY_BOUNDARY
    - GENRE_BASELINE
    - LOCAL_LITERARY_MODULATION
    - RHETORICAL_PREFERENCE
  RETURN_INTERFACE:
    fallback: ""
    unresolved: []
non_negotiables: []
unknowns_and_do_not_infer: []
output_contract:             # 只交第二稿时的标题、标记、引用等要求
```

`GENRE_BASELINE`和`WEB_NARRATIVE_PROFILE`必须先于文学调制。连载或类型文本可用 `RETENTION_ENGINE`（例如“目标—阻力—选择—后果”）、`CONCRETE_CONTAINER`、`TURN_PLACEMENT` 和 `EXIT_PULL` 说明推进；非连载任务将网文层标为 `NOT_APPLICABLE`。`LITERARY_MODULATION`只调节局部叙述距离、显露度、句法、意象、对白和留白，不能变成“每段多少意象”“每千字几次短句”等配额，也不能要求写成某位作者或某部作品。字段需要实际来源时，在 `SOURCE_BINDINGS` 记录路径、SHA、定位、语言/译本状态和采用状态；未选调制要显式写 `status: NONE`。

## 阶段 1：第一稿

第一稿必须是完整可读的候选稿，不是提纲、样段、续写片段或审计说明。先按 `WRITING_CONTRACT` 写作，保持事实与视角边界；不在第一稿前加载详细失败词表，不为了“像人”故意添加错字、病句、随机跳跃、粗口或网络梗。

第一稿默认只保存在当前任务内部。若用户要求查看，可交付并明确它是 `DRAFT_1`，不能让用户误以为它已经是第二稿或最终稿。

## 阶段 2：完整结构化自审

第一稿完成后，先完整通读一次，再形成 `DRAFT_1_AUDIT`。审计不是泛泛说“有点像 AI”，每一项都要能回到稿件位置和功能。位置可用段落／场景编号、行号、字符区间或短的定位摘录；定位摘录只需足够找到问题，不要用长引文替代分析。

### 闪光点卡

闪光点不是夸奖，而是第二稿必须尽量保住的可验证功能。

```yaml
- id: S-01
  location: scene-2 / paragraph-4
  evidence: "足够定位的短摘录或动作摘要"
  function: "character_voice | scene_motion | concrete_detail | relationship | information | rhythm | ending"
  why_it_works: 具体说明它改变了什么或为何属于此人物
  preserve_action: "KEEP | TRANSFER_FUNCTION | REBUILD_IF_NEEDED"
  risk_if_lost: []
```

### 失败点卡

```yaml
- id: F-01
  location: scene-3 / paragraph-2
  evidence: "最短定位摘录或结构位置"
  class: "FACT | VIEWPOINT | CAUSALITY | STRUCTURE | VOICE | RHYTHM | REPETITION | EXPLANATION | FORMAT"
  observed_problem: 可观察的具体问题，不写检测器猜测
  reader_or_story_effect: 对理解、人物、节奏或可信度的影响
  fix_action: "KEEP | DELETE_TAIL | BOUNDED_REPHRASE | REORDER | REBUILD_SCENE | REVIEW_FLAG"
  priority: "MUST_FIX | SHOULD_FIX | OPTIONAL"
  confidence: "HIGH | MEDIUM | LOW"
  do_not_change: []
```

同时登记：

- `FACT_DRIFT_CHECK`：第一稿是否新增、遗漏或改变了事实、来源归属、人物知识、时间、因果或设定。
- `STRUCTURE_CHECK`：每场／每段是否带来动作、信息、关系、风险、判断或理解变化；结尾是否留下合同要求的结果。
- `VOICE_CHECK`：哪些声音差异属于人物／作者位置，哪些只是统一润色造成的表面差异。
- `UNRESOLVED`：证据不足或需要用户决定的项目，不得借重写擅自解决。

脚本命中只是一项证据。不要按命中数量排序，也不要把 `WARNING` 自动升级为失败。审计完成后，停止继续反复全文推演；第二稿只处理已记录且有理由的问题。

## 阶段 3：构造独立的第二份输入包

第二份输入包必须自洽，不能只是“把上稿改好”“减少 AI 味”或把审计全文丢回模型。使用 [two-draft-input-template.md](two-draft-input-template.md) 复制一份 `DRAFT_2_INPUT`，把第一阶段合同、保留的闪光点、必须修复的失败点、禁止回归项和输出格式重新编排。

`draft_source_policy`有两种合法形式：

- `REVISE_FROM_DRAFT_1`：允许读取第一稿全文，以它为可修改的素材；仍必须重新写出完整第二稿，不得只输出差分、替换段或修改日志。
- `REAUTHOR_WITHOUT_DRAFT_1`：不把第一稿全文放入第二份输入，只传递合同、抽象功能和定位后的问题卡；适用于希望第二稿重新组织语言、避免沿用原句或第一稿结构的任务。

默认使用 `REVISE_FROM_DRAFT_1`，除非用户要求更独立的重写，或第一稿存在声线／结构级问题。无论哪种形式，第二份输入至少包含：

1. 完整 `WRITING_CONTRACT`，包括事实、未知和禁推断项。
2. `KEEP_FUNCTIONS`：闪光点的功能摘要与保留方式，不把审计当成可照抄段落。
3. `REQUIRED_REPAIRS`：失败点、证据位置、影响、修复动作和优先级。
4. `REGRESSION_GUARDS`：不得改变的事实、事件顺序、人物知识、关系、视角、引用归属、格式和结尾接口。
5. `OUTPUT_CONTRACT`：第二稿必须完整、自洽、可直接交付；不要输出过程说明、补丁标记或审计标签。

第二份提示词可以在内部写成结构化 YAML/JSON，也可以用 Markdown 的同等字段表达。关键是字段完整、来源边界明确、修复决策可追溯；不要为了格式本身增加无关元数据。

## 阶段 4：第二稿

同一个 agent 读取 `DRAFT_2_INPUT` 后产出一份从头到尾完整的 `DRAFT_2`。它可以保留闪光点的功能，但不应机械复制审计摘录；对于 `REAUTHOR_WITHOUT_DRAFT_1`，不得假装记得第一稿的句子。第二稿不得：

- 只给新增段落、差异、替换表或“其余同上”；
- 为了修复文风而改变事实、因果、人物知识、证据等级或用户指定结构；
- 把失败点列表、检测器术语、内部规则写进正文；
- 以“更自然”为由添加未经授权的现实经历、来源、引语或具体数据。

## 阶段 5：最终核验与停止条件

第二稿完成后，沿用一次轻量而完整的 `FINAL_CHECK`：

1. `FACT_AND_SOURCE_FIDELITY`：事实、来源归属、未知和允许创造是否仍在合同内。
2. `STRUCTURE_AND_COMPLETENESS`：要求的场景／论点／动作／后果是否齐全，第二稿是否可独立阅读。
3. `VOICE_AND_FORM`：人物／作者位置清楚，主导引擎成立，局部文学调制没有变成统一滤镜或配额。
4. `REPAIR_COVERAGE`：每个 `MUST_FIX` 已处理或明确说明不能处理；每个闪光点至少保留功能或记录合理舍弃。
5. `ENDING_AND_FORMAT`：结尾、标题、引用、标记和交付格式符合合同。

如果最终核验失败，不自行串联第三稿。报告具体阻断和需要用户决定的范围；只有用户另行授权，才重新开启一个新版本的双稿流程。第二稿可以交付为最终候选，但不能虚称通过任何外部检测器。

## 用户可见性

默认只交付 `DRAFT_2` 与必要的简短说明。用户要求过程时，可分别交付 `DRAFT_1`、`DRAFT_1_AUDIT`、`DRAFT_2_INPUT` 和 `FINAL_CHECK`；这些是过程记录，不应与第二稿正文混在一起。
