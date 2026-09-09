# 项目正文双独立子智能体审查门

适用范围：文学与证据方法可用于任何任务；文中“项目”“受控生产”“协调者”“正文负责人”和独立报告要求仅指显式启用的 CONTROLLED_PRODUCTION。普通单 Agent 模式保持 SELF_AUDIT_ONLY 与零命中放行，不伪造独立报告或签名。模式与完整执行顺序见 [production-workflow.md](production-workflow.md)。

本合同适用于显式启用 CONTROLLED_PRODUCTION 的新建或实质修订完整正文候选。它把“章纲有没有被写出来”和“正文是否把普通叙事盘成严密闭环”拆成两项不能互相代签的审查。

## 1. 并行与独立性

实际机械字段以随包 JSON 模板和 `scripts/validate_prose_review_gate.mjs` 为准，运行方法见 [production-workflow.md](production-workflow.md)。报告 A 是 `outline_expression_coverage_audit_v2`，报告 B 是 `NARRATIVE_LOGIC_CLOSURE_AUDIT_V1`；本文 `closure_result` 是处置语义，最终可入件的报告 B 须将已闭合结果记录为 `result=PASS`，并填写全部场景证据，不能只更改结果字段。

正文负责人在候选全文与同版冻结章纲的路径、SHA-256固定后，必须同时建立两个不同子智能体：

- `REPORT_A=OUTLINE_EXPRESSION_COVERAGE`：只核对章纲入口、必需场景、关键选择／后果、关系推进、章末接口及各项表达功能是否在正文中成立。
- `REPORT_B=NARRATIVE_CLOSURE`：只逐场检查第3节七类严密闭环，不用“章纲实现了”替代自然叙事判断。

两者固定遵守：

1. 绑定完全相同的`object_id`、章纲路径／SHA和候选正文路径／SHA；
2. 使用不同且非空的`task_id`和`context_id`，报告路径不同；
3. `execution_mode=PARALLEL_INDEPENDENT`，两者都在启动时获得相同的只读来源白名单；
4. 两个子智能体都不得读取、索取、概括或引用对方的在途或最终报告，固定`peer_report_read=false`；
5. 正文负责人主智能体只能在两份报告均`closed=true`后汇合结论；不得把主智能体先前判断塞给任一子智能体作为预设答案；
6. 某一子智能体失败或重试时，使用新的独立`task_id/context_id`，另一份报告不得作为重试输入；
7. 章纲或候选正文任一字节变化后，两份旧报告同时失效，必须对新SHA重新并行出具，不能只补其中一份。

“并行”指两个独立上下文在同一候选冻结窗口中并发执行，不是先看完A再让B复核A，也不是同一上下文连续扮演两个角色。

## 2. 报告A：章纲表达覆盖

使用`assets/outline-expression-coverage-audit-v2.template.json`。最终报告至少包含：

- `schema=outline_expression_coverage_audit_v2`；
- `report_type=OUTLINE_EXPRESSION_COVERAGE`；
- 同一对象、章纲、正文身份；
- 独立`task_id/context_id`、`one_time=true`、`closed=true`；
- 每项章纲功能的正文位置、可见证据和`PRESENT|PARTIAL|ABSENT|CONFLICTING`；
- `coverage_result=PASS|BLOCKED`。

只有所有必需功能均为`PRESENT`且没有`PARTIAL|ABSENT|CONFLICTING`时，才可写`coverage_result=PASS`。报告A不得把“原因解释得完整”当作覆盖质量，也不得代签报告B；它只登记`narrative_closure_review_delegated_to=REPORT_B`。

## 3. 报告B：叙事闭环逐场审查

使用`assets/narrative-closure-audit-v1.template.json`。每个场景都必须逐项检查以下七维，即使结果为`CLEAR`也不得静默省略：

1. `ACTION_CAUSE_OVEREXPLAINED`：普通动作或事件是否紧跟唯一原因、唯一意义或作者解释；
2. `OBSERVATION_INFERENCE_CONCLUSION_LOOP`：是否连续完成“观察／提问—推理／解释—排除／限定—结论”；
3. `DIALOGUE_QUESTION_ANSWER_EXHAUSTION`：对白是否逐题答完、复述、确认并当场结清双方理解；
4. `SELF_CORRECTION_DIRECT_TO_RIGHT_ANSWER`：人物是否每次误读后都立即自我纠错并直达正确答案；
5. `UNKNOWN_ACCOUNTED_AND_PLANNED_TO_COMPLETION`：`UNKNOWN`是否被盘成完整账目、风险列表和后续计划，反而消灭真实未知；
6. `UNIFORM_SETUP_PAYOFF_SUMMARY_CADENCE`：是否连续、均匀地执行“设置—兑现—总结”，使每一拍完成度相同；
7. `EXTERNAL_INTERRUPTION_AND_RESIDUE`：是否存在由场景真实关系／环境产生的外部介入，残留是否改变后续注意或行动；不得为了降检测值公式化添加事故、敲门、掉东西或消息打断。

报告B为每个风险建立稳定`closure_risk_id`，列出位置、可见证据、必须保留功能、可留白范围、至少一种反事实拆松方式，以及拆松后`narrative_integrity=INTACT|HARMED|UNKNOWN`。它不得自行制造机械`finding_id`；若同一范围已有`audit_prose.py`或严格house-style命中，只能通过`mechanical_finding_links`绑定真实ID。

为防止“填写字段”冒充叙事闭合，`scene_matrix[]`还必须逐场填写`scene_evidence`：`entry_state`、`immediate_task`、`resistance`、`visible_change`、`exit_state`、`next_action_dependency`、`unresolved_or_unknown`和`closure_level`。前七项必须指向正文中的具体状态或动作；`closure_level`只能是`HARD_CAUSAL`、`SOFT_FUNCTIONAL`或`OPEN_RESIDUE`。`HARD_CAUSAL`只用于主选择、医疗／技术安全判断、不可逆后果或场景转换；普通动作不因没有唯一原因而失败。每个非`CLEAR`风险必须在`counterfactual_items[]`中逐项登记原文位置、保护功能、拆松写法、拆松后的`narrative_integrity`以及关联机械命中；没有这些字段不得写PASS。报告不得用“本场逻辑自然”“七维已完成”“字段齐全”作为唯一证据。

`KEY_SCIENCE`重点科研论述可预先严密，但必须绑定来源路径／SHA／位置与科学功能。普通课堂规则、关系对白、生活动作、思想说明或人物自证不属于科研闭环。

报告B最终使用：

- `closure_result=PASS`：七维已逐场审完，所有风险已能安全拆松并在当前候选中消失，或没有风险；
- `closure_result=REVISION_REQUIRED`：非科研风险拆松不伤叙事，正文负责人必须修改；
- `closure_result=NOVELIZATION_COUNTERFACTUAL_REQUIRED`：拆松可能伤害叙事，且同一范围没有机械`finding_id`，交正文负责人按项目单方保留通道裁决；
- `closure_result=KEY_SCIENCE_NO_MECHANICAL_REVIEW`：只有重点科研范围、来源齐全且没有机械`finding_id`；
- `closure_result=MECHANICAL_EXCEPTION_REQUIRED`：同一范围存在机械`finding_id`，不能由报告B或正文负责人单方保留，须走四报告＋协调者例外；科研项再加领域审查者报告。

## 4. 正文负责人处置与重新出报告

- `REVISION_REQUIRED`：正文负责人必须把风险作为改稿依据。正文SHA变化后，A、B两份报告同时作废并对新候选重新并行出具。
- `NOVELIZATION_COUNTERFACTUAL_REQUIRED`：只有同一范围没有机械`finding_id`时，正文负责人可记录`OUTLINE_RISK_RETAIN_NARRATIVE_INTEGRITY`；必须写明反事实改法、具体损害、不可替代功能和更小修法为何不足。
- `KEY_SCIENCE_NO_MECHANICAL_REVIEW`：可按`OUTLINE_KEY_SCIENCE_ALLOWED`处理；直接科研豁免仍只覆盖无机械命中。
- `MECHANICAL_EXCEPTION_REQUIRED`：遵守`project-finding-disposition.md`的正文负责人主智能体＋三个独立子智能体四报告、协调者签名裁决；`science_involved=true`时再绑定领域审查者`SCIENCE_RIGOR_OVERRIDE_SUPPORTED`报告。

### 3.1 对白—动作握手硬门

每个 `scene_matrix` 项都必须有 `dialogue_action_handshake`。`status=PASS`、`unresolved_turn_count=0`；有对白时 `turns` 逐轮记录 `turn_id`、`speaker`、`agenda`、`knowledge_scope`、`adjacent_action`、`post_turn_state`，且六项均非空；无对白时 `dialogue_present=false`、`turns=[]`，并给出非空 `no_dialogue_reason`。该字段由报告B在既有审查中完成，不启动额外模型或单独写对白。这不是要求逐句解释，也不把普通场景升级为科研闭环，而是确认对白确实改变了可见行动或场景状态。

报告A与报告B是每章固定送审前报告，不计入“争议机械命中”的四份例外报告，也不能替代其中任何一份。

## 5. 双报告汇合与送审门

正文负责人使用`assets/dual-subagent-pre-review-binding-v1.template.json`汇合两份实物。送审前必须同时绑定：

- 报告A路径、SHA、`task_id/context_id`、`coverage_result=PASS`；
- 报告B路径、SHA、`task_id/context_id`和最终闭合状态；
- 两报告相同的章纲SHA、正文SHA和对象身份；
- `task_id`两两不同、`context_id`两两不同、`peer_report_read=false`、`one_time=true`、`closed=true`；
- 报告B风险的正文负责人处置、适用机械命中台账或合法例外证据；
- `source_changed_after_reports=false`。

只有上述绑定全部成立且`send_review_gate=PASS`，正文负责人才可建立领域／连续性送审包。缺任一报告、SHA、独立身份或处置闭合，固定`ILLEGAL_REVIEW_REQUEST / DUAL_SUBAGENT_REPORT_GATE_INCOMPLETE`。双报告PASS不替代用户明确的长度要求正文门、`natural-prose-audit`机械命中闭合、领域／连续性双审或用户选定回归对象检测验收。
