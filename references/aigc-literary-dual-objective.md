# AIGC 适配与文学性双目标契约（AIGC_LITERARY_DUAL_OBJECTIVE_V1）

适用范围：文学与证据方法可用于任何任务；文中“项目”“受控生产”“协调者”“正文负责人”和独立报告要求仅指显式启用的 CONTROLLED_PRODUCTION。普通单 Agent 模式保持 SELF_AUDIT_ONLY 与零命中放行，不伪造独立报告或签名。模式与完整执行顺序见 [production-workflow.md](production-workflow.md)。

本契约适用于用户明确要求同时改善文学质量和 AIGC 检测表现的项目写作。它不承诺任何检测器结果，也不伪造人工来源；它规定两类目标在硬事实与结构边界内具有同等优先级。

## 1. 优先级

按以下顺序处理：

1. 事实、因果、人物知识、视角、关系阶段、时间／空间、科研语义和章纲接口是不可破坏的硬边界。
2. 在硬边界内，`LITERARY_FUNCTION` 与 `AIGC_COMPATIBILITY` 是并列目标，不能用一方的短期改善抵销另一方的明显退化。
3. `AIGC_COMPATIBILITY` 表示在固定提交剖面和已绑定证据下，文本形状对当前检测器的可接受性；它不是作者身份判断，也不是普适的人类性证明。

推荐在每轮审计中登记：

```yaml
objective_schema: AIGC_LITERARY_DUAL_OBJECTIVE_V1
literary_regression: PASS | FAILED | PENDING
aigc_compatibility: PASS | FAILED | PENDING | NOT_COMPARABLE
detector_evidence_level: D0_NO_REPORT | D1_SINGLE_RUN | D2_REPEATED_SAME_INPUT | D3_CONTROLLED_AB | ORDERING_ONLY
detector_target_alignment: PASS | PARTIAL | FAIL | UNKNOWN
revision_reason: LITERARY_AND_AIGC_ALIGNED | AIGC_COMPATIBILITY_TARGETED_WITH_GUARDS | LITERARY_ONLY | NONE
user_detector_acceptance: PASS | PENDING | FAILED
source_text_sha256: string
source_text_bytes: number
submission_text_sha256: string | null
submission_text_bytes: number | null
normalization_transform: string | NONE | UNKNOWN
normalization_profile: string | NOT_AVAILABLE
source_submission_identity_status: BYTE_IDENTICAL | SOURCE_SUBMISSION_DIFFERENT_DECLARED_TRANSFORM | SOURCE_SUBMISSION_DIFFERENT_UNEXPLAINED | UNKNOWN
observed_weighted_score: number | null
observed_bucket_shares:
  human: number | null
  suspected_ai: number | null
  ai: number | null
segment_boundary_semantic_check: PASS | PASS_WITH_REVIEW_FLAG | NOT_AVAILABLE
semantic_register_bias_status: NOT_ASSESSED | SUSPECTED | CONTROLLED_REPLICATION
event_pattern_repetition_status: NOT_ASSESSED | CLEAR | REVIEW_FLAG
```

没有可比提交条件时，`aigc_compatibility=NOT_COMPARABLE`，不得把未测写成通过；有用户提供的单次报告时可登记目标和候选，但必须注明 `D1_SINGLE_RUN`，不能把单个红段当作逐句命令。

`observed_weighted_score`与三档字符占比是两个不同观察量：前者按片段字符数加权连续分值，后者按检测器公开阈值把整段字符计入对应桶。两者均应在报告提供足够片段数字时机械复算；不得用一个替代另一个，也不得把跨桶的台阶变化误写成全文连续改善。

`source_text_*`绑定项目候选原件，`submission_text_*`绑定检测器实际接收的文本。用户直接复制粘贴时，两者语义来源可以相同，但平台仍可能压缩空行或删除末尾换行；只要字节不同就不得复用一个SHA。已知归一化必须由`check_segment_semantic_boundaries.py`重新执行并得到`transform_verification_status=PASS`；未知转换只能保留`ORDERING_ONLY`或身份复核提示。

`segment_boundary_semantic_check`只核对检测分段是否落在实际提交文本的UTF-8、句末、行末或段落边界，并标记段内句末、句中／对白中截断。它是解释报告的证据门，不授权为了获得更有利的分段而改标题、空行或正文排版。固定提交剖面首先服务版本可比性。

`semantic_register_bias_status=SUSPECTED`只表示多个可比探针提示检测器可能受内容语域影响；它不是正文缺陷，也不是把小说改成事务说明文的生成规则。只有同母文、单变量、跨两个内容无关场景同方向复现时，才可登记`CONTROLLED_REPLICATION`，仍只作为审计解释，不产生句式／语域配额。

`event_pattern_repetition_status=REVIEW_FLAG`只提示多个章节或事件库重复使用相似的“触发—压力／动作—残留”机制。必须人工判断它是世界规则、人物习惯、必要母题还是可替换模板；不得因签名重复自动拒绝事件或改写正文。

## 2. 允许的检测导向改稿

检测结果可以参与改稿决策，但每项改动都必须绑定一个可见的文学或叙事功能，并说明它如何同时避免模型化形状。允许的方向包括：

- 把均匀的“动作—解释—结论”串改成由人物注意、关系压力或外部事件自然打断的叙述；
- 让对白保留搁置、抢话、答偏、改口或行动后才补足的真实议程；
- 恢复会改变下一动作、风险、关系、知识或节奏的生活纹理与事件后效；
- 把跨人物复用的抽象说明还原为各自可见的动作、物件、口头习惯或代价；
- 在固定提交剖面下，修复已被 D2/D3 或用户可复核报告反复指向的连续机制病灶。

不允许把随机同义替换、故意错别字、标点噪声、固定句长／段长、无功能笑点、元数据改写、标题伪装或跨模型拼接当作检测适配。检测数值可以是并列验收指标，但不能成为脱离文本功能的逐字替换器。

## 3. 网文蒸馏反差调制

`WEB_DISTILLED_CONTRAST` 是一种可选的局部表达形式，不是作者仿写，也不是全章模板。它可以在沉重或高密度段落后，用人物立场差、生活琐事、答非所问、实用性对白、自我拆台或小型外部打断制造反差笑点，从而降低连续“说明—结论”形状并恢复读者契约。

每次使用必须绑定：

```yaml
contrast_modulation:
  status: NONE | SELECTED
  scope_window: "场景或连续段落"
  setup: "前置压力、误会或认真议题"
  contrast_carrier: ACTION | DIALOGUE | OBJECT | SOCIAL_FRICTION | ORDINARY_TASK
  release: "笑点如何显影，不写作者解释"
  aftereffect: "笑点之后仍保留的事实、关系、风险或行动后效"
  disabled_when:
    - "会抹掉创伤、死亡、科研风险或关键关系代价"
    - "需要新增未授权事件、知识或章纲级因果"
    - "只能靠固定频率、段尾金句或无关插科完成"
```

反差必须来自人物和场景已经存在的压力，不能把笑点硬贴到每个高风险段；严肃后果仍需穿过笑点继续生效。网文蒸馏候选先按项目转换门登记 `ADOPTED / ADAPTED / REJECTED`，再进入 `VOICE_STYLE` 卡。

## 4. 放行

候选只有在章纲／事实／结构门通过、`literary_regression=PASS`，且在固定检测剖面下达到用户要求的 `user_detector_acceptance=PASS`（或明确登记 `aigc_compatibility=NOT_COMPARABLE` 并由用户选择继续）时，才可进入后续生产。任何一项失败都保留候选身份，不得声称“不可检测”或“已证明人工写作”。

`CONTROLLED_PRODUCTION`还必须取得`FINDING_DISPOSITION_CLOSURE=PASS`。机械提示全部修改到最终复跑消失；任何保留必须取得正文负责人主智能体与三个独立子智能体四份报告及协调者签名裁决，科研项再附领域审查者报告。章纲层科研豁免只处理无机械命中的覆盖报告项。该逐项处置门与外部检测验收互不替代。
