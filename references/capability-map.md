# 完整能力与资源对应

通用化保留原有单 Agent 能力，并加入完整受控审查。文学功能与证据要求不因移除专有路径、固定章号或模型品牌而删减；仅由任务决定是否启用需要独立角色的生产流程。

| 能力 | 当前资源 |
| --- | --- |
| 单 Agent 结构化成稿、明确长度来源、自审 | structured-input-template.md、self-audit-checklist.md、self-narrative-closure 模板 |
| 同一 Agent 双稿、一次自审与停止条件 | two-draft-workflow.md、two-draft-input-template.md |
| human-writing 核心及五类文体／修订 | human-writing-core.md、human-fiction.md、human-forum-prose.md、human-reality.md、human-formats.md、human-revision.md |
| 六维、认知结构、逐场功能、微循环与压缩回归 | complete-audit-method.md、cognitive-structure.md、scene-level-audit.md、audit_prose.py |
| 状语／补语功能反事实与冗余定位 | modifier-function-audit.md、check_human_writing.py |
| 分段接缝、区外字节保护、句式等价调整 | split-chapter-seam.md、syntax-bounded-rephrase.md |
| 双目标、文风三层、来源采用与撤销 | aigc-literary-dual-objective.md、voice-style-contract.md、controller-style-card-conversion.md |
| 蒸馏技法、入口与章末牵引、钩子疲劳 | method-layer-distilled-novel-toolbox.md、distilled-novel-toolbox-writing-methods.md |
| 盲态冷读、红段、源稿／提交身份与归一化 | ai-trace-audit.md、detector-evidence-and-reverse-effect.md、validate_ai_trace_record.py |
| P0/P1/P2/P2A/P4/P5、正交因素与错配拒收 | detector-mechanism-probes.md、validate_detector_probe_batch.py |
| 全文 UTF-8／句末／对白分段边界 | check_segment_semantic_boundaries.py |
| 连续加权与阈值分桶分层复算 | reconstruct_detector_aggregation.py |
| 离线代理、组留一与均值基线、域外提示 | shadow_detector_scorer.py、shadow-detector-scorer.md |
| 单 Agent 零命中处置 | finding-disposition.md，原有规则保留 |
| 严格逐项处置、四报告签名与科研附加报告 | project-finding-disposition.md、validate_project_finding_dispositions.py |
| 独立 A 覆盖与 B 七维、八字段、对白握手 | project-dual-subagent-review-gate.md、三份独立报告／汇合模板、validate_prose_review_gate.mjs |
| QUD、情绪分布、结局／主题、过度整改、五组极端条件 | narrative-architecture-human-band-rubric.md、量表模板 |
| 装配去重、引号／标点、内部标记、旧词元 | post_assembly_text_hygiene.py、production-workflow.md |
| 补写六项、四条写前约束、全篇删除反事实 | validate_post_expansion_literary_acceptance.py、验收模板、production-workflow.md |
| 冻结候选、专业复查接口、纯机械修复例外 | project-structural-protection.md、production-workflow.md |
| 最近窗口、阶段、封卷及八项连续阅读 | continuous-reading.md |
| Unicode Layer A 及语义字符保留 | unicode_layer_a.py、unicode-layer-a.md |
| 专属生活事件库与链、已选 root、跨章签名比较 | life-event-library.md、validate_life_event_chain.py、scene-event-weaver/ |

保留全部源脚本、两份正文测试夹具、四份独立审计模板和全部源参考；源入口中的详细方法迁入 complete-audit-method.md。原公开仓库的额外文体、事件链、兼容目录和单 Agent 模板仍保留。`self_test.py` 是完整审计回归，`self_test_published.py` 保留公开版回归。

项目外层的正文送审校验也已迁入 `validate_prose_review_gate.mjs`：保留源文件实读、报告独立性、场景覆盖、对白、反事实、分段全覆盖和专业例外核验；CJK 下限变为显式用户参数，无固定章号或隐含目标。测试入口为 `self_test_review_gate.mjs`。

机械检查只证明各自观察与登记，不证明文学判断、专业结论、真实检测通过或项目完成。无真实外部检测时不得把测试夹具当生产证据。
