# Natural Prose Audit

通用中文写作与审计 Skill，适用于小说、非虚构、回答、论坛长文和其他中文正文。它的目标是保留事实、视角、因果、人物声音与用户约束，同时提供可复核的结构化写作和审计流程。

## 核心能力

- 单 agent 先生成 `WRITING_INPUT`，再重新读取模板完成一次完整成稿。
- 可选的同一 agent 双稿流程：第一稿、自审、第二份完整成稿、最终核验。
- 结构覆盖与叙事闭合的两阶段自审清单，不伪装成独立子 agent 证据。
- 逐场叙事闭合证据模板：状态、任务、阻力、可见变化、退出状态、下一动作依赖、未决项和反事实拆松记录。
- 认知结构、场景级审计、章节接缝和语义等价句式有界改写。
- AIGC 机制探针、提交剖面核验、分段边界检查、报告聚合复算和透明影子评分器。
- Unicode Layer A 清理、AI_TRACE 证据绑定与机械命中逐项处置。
- 网文基线、现实文学局部调制、反差笑点和方法蒸馏的可配置文风卡。
- 生活化事件库：候选筛选、root event 调用、2-6 步链、状态后效、中止点和处置记录。
- 离线形状检查与生活事件链验证器。

## 使用

将此目录作为 Skill 安装到 Codex 的 skills 目录，或直接显式调用 `natural-prose-audit`。

创作任务默认采用：

1. 读取已授权资料，生成结构化 `WRITING_INPUT`。
2. 检查事实、未知项、视角、场景链、声音和事件调用范围。
3. 重新读取 `WRITING_INPUT`，生成完整文章。
4. 执行 `SELF_AUDIT_ONLY`，完成结构覆盖和叙事闭合复核。

需要第二稿时，显式选择 `SINGLE_AGENT_TWO_DRAFT`；通用版不设固定字数要求。

## 机械放行

凡采用机械检查器的工作，最终 `MECHANICAL_FINDINGS` 必须严格为 `0` 才能标记为放行。非零结果可以作为审计报告交付，但必须标记为 `NOT_RELEASED`。

该门不代表外部 AIGC 检测器已经通过，也不允许通过标题、空行、标点噪声、错别字或固定句长制造假象。外部检测报告只能作为有边界的证据，不能单独证明文本质量或检测器机制。

## 生活事件库

事件卡模板位于 `assets/life-event-card.template.json`，规则见 `references/life-event-library.md`。事件调用链为：

`Inventory -> Filter -> Select -> Seed -> Assemble -> Postcheck -> Disposition`

一个 root event 的连续 2-6 个可见步骤计为一个事件单元。默认自主事件上限为可配置建议值 5，而不是普遍硬规则。事件不得新增未授权事实、隐藏知识、科学主张或主要剧情结果。

验证事件链：

```text
python scripts/validate_life_event_chain.py <event-chain.json>
```

## 目录

- `SKILL.md`：入口规则与模式选择。
- `references/structured-input-template.md`：单 agent 结构化写作输入模板。
- `references/self-audit-checklist.md`：结构覆盖与叙事闭合自审清单。
- `assets/narrative-closure-audit-v1.template.json`：单 agent 逐场闭合证据与反事实模板。
- `references/life-event-library.md`：事件卡和调用链规则。
- `scripts/validate_life_event_chain.py`：事件链机械验证器。
- `references/two-draft-workflow.md`：可选双稿工作流。
- `references/cognitive-structure.md`、`references/scene-level-audit.md`：认知与场景层审计。
- `references/split-chapter-seam.md`、`references/syntax-bounded-rephrase.md`：章节接缝和句式有界改写。
- `references/ai-trace-audit.md`、`references/detector-evidence-and-reverse-effect.md`、`references/detector-mechanism-probes.md`：外部检测证据边界和机制探针。
- `references/finding-disposition.md`、`references/structural-protection.md`：通用机械处置与结构保护。
- `references/unicode-layer-a.md`：语义冻结后的 Layer A 清理。
- `references/aigc-literary-dual-objective.md`、`references/method-layer-distilled-novel-toolbox.md`、`references/distilled-novel-toolbox-writing-methods.md`：双目标文风和方法蒸馏。

## 验证

```text
python scripts/self_test.py
python scripts/validate_life_event_chain.py --self-test
python scripts/check_segment_semantic_boundaries.py --help
python scripts/reconstruct_detector_aggregation.py --help
python scripts/shadow_detector_scorer.py --help
```

本 Skill 不调用外部模型，不保证绕过任何检测器，也不把审计提醒自动解释为事实或创作授权。
