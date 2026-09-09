# 项目文风候选转换规范（STYLE_CARD_CONVERSION_V1）

适用范围：文学与证据方法可用于任何任务；文中“项目”“受控生产”“协调者”“正文负责人”和独立报告要求仅指显式启用的 CONTROLLED_PRODUCTION。普通单 Agent 模式保持 SELF_AUDIT_ONLY 与零命中放行，不伪造独立报告或签名。模式与完整执行顺序见 [production-workflow.md](production-workflow.md)。

本文件是项目协调者把外部蒸馏候选、独立章纲意见和项目既有声线编译成具体 `VOICE_STYLE` 卡的控制层规范。它不是事实源、作者仿写指令或正文模板。候选在完成本规范前保持 `NOT_YET_ADOPTED`，不得直接进入 `DRAFT`、`FINAL`、`REPAIR` 或 `EXPANSION` 输入。

## 0. 先过身份和漂移门

每个候选必须绑定候选 ID、所在层、原始证据路径、当前 SHA-256、定位和证据等级，以及当前项目外部模型协议、文风参考和本章三层来源（心理、思想、作品时间线）的路径、SHA、相关性和表达形式。任一来源漂移、路径不存在、OCR 只达到 `OCR_DOUBLE_PASS_MATCH`、候选为 `REJECTED` 或 `UNKNOWN` 时，保持 `NOT_ELIGIBLE`，不以旧快照换源。所有 `REJECTED` 候选必须拦截；`UNKNOWN` 只能在满足重评条件后重取证。

## 1. 协调者裁决：问题必须转换为可见表达

协调者先独立读完当前章纲和相关完整来源，再为候选写一条“问题—表达形式”转换，并登记 `ADOPTED / ADAPTED / REJECTED`：

```yaml
candidate_id: ADX-V2-000
adoption_status: ADOPTED | ADAPTED | REJECTED
chapter_scope: "本章或场景窗口"
problem_frame: "可讨论的问题，不写成结论"
expression_form:
  carrier: ACTION | CHOICE | COST | RELATION_FRICTION | OBJECT | INSTITUTIONAL_AFTEREFFECT
  visible_change: "读者能看到的动作、选择或后果"
  forbidden_inference: ["不得直接推出的心理、事实或后台知识"]
  exit_condition: "何时撤销、转弱或回到主导层"
```

`expression_form` 必须是可见载体，不能是“让人物意识到某哲学命题”“增加心理描写”或“写得更像某作者”。独立结构顾问 只提供 `ADVISORY_ONLY` 意见，不替协调者做采用决定。

## 2. 网文层与现实文学调制的分工

两者不是质量等级，也不是全篇比例。先选一个主导层，再在明确窗口启用最多一个局部调制组。

### WEB_BASELINE：连载／类型推进指标

只从下列可观察问题中选与场景有关者，不写频率配额：

- `READER_CONTRACT`：本场读者应跟住的具体问题、任务或关系压力；
- `FORWARD_MOTION`：人物做了什么、被什么阻住、离场时状态如何不同；
- `INFORMATION_RELEASE`：本场新增信息从谁的视角、在何时可见；
- `LOCAL_PAYOFF`：一次动作、选择或关系摩擦产生的局部回报；
- `EXIT_PULL`：结尾留下的可追踪行动、未决代价或关系问题。

网文层不等于“每段钩子”“每场反转”“高密度金句”或“每章必须危机”。日常场景可以只完成一个小动作或一个关系位移；推进用功能判断，不用段数、句数或钩子间隔。

### LITERARY_MODULATION：现实文学局部调制指标

只有当它解决具体表达问题时才启用，必须写 `scope_window` 和 `function`：

- `CAUSAL_AMBIGUITY`：允许人物和读者暂时不能结算原因，但已给行动与后效必须可追踪；
- `TEMPORAL_TEXTURE`：保留等待、重复劳动、环境噪声或普通生活造成的时间感，不能用空泛景物灌字；
- `PARTIAL_SPEECH`：允许半句、改口、偏答、沉默或不解释，关键事实仍须准确传递；
- `ORDINARY_AFTEREFFECT`：重大信息落回普通动作、资源或关系摩擦中，后效不能被笑点抹平；
- `SENSORY_SPECIFICITY`：用眼前物件、身体动作和空间限制替代抽象情绪标签；
- `NON_CLOSURE`：保留合理未决，不在段尾或章末替人物总结主题。

现实文学调制不等于“更晦涩”“更高级”“减少事件”或“去掉推进”。它不能覆盖事实、视角、人物知识、关系阶段、章纲接口或科研语义。

## 3. 最终卡只保留中性字段

```yaml
voice_style:
  schema: PROJECT_VOICE_STYLE_CARD_V1
  dominant_layer: WEB_BASELINE | LITERARY_BASELINE | USER_DEFINED
  genre_baseline: "中性体裁描述"
  scene_window: "本章/场景/段落"
  reader_contract: "一个可验证的阅读任务"
  concrete_containers: ["人物", "物件", "劳动", "制度", "空间"]
  selected_parameters:
    forward_motion: ""
    information_release: ""
    local_payoff: ""
    exit_pull: ""
    literary_modulation: "NONE 或一个明确调制组"
    modulation_function: ""
    web_distilled_contrast: "NONE 或一个有界反差窗口"
    contrast_function: ""
    syntax_guards: "NONE 或一个有界句式调整窗口"
    syntax_operations: []
  aigc_literary_objective:
    mode: AIGC_LITERARY_DUAL | LITERARY_ONLY
    mechanism_target: ""
    evidence_level: D0_NO_REPORT | D1_SINGLE_RUN | D2_REPEATED_SAME_INPUT | D3_CONTROLLED_AB | ORDERING_ONLY
    acceptance_gate: "LITERARY_REGRESSION AND USER_DETECTOR_ACCEPTANCE"
  expression_form:
    carrier: "ACTION/CHOICE/COST/RELATION_FRICTION/OBJECT/INSTITUTIONAL_AFTEREFFECT"
    visible_change: ""
  voice_protection: []
  disabled_when: []
  do_not_import: []
  source_bindings: []
  adoption_status: ADOPTED | ADAPTED
  outline_advisor_record: "路径 + SHA；无则 NOT_TRIGGERED_THIS_OUTLINE"
  audit_guards:
    detector_material_in_prompt: false
    quota_language: false
    author_imitation: false
```

`source_bindings` 必须包含当前文风参考、相关完整心理／思想／时间线来源和协调者裁决记录；未触发的心理层也写 `PSYCHOLOGY_SOURCE_STATUS=NOT_TRIGGERED_THIS_OUTLINE` 与空声明。未登记 `adoption_status` 时，最终卡不能生成。

## 4. 使用和回退

1. 章纲阶段：协调者独立判断 → 已授权的独立结构顾问 `OUTLINE_ADVISOR` → 逐条 `ADOPTED / ADAPTED / REJECTED` → 冻结章纲并双审。
2. 正文阶段：只把转换后的中性字段放入已授权正文调用卡的 `VOICE_STYLE`；候选证据不作为 `PRIOR_DRAFT_ABSTRACT` 或 `CROSS_AUTHOR_EVIDENCE`。
3. 审计阶段：检查表达是否服务场景功能、声线和已绑定的 AIGC 适配目标。候选命中量或检测分数不能单独证明文学改善，但在 `AIGC_LITERARY_DUAL` 模式下可以作为并列验收证据；句式目标只能以 `SYNTAX_BOUNDED_REPHRASE` 形式绑定连续窗口，不能变成全局句型规则。
4. 若调制使事实、因果、人物知识、关系阶段、节奏承重或章末接口受损，回到主导层并登记 `UNRESOLVED`；不得用词语替换掩盖结构问题。
5. 已完成作品不因启用本合同追溯重开。任务选择受控流程后，新对象登记来源、顾问采用决定和适用专业审查；正文变化后重做与身份有关的证据。

## 5. 明确禁止

- 不把蒸馏候选直接写入正文卡或正文提示；
- 不把“网文／现实文学”写成比例、评分或固定段落配额；
- 不用作者姓名、作品名或长引文作为风格指令；
- 不把心理标签、哲学结论、不可见后台知识或检测器猜测直接写成台词、旁白或新事实；
- 不把“降低 AIGC 检测率”变成脱离文本功能的逐词清洗；在 `AIGC_LITERARY_DUAL` 模式下，它可以与独立文学理由共同构成改稿理由。不得承诺任何检测器结果，必须记录证据等级、提交剖面和用户验收。
