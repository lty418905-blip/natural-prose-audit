---
name: natural-prose-audit
description: Audit, revise, or create Chinese fiction and nonfiction with a human-readable voice while preserving facts, causality, viewpoint, and user constraints. Supports audit-only work, bounded revision, and a same-agent two-draft workflow; never claims detector evasion.
---

# Natural Prose Audit

这是一个通用的中文写作与审计 Skill。它可以只审计已有稿件、做有界改稿，也可以在同一个活动 agent 内依次完成“冻结约束 → 第一稿 → 结构化自审 → 第二份完整成稿 → 最终核验”。第二稿不是补丁，而是可以独立交付的完整替代稿。

## 先选模式

- **AUDIT_ONLY**：只报告自然度、结构和保真问题，不改正文。
- **BOUNDED_REVISION**：冻结事实、因果、视角和用户要求后，做一次可解释的局部修改。
- **SINGLE_AGENT_TWO_DRAFT**：用户需要先写一稿、再根据闪光点与失败点重写一稿时，读取 [references/two-draft-workflow.md](references/two-draft-workflow.md) 及其结构化模板。
- **EXPLAIN**：用户只问自然度、模型化形状或本 Skill 的边界时，只给方法说明，不虚构检测结论。

若用户没有指定模式，根据交付目标选择；不要因为普通写作自动开启第二稿。用户提到 AIGC、AI 痕迹、检测率或“更像人”时，先按 `AUDIT_ONLY` 建立与源稿 SHA 绑定的冷读结论，再决定是否存在独立于检测器的改稿理由；具体门见 [references/ai-trace-audit.md](references/ai-trace-audit.md)。无论哪种模式，都不创建子智能体，不把本 Skill 变成外部模型调用器，也不把审计代理当作真实检测器。

## 共享不变量

1. 先分清作品是现实、虚构还是混合。现实材料的事实、数字、引语、身份和来源不能臆造；虚构可以创造，但要守住人物知道什么、时间、空间、因果和设定规则。
2. 先保护用户明确的结构、人物声音和有效表达，再处理模型化形状。检测脚本只产生提醒，不产生总分、通过证明或“不可检测”结论。
3. 先按当前文体读取必要参考，不要一次加载全部材料：核心规则见 [references/human-writing-core.md](references/human-writing-core.md)；小说见 [references/human-fiction.md](references/human-fiction.md) 与 [references/fiction-workflow.md](references/fiction-workflow.md)；现实题材见 [references/human-reality.md](references/human-reality.md)；论坛、回答和长文见 [references/human-forum-prose.md](references/human-forum-prose.md)；特殊格式见 [references/human-formats.md](references/human-formats.md)。
4. 初稿或原稿完整读完后，才读 [references/human-revision.md](references/human-revision.md) 做细审；不要用审稿表预先把声音磨平。
5. `VOICE_STYLE`只记录可复用的中性参数；完整字段见 [references/voice-style-contract.md](references/voice-style-contract.md)。主导体裁／叙事引擎、具体容器、转折位置、退出牵引和幽默许可负责推进，叙述距离、情绪显露度、句法舒展或压缩、意象密度、对白显露或回避、留白等只作局部调制。文学调制不是比例配额、仿写指令或作者姓名替代品，不能覆盖事实、结构、人物视角或用户约束。
6. 改稿触及事件、选择、场景顺序、因果、人物知识、关系、时间地点、专业语义、证据强度或结尾功能时，停止自然度清理，回到用户确认或事实／结构审查。
7. 检测报告只决定冷读顺序，不决定正文动作。没有逐段到源稿字节映射、同稿重复检测波动和可复核输入身份时，证据上限为 `ORDERING_ONLY`；不得把百分比、阈值、检测器名称或其猜测特征写进生成提示。
8. 脚本命中少不等于风险低。分布式声线、解释节拍、对白逐题闭合、装配接缝、物件功能过载和动作后唯一释义都可能在词表与句长检查之外；完整冷读不能被 `finding_count` 替代。

## 审计与改稿

先给每个场景或段落找眼下任务、动作、阻力、信息／关系变化和离场结果。再检查六类形状：安全而概括的词、长期同速的句法、模板过渡与重复解释、跨人物复用的作者词、统一润色造成的声线塌缩、所有场景被同一种精致声调覆盖。用上下文判断每个命中应 `KEEP`、`DELETE_TAIL`、`BOUNDED_REPHRASE` 还是 `REVIEW_FLAG`。

检测相关任务先锁定 `PRIMARY_FINDING`、`FINDING_SCOPE`、`VOICE_PROTECTION` 与源稿 SHA。没有这份记录，不得执行 `BOUNDED_REPHRASE`；局部修改没有命中已登记主病灶时，只能标记 `LOCAL_CHANGE_ONLY / PRIMARY_FINDING_UNRESOLVED`。主病灶跨场景、跨人物或跨全文分布时，停止多点局部清洗，改走获授权的完整重写或重新作者流程。跨章／跨文档比较只生成 `REVIEW_FLAG`，不得把高频词表直接交给正文模型批量替换。

已有稿件的改写边界、冷读问题和格式差异，按相关参考文件执行。优先删动作后的重复解释、把抽象判断还原到人／物／动作／后果，保留合理的误解、改口、停顿和普通收尾。禁止随机同义替换、故意错字、病句、固定句长或感官配额。

可选的离线检查：

```text
python scripts/check_human_writing.py <稿件路径>
python scripts/audit_prose.py <稿件路径> --mode fiction
python scripts/validate_ai_trace_record.py <冷读记录.json>
```

`check_human_writing.py` 是偏严格的既有 house-style 检查；用户没有要求该风格时，把它当作可解释提醒，不把所有命中都当成通用文学禁令。`audit_prose.py` 是非阻断形状提醒；其命中数不是分数。`validate_ai_trace_record.py` 只验证冷读记录、源稿身份和修订范围，不证明文学判断正确。三者都不能替代完整阅读。

## 交付边界

用户只要成稿时只交成稿；用户要求审计时再交定位、功能、处置和保留理由。第一稿、详细自审卡和第二份提示词默认留在内部，除非用户要求查看。无论交付哪一稿，都不得声称“通过朱雀”、保证绕过检测器或给出没有真实依据的概率。

需要了解来源、许可或与其他公开项目的关系时，读取 [references/source-notes.md](references/source-notes.md)。
