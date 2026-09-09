---
name: natural-prose-audit
description: Write, audit, and revise Chinese prose while preserving facts, causality, viewpoint, and voice. Supports structured single-agent drafts, optional two-draft revision, life-event chains, full literary and detector-evidence audits, and explicitly enabled independent production reviews. Never claims authorship proof or guaranteed detector evasion.
---

# Natural Prose Audit

这是一个通用的中文写作与审计 Skill。它可以只审计已有稿件、做有界改稿，也可以在同一个活动 agent 内先生成结构化写作输入，再重新读取该输入完成一次完整成稿。需要时可显式开启双稿流程，但通用版不要求固定字数，也不默认生成第二稿。

## 先选模式

- **AUDIT_ONLY**：只报告自然度、结构和保真问题，不改正文。
- **BOUNDED_REVISION**：冻结事实、因果、视角和用户要求后，做一次可解释的局部修改。
- **SINGLE_AGENT_STRUCTURED_DRAFT**：先生成 [references/structured-input-template.md](references/structured-input-template.md) 对应的结构化输入，完成自检后由同一 agent 重新读取它，再生成一份完整文章；不设通用字数门，也不自动生成第二稿。
- **SINGLE_AGENT_TWO_DRAFT**：用户需要先写一稿、再根据闪光点与失败点重写一稿时，读取 [references/two-draft-workflow.md](references/two-draft-workflow.md) 及其结构化模板。
- **EXPLAIN**：用户只问自然度、模型化形状或本 Skill 的边界时，只给方法说明，不虚构检测结论。

若用户没有指定模式，创作／续写默认选择 `SINGLE_AGENT_STRUCTURED_DRAFT`，只检查已有文字则选择 `AUDIT_ONLY`；只有用户明确要求第二稿时才选择 `SINGLE_AGENT_TWO_DRAFT`。以上默认模式不创建子智能体，不调用外部模型，也不把审计代理当作真实检测器。

用户明确需要完整独立审查生产链时，可叠加 `CONTROLLED_PRODUCTION`，读取 [production-workflow.md](references/production-workflow.md)。该模式保留独立 A/B、四报告签名例外、补写验收、叙事量表和专业复查接口；不绑定特定项目、章号、作者模型或固定长度。独立上下文不可用时如实标记该模式未完成，不能降级自审后声称同等通过。下文的单 Agent、零命中和无签名通道约束描述默认模式；受控模式仍保留全部命中，只允许有实物证据的例外闭合，绝不将其报告为零命中。

需要兼容旧版 `human-writing` 目录式调用时，可读取 `references/human-writing/` 下的同等通用参考副本；根目录参考文件是当前规范入口。

## 共享不变量

1. 先分清作品是现实、虚构还是混合。现实材料的事实、数字、引语、身份和来源不能臆造；虚构可以创造，但要守住人物知道什么、时间、空间、因果和设定规则。
2. 先保护用户明确的结构、人物声音和有效表达，再处理模型化形状。检测脚本只产生提醒，不产生总分、通过证明或“不可检测”结论。
3. 先按当前文体读取必要参考，不要一次加载全部材料：核心规则见 [references/human-writing-core.md](references/human-writing-core.md)；小说见 [references/human-fiction.md](references/human-fiction.md) 与 [references/fiction-workflow.md](references/fiction-workflow.md)；现实题材见 [references/human-reality.md](references/human-reality.md)；论坛、回答和长文见 [references/human-forum-prose.md](references/human-forum-prose.md)；特殊格式见 [references/human-formats.md](references/human-formats.md)。
4. 初稿或原稿完整读完后，才读 [references/human-revision.md](references/human-revision.md) 做细审；不要用审稿表预先把声音磨平。
5. `VOICE_STYLE`只记录可复用的中性参数；完整字段见 [references/voice-style-contract.md](references/voice-style-contract.md)。主导体裁／叙事引擎、具体容器、转折位置、退出牵引和幽默许可负责推进，叙述距离、情绪显露度、句法舒展或压缩、意象密度、对白显露或回避、留白等只作局部调制。文学调制不是比例配额、仿写指令或作者姓名替代品，不能覆盖事实、结构、人物视角或用户约束。
6. 改稿触及事件、选择、场景顺序、因果、人物知识、关系、时间地点、专业语义、证据强度或结尾功能时，停止自然度清理，回到用户确认或事实／结构审查。
7. 单 agent 不得把自己的两个阅读阶段伪称为独立审查。需要“双视角”时，先完成结构覆盖清单，再重新读取正文，按 [references/self-audit-checklist.md](references/self-audit-checklist.md) 和 [assets/self-narrative-closure-audit-v1.template.json](assets/self-narrative-closure-audit-v1.template.json) 完成逐场叙事闭合清单，并明确标记 `SELF_AUDIT_ONLY`。每场必须提交状态、动作后效、下一动作依赖和未决项的具体证据；抽象的“闭合充分”不能通过。

## 单 agent 结构化成稿

当用户要求创作、续写或重写，但没有要求双稿时，优先使用 `SINGLE_AGENT_STRUCTURED_DRAFT`：

1. 先完整读取已授权材料，生成 `WRITING_INPUT`，至少记录任务、读者、文体、事实／来源、视角、人物目标、场景链、未知项、禁止推断、声音参数、事件库调用范围和输出格式。
2. 对 `WRITING_INPUT` 做一次完整性检查；缺失字段写 `UNKNOWN` 或 `NOT_APPLICABLE`，不得用记忆补齐。
3. 暂停读取原始材料，重新读取刚生成的 `WRITING_INPUT`，只按该输入生成一份完整文章；不要输出提纲代替文章，不要输出“其余同上”。
4. 生成后按 [references/self-audit-checklist.md](references/self-audit-checklist.md) 做一次 `SELF_AUDIT_ONLY`，只修复确有文学或保真理由的问题；不设固定字数要求。

`WRITING_INPUT` 的推荐字段见 [references/structured-input-template.md](references/structured-input-template.md)。如果用户明确要求第二稿，才切换到 `SINGLE_AGENT_TWO_DRAFT`；双稿模式的输入模板和最终核验仍见 [references/two-draft-workflow.md](references/two-draft-workflow.md)。

## 审计与改稿

先给每个场景或段落找眼下任务、动作、阻力、信息／关系变化和离场结果，并填出逐场`SCENE_EVIDENCE`。再检查六类形状：安全而概括的词、长期同速的句法、模板过渡与重复解释、跨人物复用的作者词、统一润色造成的声线塌缩、所有场景被同一种精致声调覆盖。用上下文判断每个命中应 `KEEP`、`DELETE_TAIL`、`BOUNDED_REPHRASE` 还是 `REVIEW_FLAG`。

已有稿件的改写边界、冷读问题和格式差异，按相关参考文件执行。优先删动作后的重复解释、把抽象判断还原到人／物／动作／后果，保留合理的误解、改口、停顿和普通收尾。禁止随机同义替换、故意错字、病句、固定句长或感官配额。

可选的离线检查：

```text
python scripts/check_human_writing.py <稿件路径>
python scripts/audit_prose.py <稿件路径> --mode fiction
```

`check_human_writing.py` 是偏严格的既有 house-style 检查；用户没有要求该风格时，把它当作可解释提醒，不把所有命中都当成通用文学禁令。`audit_prose.py` 是非阻断形状提醒。两者都不能替代完整阅读。

公开版的机械放行门是严格的：凡采用机械检查器的工作，最终 `MECHANICAL_FINDINGS` 必须为 0；任何未处置命中、`REVIEW_FLAG` 或不确定命中都不能标记为放行。审计报告模式可以如实交付非零结果，但必须明确 `NOT_RELEASED`，不能把非零结果包装成通过。该零命中门只约束机械检查结果，不要求抹平合理的人物差异、生活留白或外部检测器的未知分数。

如用户提供外部 AIGC／自然度报告，先记录其提交剖面、分段方式、字符口径、阈值和运行方差，再把报告当作外部证据。不得从单一报告推断普适检测机制，不得把分数下降写成“人类化成功”，也不得通过标题、空行、标点噪声、错别字或固定句长配额制造假象。

## 生活化事件库

生活事件不是随机插曲，而是可检索、可撤回、可追踪的叙事材料。需要时按 [references/life-event-library.md](references/life-event-library.md) 建立或读取事件库，使用 `scripts/validate_life_event_chain.py` 校验调用链。事件库调用至少要留下：候选来源、筛选理由、采用状态、可见步骤、打断／中止点、`state_out`、后效残留和禁止结果。

事件链默认把一个 root event 的连续 2—6 个可见步骤计为一个事件单元；自主事件数量上限是可配置的项目参数，缺省建议为 5，不是普遍硬门。模型只能构筑已选 root event，不能从整库自行抽取第二个事件；装配后必须复盘实际步骤与后效，状态可为 `ADOPTED`、`REJECTED_OR_MERGED`、`REVIEW_FLAG` 或 `NOT_USED`。

需要更细的事件链、场景 profile 或跨文本机制重复检查时，读取嵌套的 [scene-event-weaver/SKILL.md](scene-event-weaver/SKILL.md)。它与本 Skill 共用事件卡，但不会授予新增事实或主要剧情结果的权限。

## 交付边界

用户只要成稿时只交成稿；用户要求审计时再交定位、功能、处置和保留理由。第一稿、详细自审卡和第二份提示词默认留在内部，除非用户要求查看。无论交付哪一稿，都不得声称“通过朱雀”、保证绕过检测器或给出没有真实依据的概率。

需要了解来源、许可或与其他公开项目的关系时，读取 [references/source-notes.md](references/source-notes.md)。

## 增强审计模块

完整审计、结构回退、分布式声线或全面改稿时，先读 [complete-audit-method.md](references/complete-audit-method.md)。它保留全部认知、场景、六维、回归与处置方法；其中角色生产要求仅在显式启用 `CONTROLLED_PRODUCTION` 后生效，普通模式保留文学方法但标为 `SELF_AUDIT_ONLY`。

- 装配稿、有界修订、补写或锚点插入：读 [production-workflow.md](references/production-workflow.md)，运行 `scripts/post_assembly_text_hygiene.py`；补写后使用 `scripts/validate_post_expansion_literary_acceptance.py`。反复述、反同义复写、反连续骨架和逐段删除反事实必须成为补写输入。
- 初稿完成后检查修饰语：读 [modifier-function-audit.md](references/modifier-function-audit.md)。删后不改变时空、动作、程度、因果、视角、声口或后效的装饰应删除；必要限定保留。
- 完整正文：读 [narrative-architecture-human-band-rubric.md](references/narrative-architecture-human-band-rubric.md)，保留 QUD、情绪方式、主题过度决定、过度整改和五组观察。普通偏离仅提醒；只有五项极端条件全部满足才阻断，不能按人类特征配额打分。
- 文风蒸馏候选进入调用卡：读 [controller-style-card-conversion.md](references/controller-style-card-conversion.md)，绑定来源并逐项 `ADOPTED / ADAPTED / REJECTED`；不指定模型品牌。
- 独立生产审查：读 [project-dual-subagent-review-gate.md](references/project-dual-subagent-review-gate.md)、[project-finding-disposition.md](references/project-finding-disposition.md)、[project-structural-protection.md](references/project-structural-protection.md)。报告 A/B 同源但身份不同，场景证据与对白—动作握手均不可省略。
- 跨章与整卷阅读：读 [continuous-reading.md](references/continuous-reading.md)，不能由单章 PASS 推断整体 PASS。

通用模式与源能力逐项对应见 [capability-map.md](references/capability-map.md)。

按任务需要渐进读取以下通用模块；它们不依赖特定项目、审查线程、调用器、角色或内部路径：

- 认知结构与场景级审计：`references/cognitive-structure.md`、`references/scene-level-audit.md`。
- 多段章节接缝：`references/split-chapter-seam.md`。
- AIGC 证据、反向效应与机制探针：`references/ai-trace-audit.md`、`references/detector-evidence-and-reverse-effect.md`、`references/detector-mechanism-probes.md`。
- 句式有界改写：`references/syntax-bounded-rephrase.md`。只允许连续窗口内的语义等价调整，不使用句长或标点配额。
- Unicode Layer A：`references/unicode-layer-a.md`。只在语义冻结后清理高置信不可见控制字符，不声称降低检测率。
- 网文／现实文学局部调制与蒸馏方法：`references/aigc-literary-dual-objective.md`、`references/method-layer-distilled-novel-toolbox.md`、`references/distilled-novel-toolbox-writing-methods.md`。来源只提供可迁移方法，不提供事实、仿写指令或作者身份。

### 机械命中处置

公开版的机械检查器采用严格零命中放行：最终 `MECHANICAL_FINDINGS` 必须为 `0`。任何 `REVIEW_FLAG`、未知命中或未完成处置都只能交付为 `NOT_RELEASED`。在单 agent 模式下，先为每个 finding 建立 `finding_id`、证据位置、功能判断、处置动作和复跑结果；不得以“只是提醒”跳过。

机械命中不等于必须牺牲文学性。若命中涉及事实、因果、人物声音或专业准确性，先保护这些不变量；只有在语义等价、结构不增量且有独立文学或可比检测理由时才做有界改写。无法安全修改时，公开版只能停在 `NOT_RELEASED`，不得自造豁免、审查线程或外部签名通道。

### 生活事件调用链

事件库按 `Inventory -> Filter -> Select -> Seed -> Assemble -> Postcheck -> Disposition` 执行。一个 root event 的 2—6 个可见步骤计为一个单元；调用必须记录来源、筛选理由、状态变化、中止点、后效残留和禁止结果。模型只能构筑已选事件，不得从整库自行抽取第二个事件；跨文本重复只作 `REVIEW_FLAG`，由人工判断是否为必要母题。

### AIGC 机制证据边界

先盲态冷读，再读取分数、红色片段或报告定位；固定提交剖面并分别记录源稿与实际提交文本的 SHA、字节、字符、段落和归一化。P0—P2 只用于确认运行方差、解析和分段因素；P4 才可能在独立文学理由成立时进入 `BOUNDED_REVISION`；P5 不得进入生产。分数变化只能登记为 `AIGC_COMPATIBILITY_SIGNAL`，不能写成作者身份或普适检测结论。

### 结构化输入与双稿

创作模式先生成 `WRITING_INPUT`，完成字段自检后停止读取原始材料，再重新读取该输入生成完整稿件。用户明确要求双稿时，第一稿完成后只做一次结构化自审，分别记录 `KEEP_FUNCTIONS`、`REQUIRED_REPAIRS`、`AIGC_COMPATIBILITY_TARGETS`、`REGRESSION_GUARDS` 和 `UNRESOLVED`，再生成完整第二稿；不自动生成第三稿。
