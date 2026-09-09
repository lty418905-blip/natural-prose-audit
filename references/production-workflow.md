# 通用受控生产与装配流程

本包的文学、证据和机械能力均可用于任意作品。默认仍为单 Agent 写作／自审，沿用零命中机械放行；需要项目级独立审查时，由用户显式选择 `CONTROLLED_PRODUCTION`。这里定义通用角色和流程，不自动调用模型、不扩大创作授权、不要求固定字数。

## 任务配置

在已有工作记录中注明对象、动作、授权范围、采用模式和验收条件，无须另外建配置系统：

- `prose_owner`：正文作者／编辑；
- `controller`：用户指定的协调／采用决定人；
- `reviewer_a / reviewer_b`：真正独立的结构覆盖与叙事闭环上下文；
- `domain_reviewer / continuity_reviewer`：作品需要的专业与连续性审查者；不涉及的专业范围明确 `NOT_APPLICABLE`，不得代签；
- `length_requirement`：只记录用户明确要求及原话；未指定时 `UNSPECIFIED`，不继承任何内部最低值；
- `regression_object / baseline`：任务选择的回归对象与基线，不预设章节；
- `submission_profile`：显式固定编码、标题策略、换行、提交容器与可执行归一化。无标题 UTF-8/LF 无 BOM 可命名为 `BODY_ONLY_UTF8_LF_V1`，它是可选剖面，不是追分技巧；
- `objective_mode`：`LITERARY_ONLY` 或用户要求的 `AIGC_LITERARY_DUAL`；后者分别登记文学回归和用户检测验收，不能互相代替。

参考中的“项目”意为上述受控任务，“正文负责人”“协调者”“领域审查者”是角色。`project_*`、`NOVELIZATION_*` 等既有文件名或 schema 字段保留作接口兼容，不代表专有项目依赖。普通模式不生成假的独立身份、外部调用、ACK 或签名；如果用户所选完整模式的角色不可用，只停止该模式的放行，不妨碍交付只读审计。

## 固定顺序与证据失效

冻结结构／事实和写作输入 → 授权写作与机械装配 → 装配卫生 → 适用的补写文学验收 → 盲态完整冷读／基线对照 → 检测证据核验与机械命中闭合 → 最终独立 A/B → 叙事架构人工量表 → 完整候选验收 → 适用领域／连续性复查 → 用户验收与版本交付。

这是受控模式的唯一顺序；其他参考中的编号列表是检查内容，不得据其前后编号把最终 A/B 提前到正文整改之前。若尚未看过检测材料，冷读必须先于检测阅读；已经看过的上下文不能伪称盲态。正文或结构改变后，相关源身份、补写验收、卫生、冷读、机械处置、A/B、量表和下游审查重新绑定；历史证据原样保留。独立 A/B 在同一冻结窗口并发，互不读取结论；调用重试次数服从任务授权，不因本包自行增加。

完整候选验收检查实际正文而非分段草稿：所有必需场景与接口存在；适用长度要求满足；卫生、机械处置、分段检查、A/B 和量表均闭合；未决事项不被包装成通过。`scripts/validate_prose_review_gate.mjs` 保留完整 A/B、逐场证据、反事实、对白握手、源身份与分段校验，去掉固定章节和隐含长度门。文学、量表、卫生裁决及专业结论仍须责任人实读，不能把该脚本 PASS 冒充整体 PASS。

在存放本轮正文及证据的工作目录运行（脚本可用绝对路径，Node.js 18+）：

```text
node /installed-skill/scripts/validate_prose_review_gate.mjs --prose prose.txt --object-id article --outline-completion-audit a.json --narrative-closure-audit b.json --segment-boundary-audit segment-audit.json --result review-gate.json
```

所有材料和输出都应位于当前工作目录内；输出必须使用新文件名。只有用户明确给出最低 CJK 数时才加 `--minimum-cjk <用户数值>`，未提供时输出 `minimum_cjk=null / length_floor_status=UNSPECIFIED`，没有隐藏目标。其他单位或上限仍按用户原话核验，不擅自换算成 CJK。

## 装配卫生

```text
python scripts/post_assembly_text_hygiene.py prose.txt --object-id article --output hygiene.json
```

可加 `--obsolete-register obsolete.json`。检查非相邻完全／归一化重复、长窗口近重复、引号不平衡或混用、中英文标点、内部过程标记和本轮旧词元。旧词元按当前修订登记原因、允许逐字上下文与来源，不把普通词全局禁用。

硬命中修复后复跑；近重复需判断必要母题、合法引文还是重复结算。近重复的 `LITERARY_JUSTIFIED` 只用于该卫生门的人工处置，不豁免其他机械命中。保留原扫描结果和逐项裁决；不得修改扫描 JSON 冒充自动 PASS。普通单 Agent 模式若采用严格零命中放行，任何残留仍报告 `NOT_RELEASED`。受控模式卫生关闭要求硬命中为零，近重复已 `FIXED|LITERARY_JUSTIFIED`，由负责人合并机械与文学结论。

## 补写后文学验收

新增片段、锚点插入、扩写和长度融合都先绑定：补写前／后完整正文、冻结结构、补写计划、各片段路径／SHA、唯一左右锚点与实际新增字节范围。不能从丢失场景的压缩稿继续灌字。

补写输入保留四条正向约束：

1. 不复述既有事实、心理、观点或结论（NPA-17）。
2. 不以同义复写冒充新推进（NPA-18）。
3. 不连续复用同一句式骨架（NPA-19）。
4. 输出前逐段做删除反事实：删掉会失去什么功能（NPA-20）。

人名、必要指代、准确术语和承担新功能的持续物件不属于禁词。用户长度原话可保留在输出约束中，但算术缺口不是叙事任务，新增规模来自动作、阻力、互动、信息与后效预算。

每个片段逐项检查：`FUNCTION_LOST_IF_REMOVED`、`NOVEL_INFORMATION_OR_STATE_CHANGE`、`OBJECT_AND_SENSORY_RECURRENCE`、`VOICE_AND_SEAM_FIT`、`OUTLINE_AND_FACT_BOUNDARY`、`PLAN_CLOSURE`。全篇临时移除新增片段后冷读，若行动、信息、关系和阅读体验基本不变，登记 `FUNCTIONAL_PADDING_SUSPECTED`，不因字数达标放行。

使用 [验收模板](../assets/post-expansion-literary-acceptance.template.json)，运行：

```text
python scripts/validate_post_expansion_literary_acceptance.py expansion-review.json
```

脚本证明文件身份与记录完整性，不证明人工判断正确。`PASS` 表示每片有有效功能且全文无重复扩写病灶；`REVISION_REQUIRED` 为新增区域可安全修复；`BLOCKED` 为结构丢失、广泛灌水、需改纲或无法保住声线。

## 独立审查与例外

按 [双独立审查合同](project-dual-subagent-review-gate.md) 与四份原有 JSON 模板出具 A/B 和汇合记录。同一对象、结构、正文 SHA；非空且不同的 task/context 身份；不读取同伴报告；两份关闭后才汇合。逐场八项证据、七类闭环风险、反事实与对白—动作握手都保留；正文变化两份同时失效。

实际入件字段按模板：A 使用 `outline_expression_coverage_audit_v2`（`audit_id`、逐项 `scene_coverage` 的 `item_id/status/prose_location/evidence`、顶层 task/context 和 independence）；B 使用 `schema_version=NARRATIVE_LOGIC_CLOSURE_AUDIT_V1`，身份在 `auditor`，七维在 `dimension_evidence`，最终机械状态为 `result`。旧 `OUTLINE_EXPRESSION_COVERAGE_AUDIT_V1` 输入继续支持。概念风险处置词不能代替入件 schema。填入真实检查结果，不把模板的占位符或示例 PASS 当报告。

机械逐项处置运行：

```text
python scripts/validate_project_finding_dispositions.py initial-audit.json final-audit.json dispositions.json
```

保留初始／最终两份结构审计与两份 `check_human_writing.py --strict-house-style --json`。普通 `KEEP/REVIEW_FLAG` 不关闭机械项。确需保留时，依 [例外合同](project-finding-disposition.md) 取得正文负责人＋三个不同独立上下文报告、协调者签名实物；科研项另附领域报告。A/B 不算入四报告。报告数量、独立性与实物绑定不可因通用化减少。

A/B 后由正文负责人执行 [叙事量表](narrative-architecture-human-band-rubric.md)，不再增设一个评审 Agent。QUD、情绪方式、结局与主题、过度整改及五组量表完整保留。只有至少两组、至少三处窗口、全篇主导、必要约束无法解释且有实质文学损害五项同时成立，才判极端偏离；普通偏离不阻断。

## 已完成文本的纯机械修复

只有用户明确采用此例外，且原稿已有所需专业／连续性通过，才可对错字、重复半句、确定标点、成对引号或首尾空白做新版本直落。保留源／目标、逐项原改句位置、预先允许范围、区外字节不变证明、新稿卫生结果与唯一活动版本；旧版可恢复保留。

动作归属、次数、事实、因果、知识、关系、证据强度、专业含义或接口变化不适用；必须回到候选与相应复查。不得把实质改写命名为“病句修复”。
