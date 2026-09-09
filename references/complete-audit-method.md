# 完整审计与受控生产方法

把检测器视为与文学冷读并列的验收信号，不把它当作者。项目目标是同时让文字在固定提交剖面下具有可接受的 AIGC 检测表现，并像一个具体的人在具体处境中写出来；事实、因果、人物和节奏仍是不可破坏的硬边界。本包已经整合 `human-writing` 的核心、分文体参考、改稿流程和检查脚本；检测适配可以参与改稿，但不等于作者身份证明，也不承诺对所有检测器有效。

用户选择 `AIGC_LITERARY_DUAL_OBJECTIVE_V1` 时，AIGC 检测适配与文学性同等优先；仅要求文学编辑的任务可保持 `LITERARY_ONLY`，无需外部检测。先固定事实、章纲功能、人物声线和提交剖面，再用可比报告定位检测器敏感的叙事形状；检测证据可以进入版本选择和用户放行门，但不能以标题、噪声、随机扰动或元数据伪装冒充正文改善。完整字段见 [aigc-literary-dual-objective.md](aigc-literary-dual-objective.md)。

本文件保存完整方法。模式入口以根 SKILL.md 为准；本文中“项目”和受控流程要求只在用户显式启用 CONTROLLED_PRODUCTION 后生效。单 Agent 保留所有文学检查，但仅出具 SELF_AUDIT_ONLY，不能宣称完成独立 A/B 或签名例外。详见 [production-workflow.md](production-workflow.md)。

## 先选模式与权限

- `AUDIT_ONLY`：默认模式；完整冷读、定位机制、保护项和处置建议，不改正文。
- `BOUNDED_REVISION`：只有用户或项目流程明确授权时使用；先冻结事实／结构／声线，再做一次可解释的局部修改。
- `SINGLE_AGENT_TWO_DRAFT`：用户明确要求“初稿→结构化自审→第二稿”时使用同一个活动 agent 串行完成；不得创建子智能体冒充独立审稿。流程细节见 `two-draft-workflow.md` 与 `two-draft-input-template.md`。
- `EXPLAIN`：只解释自然度、模型化形状或检测证据边界，不生成正文。

项目生产链默认停留在 `AUDIT_ONLY`。任何改写必须另有版本化授权、正文身份和项目闸门；本 Skill 不自行解除领域／连续性双审、正文门或作者隔离。

## 选择工作方式

- 新写或实质重写任何正文时，先读 `human-writing-core.md`，再按下列文体路由读取参考。
- 小说、故事、虚构散文与对白，读取 `human-fiction.md`、`fiction-workflow.md`、`cognitive-structure.md`和`scene-level-audit.md`。若章节由多段连续生成或机械装配，再读取`split-chapter-seam.md`。
- 在`CONTROLLED_PRODUCTION`处理章纲逻辑闭环风险或正文机械命中时，另读`project-finding-disposition.md`。该参考规定章纲端只预警、正文负责人端逐项反事实裁决和最终机械闭合；不得以“脚本只是提醒”为由跳过命中项。
- 在`CONTROLLED_PRODUCTION`为受控生产模式完整候选建立送审前子智能体审查时，必须另读`project-dual-subagent-review-gate.md`。固定并行建立A章纲表达覆盖与B叙事闭环两个不同子智能体；两者绑定同一章纲／正文SHA但使用不同`task_id/context_id`，互不读取对方结论。正文负责人必须把两份报告路径与真实SHA同时写入送审门绑定，缺一份即非法入件。
- 在`CONTROLLED_PRODUCTION`审查完整正文候选时，还必须由正文负责人主智能体读取`narrative-architecture-human-band-rubric.md`，先完成QUD段落问题链、情绪表达方式分布、结局驱动／主题过度决定、过度整改四项检查，再对五组叙事架构特征做人工量表复核。该量表不新增子智能体、不计算“人类总分”、允许`N_A`，普通偏离只登记`ADVISORY_DEVIATION`；只有跨至少两个独立组、覆盖至少三个场景／位置窗、主导全章且无法由章纲／题材／视角／科研／世界约束解释，并有实质文学损害证据时，才登记`EXTREME_DISTRIBUTIONAL_DEVIATION / NOT_QUALIFIED`并阻断。
- 在`CONTROLLED_PRODUCTION`处理完整装配稿、有界修订或补写稿时，先执行`production-workflow.md`的装配后卫生门；若发生补写、锚点插入或长度融合，再执行`production-workflow.md`的补写后文学质量验收。补写输入必须含NPA-17—20：反复述、反同义复写、反连续句式骨架复用和逐段删除反事实；不得把内部长度门或算术缺口写成外部创作目标。两项必须先于最终A/B报告，正文SHA变化后全部重做。跨章连续阅读重复不由本Skill单章脚本裁决，交`continuous-reading.md`。
- 论坛长帖、公众号、博客与中文长回答，读取 `human-forum-prose.md`；现实内容再读 `human-reality.md`。
- 短内容、口播、教程、剧本、对白或特殊格式，读取 `human-formats.md`。
- 初稿完成后才读取 `human-revision.md`；并读取 `modifier-function-audit.md`，逐项检查状语、补语是否真正改变时空、动作、程度、因果、视角、人物声口或后续状态。不得在第一稿前用详细审稿表压扁声音。
- 新写正文时，只把 `external-model-card.md` 的正向原则编译进当前结构化输入；不得把本审计手册、阈值、检测报告或词表交给正文作者。调用器由用户另行配置，本包不绑定外部模型。
- 已有正文需要改稿时，先冻结事实与结构，再做语义审计和有界改写。
- 用户只问检测原理或策略时，读取 `six-dimensions.md`。
- 用户要求检查或清理文本中的不可见Unicode控制字符，或最终正文已经冻结时，读取`unicode-layer-a.md`。Layer A只能在所有语义修订完成后执行；任何后续语义改写都会使旧清理结果失效。
- 用户要求“逆向类似检测器”“本地模拟打分”或比较替代评分器偏差时，读取`shadow-detector-scorer.md`并只运行`shadow_detector_scorer.py`的证据约束模式。必须排除错配／混母文样本，报告组留一交叉验证与均值基线；代理误差高时固定登记`SHADOW_SURROGATE_INSUFFICIENT`，不得把代理分数冒充真实检测器结果，但可把它作为并列审计线索，不得单独放行。
- 用户提供检测报告、要求比较检测前后版本、出现微小改动后分数反向或拟据检测结果改稿时，完整读取`detector-evidence-and-reverse-effect.md`。先在不看分数和高风险定位的条件下完成独立文学冷读，再核验提交输入、可见文本、报告字符和分段是否可比；单次报告不得直接触发正文改动。报告存在公开分段时，还须把分段文字边界映射到源稿UTF-8字节、场景和作者／轮次边界；没有完成这一步，不得选择局部修复范围。
- 用户明确要求以 AIGC 审计机制为重点，或同一章节出现“微小改动后检测值飙升／反向”时，追加读取`detector-mechanism-probes.md`并登记`AIGC_AUDIT_MODE=MECHANISM_FIRST`。先执行`PROBE_INPUT_IDENTITY_GATE`，报告实载文本与计划探针错标、未知或长度梯混入不同母文时，所属因果组固定阻断；不得以文件名代替输入身份。按 P0→P2 优先区分运行方差、格式／解析敏感性和分段敏感性；P4 才可能在独立文学理由成立时进入有界改写，P5 永不进入生产。探针不上传正文、不进入正文提示、不产生“通过／绕过”结论。
- 用户明确指出句式／句群对检测结果有显著影响，或要求在不改叙事的前提下调句时，追加读取`syntax-bounded-rephrase.md`并登记`SYNTAX_BOUNDED_REPHRASE_V1`。只在冻结的连续窗口内做合并、拆分、信息落点调整、解释延迟、对白—动作交替或具体落点修订；不得把句式调整变成固定句长、短句比例或句型配额。
- 用户提供 PDF、截图或红色／高风险片段标注时，另读 `ai-trace-audit.md`。红色只提高冷读优先级；先绑定检测材料、源稿 SHA 和 UTF-8 字节范围，再与同章非红色上下文对照。颜色、分数和片段数量不得直接触发改写，红色原文不得进入正文生成提示。
- 需要建立或审计网文层与现实文学局部调制的文风卡时，读取 `voice-style-contract.md` 与 `aigc-literary-dual-objective.md`；必须分开 `WEB_BASELINE`、`LITERARY_MODULATION` 与可选的 `WEB_DISTILLED_CONTRAST`，不写作者仿写指令，不使用句长、意象、幽默或钩子配额。
- 小说、故事、人物对白或第一人称叙事，读取 `fiction-workflow.md`。
- 需要解释本 Skill 与 `qoqu/anti-zhuque` 的关系、许可或能力边界时，读取 `source-notes.md`。
- 需要从一部或多部小说提炼可迁移技法、比较写法或建立来源证据链时，读取 `method-layer-distilled-novel-toolbox.md`；它只提供方法参考，不是事实源，也不替代本项目的审计、调用器和双审闸门。
- 小说正文需要检查入口牵引、关键场景推动、章末继续阅读理由、钩子疲劳或样本声线保护时，读取`distilled-novel-toolbox-writing-methods.md`；固定字数／高潮／爽点配额和检测绕过做法不适用。

先冻结事实与章末接口，再按场景写出事件冻结、认知上限和未决残留，检查认知流程复现、对白闭环、动作配对、物件过载、生活后效和结尾总回收；然后按内置 human-writing 规则清理翻案腔、模型黑话、解释尾巴、无功能漂亮句，以及删去后不损失任何有效信息的装饰性状语／补语，最后做六维自然度复核。结构与六维代理都不得推翻有效人物声音、必要认识论限定或专业准确性。

## AI_TRACE 冷读、证据绑定与红片段边界

检测报告必须在独立文学冷读之后读取。冷读记录至少绑定：源稿路径与 SHA-256、`PRIMARY_FINDING`、`FINDING_SCOPE`、`VOICE_PROTECTION`、`DETECTOR_INDEPENDENT_REASON`、处置动作和未决项。高等级检测证据还必须分别绑定报告 SHA、项目源稿 SHA、检测器实际提交文本 SHA、源稿到提交文本的归一化转换、分段映射 SHA 与两套 UTF-8 左闭右开字节范围。用户确认直接复制粘贴时，语义来源可确认一致，但平台压缩空行或删除末尾换行后仍是不同字节身份，不得合并SHA；验证器只证明记录身份与范围完整，不证明文学质量、作者身份或检测结果。

红色／高风险片段逐项建立 `RED_HIGHLIGHT_REVIEW`：

1. 完整通读后再查看颜色、分值和定位；
2. 将片段边界映射到源稿字节、场景和作者轮次，并与同章非红色片段作功能对照；
3. 先判断动作后唯一释义、对白逐题闭合、解释尾、背景节拍、物件过载或装配接缝等检测器无关机制；
4. 保护人物稳定声口、必要事实、知识状态、关系动作和场景后效；
5. 默认 `KEEP` 或 `REVIEW_FLAG`，只有独立文学理由、范围可锁定且有明确授权时才进入 `DELETE_TAIL` 或 `BOUNDED_REPHRASE`。

上项只描述通用审计。`CONTROLLED_PRODUCTION`自本规则生效后改用项目逐项处置门：每个机械命中都必须进入正文负责人整改台账，默认必须`FIXED`并在最终复跑消失。正文负责人若认为某项不应修改，不能单方`KEEP`，必须取得正文负责人主智能体与三个独立子智能体共四份研究报告，再由协调者签署并绑定四份报告SHA，登记`CONTROLLER_EXCEPTION_APPROVED`；科研相关机械命中还必须额外绑定领域审查者的`SCIENCE_RIGOR_OVERRIDE_SUPPORTED`报告。章纲层科研豁免与正文负责人单方保留都只适用于覆盖子智能体报告但无机械`finding_id`的项目，不能越过机械命中。普通`KEEP / REVIEW_FLAG`不构成项目闭合。

PDF、截图、检测分数、命中词表和红色原文始终留在证据层，不得进入蒸馏输入、正文提示或事实源。建议使用 `python scripts/validate_ai_trace_record.py <冷读记录.json>` 做机械身份检查；验证通过不等于“自然度改善”或“检测通过”。

## AIGC 审计机制优先（项目回归协议）

当用户要求“对抗 AIGC 审计”时，固定登记 `AIGC_AUDIT_MODE=MECHANISM_FIRST` 与 `OBJECTIVE_MODE=AIGC_LITERARY_DUAL`：检测器机制、可比报告和文学冷读共同决定改稿优先级。不得把它解释为伪造作者身份或普适保证；允许在证据支持的范围内针对检测器敏感叙事形状做有界修订。执行顺序、字段和探针解释见 [references/detector-mechanism-probes.md](detector-mechanism-probes.md) 与 [references/aigc-literary-dual-objective.md](aigc-literary-dual-objective.md)。

最低闭合要求：

1. 先做盲态文学冷读和本地结构统计，锁定 `PRIMARY_FINDING` 与 `VOICE_PROTECTION`，之后才读取报告分数／红段；
2. 在同一检测条件下优先建立 `P0_RAW_REPLAY`、`P1_FORMAT_NOOP`、`P2_SEGMENT_NOOP`和`P2A_PREFIX_HEADING_CONTROL`。先逐份核验计划文本与报告详情页实载文本身份，再用公开分段字符数和阈值机械重构总比例；重构成功也只说明可观察聚合规则。报告缺少提交字节、可见文本或分段映射时，最高只登记 `ORDERING_ONLY`；错标或混母文固定 `INVALID_INPUT_IDENTITY / BLOCKED_FOR_CAUSAL_INTERPRETATION`；
3. 只有 P0—P2 基本稳定、且独立文学理由锁定单一连续病灶，才可登记 `P4_LITERARY_ABLATION` 并进入既有 `BOUNDED_REVISION`。任何分布式声线、压缩导致的说明单一化或未闭合章纲功能，固定 `PRIMARY_FINDING_UNRESOLVED`；
4. 探针变体全部保持 `NOT_A_FACT_SOURCE / NOT_PRODUCTION_VISIBLE`。分数下降、红段消失或阈值穿越可以登记为 `AIGC_COMPATIBILITY_SIGNAL`，但不得单独写成文学改善；放行必须同时记录文学回归结果、检测证据等级和用户验收；
5. 同时改变标题与段落等两个因素的对角 A/B 不得拆分归因，须补齐正交`2×2`。任何句法／语义启发式在两个内容无关场景同方向复现前，只能登记`SINGLE_SCENE_SIGNAL`；在用户明确的双目标任务中，可以作为当前窗口的 `AIGC_COMPATIBILITY_TARGET`，但不能进入全局生成配额或自动改写规则；
6. 选定回归对象 作为固定回归样本，必须同时保存原稿、候选、实际提交文本、报告和探针的 SHA、字节／字符／句段统计与未知项。正式比较固定使用`DETECTOR_SUBMISSION_PROFILE=BODY_ONLY_UTF8_LF_V1`；若采用人工粘贴，另登记并机械复核`DETECTOR_SUBMISSION_NORMALIZATION`，不得把候选文件SHA冒充提交文本SHA。标题版只作前缀／分段影子探针。用户的检测验收只能单独登记 `USER_DETECTOR_ACCEPTANCE=PASS|PENDING|FAILED`，不得被 Skill 推断或替代。

公开分段既要复算按字符加权的连续分值，也要复算按公开阈值整段换档后的三档字符占比；两者不得混称“总分”。分段映射完成后，使用 `python scripts/check_segment_semantic_boundaries.py <submission.txt> <segments.json>` 对检测器实际提交文本标记段内句末、句中／对白中截断，并由V2字段另绑源稿身份与可执行归一化；ASCII直引号与中文弯引号都必须检查。该结果只解释解析敏感性，不授权调整标题、空行或排版追求有利分段。`SEMANTIC_REGISTER_BIAS_SUSPECTED`只能在同母文、单变量证据不足时作为审计假设，不能转成“改写成事务语体”等生成规则；缺失标点触发极高分的 M4 类现象固定登记`PUNCTUATION_PARSER_FALSE_POSITIVE_SUSPECTED`，不得反向利用。

完整批次先使用：`python scripts/validate_detector_probe_batch.py <probe-results.json> --strict`；公开分段数字的机械聚合使用：`python scripts/reconstruct_detector_aggregation.py <report-segments.json> --strict`。脚本 PASS 只说明登记身份、文件与公开数字自洽，不说明文学质量或检测通过。若本轮使用`scene-event-weaver`事件库，再以其`event_pattern_signature`做跨章只读重复检查；重复只登记`REVIEW_FLAG`，必须人工区分必要母题与无功能模板，不自动拒绝事件或触发正文改写。

## 受控生产 单章三工序

项目 受控生产模式新建或实质修订的完整候选，在送领域／连续性成稿复查前必须完成以下三项；三项都只针对当前单章和当前正文 SHA，不做跨章分数解释，也不引入新的外部模型路由。

1. **分段语义硬门**：固定同一提交剖面后，用 `check_segment_semantic_boundaries.py` 生成 `SEGMENT_BOUNDARY_SEMANTIC_CHECK_V2`。完整正文必须覆盖全 UTF-8 字节范围，段界不得落在句中、对白中或 UTF-8 字符中间；`result` 必须为 `PASS`，任何 `review_flag` 都阻断送审。段界问题是提交可比性门，不授权为了分数改正文或人为加标题。
2. **对白—动作握手**：报告 B 的每个场景都必须登记 `dialogue_action_handshake`。有对白时逐轮绑定说话者、当轮议程、知识边界、对白相邻的可见动作和动作后的状态变化；无对白时说明无对白理由。该检查由报告 B 完成，不新增外部模型、不单独生成或改写对白；它只要求对话之后存在可读的行动／状态承接，不要求每句话解释原因，也不把非科研生活段落改成严密问答闭环。
3. **单章检测结果分层记录**：若有外部检测报告，使用 `reconstruct_detector_aggregation.py` 分开记录连续加权层（逐段分值的加权均值）与阈值分桶层（人工／疑似／AI 字符占比），同时记录提交路径、SHA、字节数、段数和可比性。缺少外部报告时登记 `DETECTOR_EXTERNAL_EVIDENCE=NOT_AVAILABLE`，不得补造分数；不得把分桶变化写成文学质量或作者身份结论。

三项工序的结果都写入当前 `AI_TRACE_AUDIT` 或正文门证据。正文 SHA、提交剖面或候选内容变化后，分段审计、对白—动作审计和检测分层记录必须按新身份重做；历史报告只保留为历史证据。

## 分层文风与双稿流程

网文层负责读者契约、目标—阻力—选择—后果、信息释放、对白行动、局部回报和章末出口；现实文学负责有范围的局部质地调制；可按 [references/aigc-literary-dual-objective.md](aigc-literary-dual-objective.md) 启用 `WEB_DISTILLED_CONTRAST`，用人物立场差、生活琐事、答非所问或外部打断形成有后效的反差笑点。三者不得合并成单一“高级／自然”标签。每个调制必须有 `scope_window`、`function`、`disabled_when` 与 `do_not_import`，优先级低于事实、视角、人物知识、结构和项目硬规则，但与文学性共同承担 AIGC 适配目标。

同一 agent 双稿时，第一稿必须完整可读；随后只做一次完整结构化自审，分开记录 `KEEP_FUNCTIONS`、`REQUIRED_REPAIRS`、`AIGC_COMPATIBILITY_TARGETS`、`REGRESSION_GUARDS` 和 `UNRESOLVED`，再构造自洽的第二份输入并输出完整第二稿。第二稿输入可以引用已绑定的检测机制类别和用户验收目标，但不得塞入私有词表、逐句红段或伪装指令；不得用随机同义替换、故意错误、句长配额或无关生活事件制造所谓活人感。最终核验失败时停在安全节点，不自行串联第三稿。

## 项目蒸馏候选的额外转换门

项目蒸馏候选若要进入最终 `VOICE_STYLE` 卡，必须按 [references/controller-style-card-conversion.md](controller-style-card-conversion.md) 完成当前 SHA 重绑、三层来源登记、协调者 `ADOPTED / ADAPTED / REJECTED` 裁决和网文／现实文学指标选择；候选默认不得直接进入正文调用卡。

## 项目正文结构保护硬门（CONTROLLED_PRODUCTION，受控生产模式）

本节是项目生产合同，不是通用检测器策略。对 受控生产模式所有新建或实质修订的完整正文候选，先冻结同版章纲与完整候选SHA，再并行建立两个互不读取对方结论的独立子智能体：A输出`OUTLINE_EXPRESSION_COVERAGE_AUDIT_V2`，B输出`NARRATIVE_CLOSURE_AUDIT_V1`。两者绑定同一对象／章纲／正文，但`task_id/context_id`必须不同；任一源文件字节变化都会使两份报告同时失效。正文负责人送审前必须同时绑定两报告路径与真实SHA，完整合同与模板见[references/project-dual-subagent-review-gate.md](project-dual-subagent-review-gate.md)。

报告A必须得到`OUTLINE_EXPRESSION_COVERAGE=PASS`。缺少报告、覆盖为`PARTIAL|ABSENT|CONFLICTING`，或章纲入口、场景链、章末接口、关键选择／后果没有闭合时，状态只能是`BLOCKED_FOR_REWORK`；不得把它写成事实冲突，也不得把候选冒充已改善。报告B必须逐场完成七维审查：动作原因解释过满、观察／提问到推理／结论、对白逐项答完、自我纠错直达正确答案、UNKNOWN被盘成完整账目与计划、连续“设置—兑现—总结”的均匀完成度、外部打断及其真实残留。外部打断不得公式化添加事故。报告B发现的非科研风险若拆松不伤叙事，正文负责人必须修改；若会伤害且无机械`finding_id`，才可走单方有据保留；存在机械命中仍只可走四报告协调者例外，科研项再加领域审查者报告。

A／B报告闭合后、双送审前，正文负责人主智能体必须对同一章纲／正文SHA完成`NARRATIVE_ARCHITECTURE_HUMAN_BAND_RUBRIC_V1`。报告必须显式包含`QUD_PARAGRAPH_CHAIN`、`EMOTION_MODE_DISTRIBUTION`、`RESOLUTION_AGENCY_AND_THEMATIC_OVERDETERMINATION`与`HUMANIZER_OVERCORRECTION`，再使用五组分开的人工观察汇总全章分布；最近三章与卷级重复只提交`continuous-reading.md`处理，不在单章量表中越权裁决。不得把语料均值、命名互文、第四墙、倒叙、支线、地点数或对白比例变成配额。`REFERENCE_PASS`与`ADVISORY_DEVIATION`均允许继续原有项目门；只有五项极端条件全部成立的`EXTREME_DISTRIBUTIONAL_DEVIATION`才判正文不合格并阻断送审。量表报告必须绑定路径与真实SHA；正文或章纲变化后失效重做。完整口径和模板见[references/narrative-architecture-human-band-rubric.md](narrative-architecture-human-band-rubric.md)与`../assets/narrative-architecture-human-band-audit-v1.template.json`。

固定执行位置不得前移或后置：装配卫生流程与适用的补写文学验收流程 → 盲态文学冷读／AI_TRACE／机械命中闭合 → 最终A／B报告 → 本人工量表 → 最终正文门 → 领域／连续性双送审。不得把完整量表或“人类特征配方”装入首次正文生成提示；量表触发整改时只传递具体文学损害、保护项和合法最小范围。量表导致任何正文改字后，上述正文身份相关证据全部失效并从装配卫生流程起重做。

扩写或有界改写前必须同时保留原候选的入口、必需场景、人物行动链、章末出口和基线结构证据。不得从已经丢失场景、群像铺垫、生活后效或作者交接声线的压缩稿继续“补长度”；先回到合法的作者／返工门，或保持 `CANDIDATE_ONLY / NEXT_AUTHOR_HANDOFF`。

`AI_TRACE_AUDIT` 固定按以下顺序执行：先在不知道检测分数、红色片段和高风险定位的条件下完成全章文学冷读，再绑定基线／候选结构对照，最后读取外部检测证据。记录必须增加 `OBJECTIVE_MODE=AIGC_LITERARY_DUAL`、`AIGC_COMPATIBILITY_TARGET`、`DETECTOR_EVIDENCE_LEVEL`、`DETECTOR_TARGET_ALIGNMENT`、`LITERARY_REGRESSION` 与 `USER_DETECTOR_ACCEPTANCE`。检测证据可以在身份和可比性闭合后参与正文改写，但局部命中仍不能绕过事实、结构和声线保护。

出现 `COMPRESSION_INDUCED_EXPOSITIONAL_MONOCULTURE`、`DISTRIBUTED_VOICE` 或目标功能未闭合时，固定登记 `PRIMARY_FINDING_UNRESOLVED`；禁止用删句、随机同义替换、补无功能动作或单点润色声称自然度改善。只有单一连续区域、文学理由独立成立且用户已有明确有界授权时，才可进入 `BOUNDED_REGION_REAUTHOR`；否则保留原文并交下一合法作者门。详见 [references/project-structural-protection.md](project-structural-protection.md)。

项目正文不得以`PRIMARY_FINDING_UNRESOLVED`长期绕过机械提示。分布式问题仍须进入合法作者门并形成新候选；新候选复跑后，每个初始命中必须登记`FIXED / CONTROLLER_EXCEPTION_APPROVED`之一。`CONTROLLER_EXCEPTION_APPROVED`不是正文负责人单方判断：必须绑定正文负责人主智能体＋三个独立子智能体的四份报告路径／SHA，以及协调者签名且在实物中列明四个SHA的批准裁决；`science_involved=true`时裁决还必须绑定领域审查者报告SHA。固定报告A与报告B不计入这四份争议机械命中报告，也不能替代其中任何一份。完整合同见 [references/project-finding-disposition.md](project-finding-disposition.md)。

选定回归对象 是本项目的固定回归样本。任何 选定回归对象 重写候选必须先通过上述文学与结构门，再绑定同一检测器、同一提交格式、可比分段和报告 SHA 供用户验收；`LITERARY_REGRESSION=PASS` 与用户明确登记 `USER_DETECTOR_ACCEPTANCE=PASS` 是同等放行条件。外部报告的机制类别和验收目标可以进入返工卡的结构化字段，但私有分数、逐句词表和标题伪装不得进入正文提示；报告不具可比性时只能登记 `ORDERING_ONLY / USER_ACCEPTANCE_PENDING`，不能据猜测反复改稿。

## 新写时使用受约束非最优选择

当几个表达都准确时，不必总选最完整、最顺滑、最像范文的那个。优先选择符合说话者年龄、经历、关系距离、当前压力和注意顺序的表达。

允许人物说半句、改口、答偏一点、漏掉作者最想解释的部分。允许普通段落普通结束。允许叙述先看见眼前麻烦，再补背景。

以下内容始终取最准确解：事实、数字、时间、空间、因果、技术术语、医疗与安全信息、人物知识、物品持有和关系阶段。不要故意使用怪词、错字、病句或无法恢复的跳跃。

## 改稿时锁住正文身份

改动前列出不可改变项：

1. 事件、选择、场景顺序、因果和结尾接口。
2. 人物知道什么、与谁处在什么关系、能看见什么。
3. 时间、地点、物品、数字、专业语义和证据强度。
4. 已经成立的幽默、停顿、反复、意象和人物口吻。

改动若触及任一项，停止自然度清理，转回事实或结构审查。

## 执行六维审计

六维之前先做认知结构层与场景级审计：

报告B不得只提交“七维均已检查”或“本场闭合完整”。每个场景必须绑定`scene_evidence`八字段：`entry_state`、`immediate_task`、`resistance`、`visible_change`、`exit_state`、`next_action_dependency`、`unresolved_or_unknown`、`closure_level`；每个字段都要有正文位置或明确`NONE`理由。每个闭环风险必须绑定一个反事实条目，写明准确位置、保留功能、拆松形式、删除后损害和下一动作是否仍可理解。没有这些证据时，结果只能是`REVISION_REQUIRED`或`NOT_RELEASED`，不能用字段齐全代替闭合。

该证据合同升级会使缺少上述字段的历史报告失效；正文或章纲SHA不变也不能补写旧报告，必须用当前模板重新独立审查并重新绑定SHA。

1. 完整的“观察—枚举—排除—最低结论”原则上只预先允许于重点科研相关论述。其他场景命中严密逻辑闭环时，由独立报告B逐场给出证据，正文负责人再测试“拆松后是否损害叙事完整性”：不损害则必须按压缩、延迟、中断或行为化修改。若只存在A／B子智能体风险、没有机械`finding_id`，会损害时可由正文负责人单方有据保留；一旦存在机械命中，则须走四份独立报告＋协调者签名例外门，科研项再附领域审查者报告。命中本身不是章纲硬阻断，但两份独立报告及其SHA是送审前硬门。
2. 认识论限制语处理的是成簇和重复翻译，不是词本身；删后造成过度断言就撤销。
3. 对白可以准确但不必当场完整。允许合并回答、搁置、延迟纠正和“回头查证”，关键术语与证据等级仍取最准确解。
4. 动作应有身体、关系或生活功能，不必为每个论证节点伴奏。
5. 正文不必解释每个动作或事情的原因。只有省略会破坏关键因果、人物选择可理解性、知识进入或章末接口时才保留最短必要说明；普通动作与他人内心可以只留可见结果和可撤回推断。
6. 章末优先保住必要接口和一处有效余音，不同时总结所有主题、意象、证据与关系意义。
7. 每场核对事件冻结、认知上限和未决残留；残留来自人物没能看全、想全或当场结算，不是固定悬念钩子。
8. 关系对白核对双方即时议程和关系状态认知是否被作者强行同步；关键交接可完成，人物理解不必同时完成。
9. 生活动作核对其对注意、节奏、选择或后续状态的真实影响；纯质感可以存在，但不能成为全章唯一生活层。
10. 先标出全章`PRIMARY_FINDING`与范围，再决定单点动作。同一物件、想法、关系判断或结尾意义若跨三处以上反复承担同一功能，登记`DISTRIBUTED_VOICE / NEXT_AUTHOR_HANDOFF`，锁定该声线并停止同轮局部清洗；不得另挑弱相关单句冒充主病灶已经改善。
11. 比较叙事功能而不只比较字词。同一场景若多次以不同物件、动作或说话人重新完成“重置现场—再次尝试／说明—重新核验—局部收束”，登记`FUNCTIONAL_MICRO_LOOP`；逐次问它是否真的改变行动、风险、关系、知识或资源。没有新增后效的回合不能靠换词冒充新推进。
12. 任何`PATTERN_BOUNDED_REVISION`在改后冷读前必须把冻结基线与候选同时交给脚本比较：`python scripts/audit_prose.py <候选> --mode fiction --structure --baseline <基线> --target-finding-type functional_micro_loop_candidate`。目标代理数量未下降时固定登记`PRIMARY_FINDING_UNRESOLVED`；若候选同时缩短字符或段落，追加`COMPRESSION_INDUCED_EXPOSITIONAL_MONOCULTURE_RISK`，检查是否删掉生活纹理却保留说明骨架。代理数量下降也只写`TARGET_PROXY_REDUCED_REQUIRES_HUMAN_REVIEW`，不得机械宣称改善。
13. 对状语与补语执行`MODIFIER_FUNCTION_TEST`：删去后若时间、空间、动作方式／方向／结果／持续、必要程度、因果条件、视角证据、人物声口和后续状态均不变，该成分就是无功能装饰，必须删除；需要的信息应落到可观察动作或具体后效，不得换一组近义修饰继续装饰。方向、结果、数量、持续、证据强度及人物特有口吻所必需的成分必须保留。相邻同义修饰叠加属于高置信机械候选，最终必须按既有`finding_id`处置门闭合。完整判定见`modifier-function-audit.md`。
14. 六维与逐场审查完成后，以`NARRATIVE_ARCHITECTURE_HUMAN_BAND_RUBRIC_V1`先标注每段隐含问题及回答方式，统计主要情绪落点采用直接命名／身体化／行为／对白／环境映照中的何种方式，检查结局驱动和主题是否跨场重复翻译，并对基线／候选执行过度整改反查；再从主题过度决定、感官／心理表演同质化、结构过度顺滑、可选人类正向标记、时间／空间／话语压平五组做全章人工复核。没有互文、第四墙、倒叙、支线、多地点或高对白不算缺陷；普通或可解释偏离只作编辑提醒。只有跨组、跨场景、章级主导、无法由必要功能解释且造成文学损害的极端偏离才阻断。

章节分段生成时，先逐段核对硬事实，再把机械装配后的全文作为唯一审计对象检查接缝：删除下半章的重开场／前情复述，避免上半章伪章末，核对时间、位置、持有、知识、说话权和未完成动作是否连续。详细处置见`split-chapter-seam.md`；接缝修正只能是`BOUNDED_REPHRASE`或其中的`SYNTAX_BOUNDED_REPHRASE`子型，不得借机改写两半结构。

详细处置见 `cognitive-structure.md`和`scene-level-audit.md`。压缩、延迟、中断与行为化均登记为 `BOUNDED_REPHRASE` 子类型，不改变现有顶层动作枚举。

依次检查：

1. 用词是否总是安全、概括、像标准答案。
2. 句长、停顿和句法是否长时间同速同模。
3. 段落是否依赖模板过渡、完整论证和段尾点题。
4. 作者高频词、连接词和惯用隐喻是否跨人物复现。
5. 不同人物是否被统一润色成同一种声音。
6. 不同场景是否都被同一种精致、沉静或意味深长的声调覆盖。
7. 状语、补语删去后是否什么都没有改变；是否只在替动作加柔光、替气氛重复命名，或把相邻近义词叠成“精致感”。

先运行 `python scripts/post_assembly_text_hygiene.py <完整正文> --object-id <对象> --output <结果.json>`检查非相邻重复、引号体系、半角标点、内部标记与本轮旧词元，再运行 `python scripts/check_human_writing.py <文本路径>`和`python scripts/audit_prose.py <文本路径> --mode fiction --structure`获取表层、认知结构与部分场景级定位提醒；脚本只发现形状，不自动清理。若要验证冷读记录，再运行 `python scripts/validate_ai_trace_record.py <冷读记录.json>`。活动v3脚本额外定位相邻段落长重合、异常空白装配槽、回到文本时出现的未建立引文、叙述层否定证明簇、背景声与前景停顿重复对齐，以及对白／叙述共享句法签名。脚本仍抓不到物件功能、双方议程、真实生活后效、引文事实真伪和跨场闭合，必须继续人工执行`scene-level-audit.md`。

通用任务可继续把这些结果作为`review_flag`。项目受控生产模式必须分别在修改前后运行`check_human_writing.py --strict-house-style --json`和`audit_prose.py --mode fiction --structure`，保存四份JSON，并在处置台账中以路径／SHA绑定初始与最终两份house-style审计；随后用`python scripts/validate_project_finding_dispositions.py <初始审计.json> <最终审计.json> <处置台账.json>`取得`PASS`。验证器会把两类审计的`finding_id`合并核验。机械提示必须`FIXED`并在最终审计消失；任何残留都必须走四报告协调者例外，科研项再附领域审查者报告。不得以命中数量给正文打总分，但也不得遗漏任何命中。

### 句式有界调整

当句式成簇形状本身是本轮 AIGC 目标时，按 [references/syntax-bounded-rephrase.md](syntax-bounded-rephrase.md) 建立连续 UTF-8 窗口和 `SYNTAX_GUARDS`。允许合并相邻动作、在真实注意转移处分句、调整信息落点、延迟解释、交替对白与动作、把抽象收束落回既有具体后效；每轮只选一种主操作。候选必须证明语义等价、结构零增量、区外字节不变、文学回归不退化，并在同一提交剖面下完成用户检测验收。不得强制第三人称、全对白、长句链、短句比例或任何句式数值配额。

通用任务若章纲功能本身包含分类、定义、证据排除或规则语言，可建立`natural_prose_audit_exemptions_v1` JSON。项目最终复跑不得用该清单隐藏命中。重点科研的`OUTLINE_KEY_SCIENCE_ALLOWED`只处置章纲覆盖子智能体提出、但脚本没有产生`finding_id`的风险；若存在机械命中，仍须四报告协调者例外并额外绑定领域审查者报告。普通规则对白、日常解释、关系讨论和思想表达不属于科研例外。带`--baseline`的比较不得复用同一豁免清单，基线和候选必须分别审计。

## House-style 门的默认语义

`check_human_writing.py` 默认把冒号、破折号、模板路标和翻案句列为可解释的 `house-style` 提醒。`CONTROLLED_PRODUCTION`已明确启用严格逐项整改，因此项目受控生产模式固定加`--strict-house-style`；命中必须修复到复跑消失，不能只抄进记录。通用项目仍可保持默认非阻断语义。硬停词与黑话边界继续按脚本硬失败处理。

## 有界改写

每个可见文本改动先回答两个问题：它是否有独立的文学／结构功能，或是否命中已绑定且可比的 AIGC 机制目标；以及它是否直接处理本轮主病灶。两者都为否时不执行；只有 AIGC 目标而无文学功能时，必须登记 `AIGC_COMPATIBILITY_TARGETED_WITH_GUARDS` 并限制为最小连续范围，禁止逐词清洗。若已登记`NEXT_AUTHOR_HANDOFF`，不得用同轮次要单点改动生成“自然度修订”版本；只能真正进入现行作者门，或保持正文不变并标记`PRIMARY_FINDING_UNRESOLVED`。若独立冷读把病灶锁定在一个连续区域，检测分段与该区域及既有作者／轮次边界相互吻合，而且用户明确要求有界修正，可执行一次`BOUNDED_REGION_REAUTHOR`：以源稿SHA、精确UTF-8起止锚点和区域外锁定字节SHA限定作者级重写。它仍是作者级处理，不得拆成多处局部润色；锁定区域任何字节变化都使本轮失败关闭。

模式性有界修改不能只检查候选本身。必须比较基线与候选的主病灶代理、字符数、段落数和人工场景功能：若目标微循环仍在，而课堂噪声、生活动作、人物打断或物件后效被大量压缩，禁止以“更紧凑”放行；先判断这些被删内容是否原本承担外部节奏压力。只有目标功能序列确实被重排或关闭、受保护声口仍在、区外锁定通过，才可由人工冷读考虑`IMPROVED`。

- 优先删除动作后的重复解释和普通段落后的漂亮尾句。
- 删除没有信息增量的装饰性状语／补语；先做删除反事实，需要保留的信息再改写为具体动作、方向、结果、程度依据或后效，禁止只换近义词。
- 把跨人物复现的作者词还原为眼前动作、物件、口语反应或后果。
- 让节奏变化来自赶路、争执、犹豫、观察和任务压力，不来自数值配额。
- 保留人物合理的笨拙、误解、抢话、不完全回应和有功能反复。
- 保护人物偶发的自我拆台、偏心辩解和不够圆滑的声口；不能仅因它像“解释尾”就删除。
- “算账”“这笔账”“把账算清”等抽象隐喻应降频。场景真有价钱、预算、欠款、交易或账本时可保留本义。

禁止随机同义替换、故意错别字、强制句长差、固定段长、感官配额、主动被动句配额和为了“自然跳跃”打断因果。句式有界调整只按`syntax-bounded-rephrase.md`执行，并必须同时通过语义等价、结构零增量、文学回归和用户检测验收。

## 冷读与交付

改完后暂时忘掉规则，回答：

- 能否辨认谁在说，他此刻要做什么。
- 每段是否带来动作、信息、关系、风险或理解变化。
- 哪句话换一个模型或人物也能原样使用。
- 哪处不够漂亮，却恰好属于这个人物。
- 文章是否已经在更早一句结束。

若用户只要成稿，只交成稿。若用户要求审计，简要列出有证据的位置、处理动作和保留理由。不得声称“通过朱雀”“不可检测”或给出无真实检测依据的成功率。

项目审计交付还必须报告`NARRATIVE_ARCHITECTURE_RUBRIC_STATUS`、`QUD_CHAIN_STATUS`、`EMOTION_MODE_DISTRIBUTION`、`RESOLUTION_THEME_OVERDETERMINATION_STATUS`、`EXTREME_DEVIATION_GROUPS`和`HUMANIZER_OVERCORRECTION_ADVISORIES`。`ADVISORY_DEVIATION`不得写成不合格；`EXTREME_DISTRIBUTIONAL_DEVIATION`必须列明全部五项极端条件的正文证据，不能只写量表结论。

## 最终文本 Layer A

所有语义写作、作者级重修、有界改写与全文回归完成后，先冻结最终可见文本，再执行：

```bash
python scripts/unicode_layer_a.py inspect path/to/text.txt
python scripts/unicode_layer_a.py clean path/to/text.txt
```

clean默认写入新文件，不原地覆盖，并在输出中给出逐码点计数、移除总数和清理后复检。ZWJ、ZWNJ、variation selectors与emoji tag等可能承载语言或emoji语义的字符默认只报告并保留。若Layer A后发生任何语义改写，必须对新冻结全文重新inspect与clean。

Layer A只清理高置信不可见文本控制字符，不做Layer B统计重写，不处理C2PA、EXIF、PDF或图片元数据，不降低采样水印或AI率，也不证明人工写作。完整边界见`unicode-layer-a.md`。
