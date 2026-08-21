# 检测报告证据与反向效果处理

检测报告仍先在独立文学冷读之后读取，但在 `AIGC_LITERARY_DUAL` 模式下，报告是与文学审计并列的改稿证据。先写出主病灶、保护声口和范围，再查看报告是否提供可比、可复现的检测机制线索；禁止让检测器逐句替作者清洗，允许它参与连续机制区域和版本选择。

## 一、先固定检测对象

每份报告至少登记，并严格区分项目候选原件与检测器实际提交文本：

- `SOURCE_TEXT_PATH / SHA256 / BYTES`：项目候选原件；不得因用户复制粘贴而假定它与检测端字节相同。
- `SUBMITTED_INPUT_PATH / SHA256 / BYTES / FORMAT`：实际提交给检测器的文件或物化纯文本字节；无法取得时写`NOT_AVAILABLE`。
- `SOURCE_TO_SUBMISSION_TRANSFORM / NORMALIZATION_PROFILE`：标题剥离、空行压缩、换行归一化、末尾换行删除等逐项说明；未知写`UNKNOWN`。
- `VISIBLE_TEXT_SHA256`：提取可见正文，统一换行、引号等展示差异后的文本身份；归一化规则须明示。
- `REPORT_PATH / SHA256 / DETECTED_AT`。
- `REPORT_TOTAL_CHARS / LOCAL_TOTAL_CHARS / SEGMENT_COUNT`及逐段字符数和公开分值。
- `INPUT_COMPARABILITY=PASS|FAILED|UNRESOLVED`。

可见文本相同不等于提交字节、文件格式、解析链和检测条件相同。用户人工确认“直接复制粘贴”证明语义来源与候选一致，但不能抹去平台空行／尾换行归一化；若归一化后的字符合计与报告精确闭合，应绑定两个SHA和转换，而不是把报告错判为另一母文。报告字符合计与任何可重构提交均不符、前后提交格式不同、缺少旧输入或检测端版本未知时，只能登记`UNRESOLVED`，不得写“某句导致分数变化”。

若报告头部百分比能由公开分段数字算术重构，只可把重构式描述为“这份报告的可观察计分表现”，不得外推为检测器的私有算法。

## 二、证据等级

- `D0_NO_REPORT`：只做文学审计。
- `D1_SINGLE_RUN`：单次报告只能生成`DETECTOR_EXTERNAL_FLAG`；在用户明确要求双目标时，可作为候选改稿的初始目标，但必须限制为最小连续范围并在固定提交剖面下复核，不能单独触发放行或版本升级。
- `D2_REPEATED_SAME_INPUT`：同一提交字节、格式和操作路径重复运行；只有跨运行稳定落在同一文本区域的信号可辅助安排人工冷读优先级。
- `D3_CONTROLLED_AB`：A/B各自输入字节和唯一差分闭合，提交格式与操作路径一致，并有足够重复运行估计组内波动。即便如此，报告也不能替代文学判断或证明作者身份。

用户没有明确授权时，不自行上传未公开正文或反复调用第三方检测器。既有报告不足以达到D2/D3时，保留未知，不补猜服务器版本、分段原因或私有特征。

## 三、主病灶先于改句

独立冷读必须先填写：

- `PRIMARY_FINDING_ID / PRIMARY_MECHANISM`：本轮最影响人物声音与阅读节奏的机制。
- `FINDING_SCOPE=LOCAL_ISOLATED|DISTRIBUTED_VOICE|STRUCTURAL|UNKNOWN`。
- `VOICE_PROTECTION`：不够漂亮却属于人物的自嘲、偏心、停顿、误解、口头习惯和有效反复。
- `DETECTOR_INDEPENDENT_REASON`：假设没有任何检测报告，文学编辑是否仍会改；若没有独立文学理由，必须登记检测目标和护栏，不得扩大范围。
- `AIGC_COMPATIBILITY_TARGET`：已绑定的检测机制、提交剖面、证据等级和验收目标；没有则写`NONE`。
- `TARGET_ALIGNMENT`：实际改动是否直接处理主病灶或已绑定的 AIGC 机制目标；只处理次要问题时必须写`PRIMARY_FINDING_UNRESOLVED`。

若主病灶为`DISTRIBUTED_VOICE`、已登记`NEXT_AUTHOR_HANDOFF`，同轮立即锁定同一声线；检测报告若指向同一分布式机制，只能登记为并列 `AIGC_COMPATIBILITY_TARGET`，不能用弱相关单点替代作者级处理：

1. 不得挑选一个弱相关局部句作为替代目标。
2. 不得用若干局部删改拼成作者级重写。
3. 不得把事实／机械修正或次要单点修改命名为“自然度改善”或“检测适配完成”。
4. 只能按现行作者门槛真正交下一位获授权作者，或保持正文不变并登记`PRIMARY_FINDING_UNRESOLVED`。该标签本身不自动创造额外模型次数。

局部修改只有同时满足以下条件才可执行：范围确为`LOCAL_ISOLATED`；没有同声线分布式牵连；有独立文学理由，或有已绑定且可比的 AIGC 机制目标；删除或改写后无需连改；不损害`VOICE_PROTECTION`；与主病灶或检测目标直接对齐。

## 三A、分段边界必须映射到文本与作者轮次

报告公开分段时，先把每个分段定位到检测器实际提交文本，再通过绑定转换回映源稿；不得把提交偏移直接冒充源稿偏移。登记：

- `SEGMENT_TEXT_BOUNDARY`：分段实际从哪一句开始、到哪一句结束；若边界落在一行中间，不得只写行号。
- `SUBMISSION_SEGMENT_BYTE_RANGE`：基于已绑定提交文本SHA的UTF-8字节偏移。
- `SOURCE_SEGMENT_BYTE_RANGE`：映射回已绑定源稿SHA的UTF-8字节偏移；转换未知时写`NOT_AVAILABLE`。
- `SEGMENT_BOUNDARY_CLASS`：`DOCUMENT_EDGE|PARAGRAPH_OR_LINE_BOUNDARY|SENTENCE_WITHIN_PARAGRAPH_FLAG|MID_SENTENCE_FLAG|MID_DIALOGUE_FLAG`；段内句末和对白中截断都必须复核。
- `AUTHOR_ROUND_ALIGNMENT`：分段是否与Gemini、Opus、Fable、受控融合或人工校正的既有轮次边界重合；只能写可由生产证据确认的身份。
- `INDEPENDENT_FINDING_OVERLAP`：盲态主病灶与检测高风险段是`PASS / PARTIAL / FAIL / UNRESOLVED`。
- `LOCKED_LOW_RISK_REGION`：低风险段是否存在独立文学硬伤；若没有，默认不重写，只允许为接缝所必需的一处最小承接修正。

分段与作者轮次重合只说明“应重新检查此前选错修复范围的可能”，不能证明某个模型、某句话或某种私有特征导致分数。只有盲态冷读独立识别出同一机制、用户明确授权修正，而且范围可被精确锁定时，分段证据才可用于选择作者级审阅区域。

连续区域内同一机制跨三处以上，仍属于`DISTRIBUTED_VOICE`。它不能改名为局部清洗；可在下列条件全部满足时登记一次`BOUNDED_REGION_REAUTHOR`：

1. 源稿路径与SHA固定，区域起止使用精确UTF-8字节锚点；
2. 区域外至少一侧以原始字节SHA锁定，边界落在句中时以完整字节串而非行号为准；
3. 事件、选择、场景顺序、人物知识、关系阶段、时间、地点、物品与章末接口全部冻结；
4. 修改目标是重建该连续区域的叙述注意顺序、对话议程和意义延迟，不是逐个替换命中词；
5. 只进行一次区域级作者处理，完成后机械验证锁定区域逐字节不变；
6. 若接缝需要改变锁定区第二处以上，或重写需要新增事件／知识／关系承诺，立即失败关闭并退回结构流程。

`BOUNDED_REGION_REAUTHOR`的结论只能来自改后冷读与边界核验；不得写成“朱雀PASS”或保证分数下降。用户未授权重新检测时，不自行上传正文。

若独立冷读发现的是同一个`FUNCTIONAL_MICRO_LOOP`在两个相邻、可分别锁定的区域复现，且用户明确要求一次有界修改，可登记`PATTERN_BOUNDED_REVISION`范围标签。它不替代现有动作枚举，也不降低`DISTRIBUTED_VOICE`证据等级。必须同时满足：

1. 两区均有精确文本／UTF-8锚点，区外字节可机械锁定；
2. 两区共享同一叙事功能序列，而非仅共享高风险分数或词语；
3. 每区分别列出不可删除的递进功能和人物声口；
4. 只压缩同功能回合，不重排场景、不改变事实、关系、知识或章末接口；
5. 修改后若出现第三个未冻结区域也必须联动，范围立即失败并退回`NEXT_AUTHOR_HANDOFF`。

检测分段只能辅助核对已由冷读识别的两个区域，不能创造该标签。版本结论仍依据文学冷读与边界核验，不依据分数升降。

## 四、反向效果

检测百分比在微小改动后大幅升降时：

1. 先核对源稿字节、提交字节、二者转换、格式、报告字符合计、分段数量和阈值穿越。
2. 把“文本变化”“输入解析变化”“重新分段”“阈值翻转”“检测端未知变化”分开登记。
3. 只报告现有证据能确认的部分；无法区分的原因统一写`UNKNOWN`。
4. 不因分数反向立刻回滚，也不继续追加删句；先记录`AIGC_COMPATIBILITY_SIGNAL`，重新核对目标是否仍与文学功能一致。
5. 重新审查原改动是否有独立文学理由、是否命中主病灶、是否伤害人物声口。

若改稿以压缩为主，额外执行`COMPRESSION_INDUCED_EXPOSITIONAL_MONOCULTURE`检查：

1. 分别统计基线与候选的字符、段落和目标结构代理数量；
2. 区分被删的是说明骨架，还是打断说明骨架的生活动作、人物噪声、等待、失败后效与外部压力；
3. 目标`FUNCTIONAL_MICRO_LOOP`数量未下降而字符／段落减少时，固定登记`PRIMARY_FINDING_UNRESOLVED`与`COMPRESSION_INDUCED_EXPOSITIONAL_MONOCULTURE_RISK`；
4. 不因候选更短、词更少或某些次级提示消失就推断主病灶改善；
5. 需要恢复内容时只恢复会改变下一动作、压力、关系、知识或节奏的功能性纹理，不恢复纯结构标点。

脚本比较命令：

```text
python scripts/audit_prose.py <候选> --mode fiction --structure --baseline <基线> --target-finding-type functional_micro_loop_candidate
```

比较结果仍是人工冷读的防错门，不是文学评分或检测器模拟器。

跨运行同一位置持续高风险且独立冷读也发现同一机制时，可提升该区域的作者级审阅优先级；仍不得逐句按分数清洗。

## 五、版本结论

每轮只允许下列结论：

- `NATURALNESS_EDITORIAL_OUTCOME=IMPROVED`：实际处理了主病灶，且冷读确认人物声音和场景功能更好；它不是检测器 PASS。
- `AIGC_COMPATIBILITY_OUTCOME=IMPROVED`：在固定提交剖面和可比证据下，检测适配目标改善；它不是文学 PASS，也不是作者身份结论。
- `AIGC_LITERARY_OUTCOME=RELEASE_READY`：`NATURALNESS_EDITORIAL_OUTCOME=IMPROVED` 与 `AIGC_COMPATIBILITY_OUTCOME=IMPROVED` 均成立，并通过项目事实／结构／用户放行门。
- `...=LOCAL_CHANGE_ONLY`：只完成一个合法单点，未处理分布式主病灶。
- `...=UNCHANGED`：审计后选择保留正文。
- `...=PRIMARY_FINDING_UNRESOLVED`：主病灶需要作者级处理或证据不足。

版本名和交接摘要必须与该结论一致。专业／settingPASS只证明各自职责范围，不得作为自然度改善证据。

## 六、最小记录模板

```text
SOURCE_TEXT=<path + sha>
SOURCE_TEXT_BYTES=<bytes>
SUBMITTED_INPUT=<path + sha + bytes or NOT_AVAILABLE>
SOURCE_TO_SUBMISSION_TRANSFORM=<explicit transform or UNKNOWN>
SOURCE_SUBMISSION_IDENTITY_STATUS=<enum>
BLIND_LITERARY_AUDIT_COMPLETED=true|false
PRIMARY_FINDING_ID=<id>
PRIMARY_MECHANISM=<mechanism>
FINDING_SCOPE=<enum>
VOICE_PROTECTION=<short list>
DETECTOR_EVIDENCE_LEVEL=D0|D1|D2|D3
INPUT_COMPARABILITY=PASS|FAILED|UNRESOLVED
DETECTOR_INDEPENDENT_REASON=<reason or NONE>
TARGET_ALIGNMENT=PASS|FAIL|NOT_APPLICABLE
ACTION=<existing action enum>
SEGMENT_TEXT_BOUNDARY=<exact excerpt boundary or NOT_AVAILABLE>
SUBMISSION_SEGMENT_BYTE_RANGE=<utf8 range or NOT_AVAILABLE>
SOURCE_SEGMENT_BYTE_RANGE=<utf8 range or NOT_AVAILABLE>
SEGMENT_BOUNDARY_CLASS=<enum or NOT_AVAILABLE>
AUTHOR_ROUND_ALIGNMENT=<evidence-bound result>
INDEPENDENT_FINDING_OVERLAP=PASS|PARTIAL|FAIL|UNRESOLVED
LOCKED_LOW_RISK_REGION=<path/range/sha or NONE>
NATURALNESS_EDITORIAL_OUTCOME=<enum>
UNKNOWN_CAUSES=<explicit unknowns>
```

