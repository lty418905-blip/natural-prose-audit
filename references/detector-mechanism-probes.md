# AIGC 检测机制探针协议（MECHANISM_FIRST）

本文件用于在用户明确要求比较 AIGC 检测结果、或同一章出现检测值反向波动时，区分三类问题：文本本身的叙事／声线病灶、提交格式与解析链敏感性、以及检测器运行方差。在 `AIGC_LITERARY_DUAL` 模式下，已闭合的机制证据可以成为与文学性并列的改稿目标；它仍不是检测器私有算法说明、作者身份证明或无条件“降低 AI 率”的写作配方。

## 1. 目标、边界和身份

- 审计模式固定登记 `AIGC_AUDIT_MODE=MECHANISM_FIRST`。
- 所有探针都绑定 `SOURCE_SHA256`、`PROBE_SHA256`、转换说明、可见文本不变量、报告路径／SHA 和检测条件；缺一项只能登记 `UNRESOLVED`。
- 探针默认只读、离线计划，不自动上传正文、不调用第三方检测器、不把探针变体送入正文模型提示。
- 探针结果首先回答“这次报告是否对输入形状敏感”；在证据身份和提交剖面闭合后，可额外生成结构化 `AIGC_COMPATIBILITY_TARGET`，不回答作者身份，不生成普适“通过检测”“不可检测”或成功率。
- 生产正文与探针副本分离。探针副本永远是 `NOT_A_FACT_SOURCE / NOT_PRODUCTION_VISIBLE`；任何语义变化都不能以“探针”名义进入终稿。

## 2. 探针级别与固定矩阵

按以下顺序建立，只有前一层证据可比时才进入下一层：

| ID | 探针 | 允许的变化 | 要回答的问题 | 生产资格 |
|---|---|---|---|---|
| P0 | `RAW_REPLAY` | 同一正文、同一字节、同一格式、同一路径重复提交 | 检测器自身是否有运行方差 | 只作证据，不改稿 |
| P1 | `FORMAT_NOOP` | 仅换行、BOM 或容器格式；可见字符逐字不变 | 分数变化是否来自解析／格式 | 影子审计 |
| P2 | `SEGMENT_NOOP` | 可见文本不变，只改变窗口、分页或分段边界 | 红段是否由短片段／边界造成 | 影子审计 |
| P2A | `PREFIX_HEADING_CONTROL` | 正文主体逐字不变，只在开头加入／移除固定标题；必须成对保存 | 标题是否重置首段及后续分段 | 影子审计，不能把标题当规避手段 |
| P3 | `PUNCTUATION_CONTROL` | 仅在用户授权下变更等价引号／标点字形；语义不变 | 标点归一化是否改变报告 | 影子审计，不可直接入稿 |
| P4 | `LITERARY_ABLATION` | 只移除一个已由盲态冷读确认的解释尾、同功能回合或装配接缝；双目标模式下可同时绑定一个可比检测机制或 `SYNTAX_BOUNDED_REPHRASE` 窗口 | 文学主病灶与 AIGC 高风险形状是否重合 | 通过事实／结构／声线护栏后可进入有界改写 |
| P5 | `STRUCTURE_PERTURBATION` | 场景顺序、句法重排或新增动作 | 仅作研究对照 | 永不直接生产 |

P1—P3 是“语义不变量”控制，不是正文改写；P4 才可能成为正文处理候选，且仍须通过项目既有 `BOUNDED_REVISION`、事实门、结构门、声线门和用户验收门。P5 不得用于制造“活人感”或追逐分数。

### 2.1 批次输入身份硬门

探针名、PDF 文件名和操作者记忆都不能证明实际提交了计划文本。读取结果前必须逐份登记：

- `PLANNED_SOURCE_ID / PLANNED_VISIBLE_TEXT_SHA256`；
- 报告详情页实际可见文本的人工转录或可复核摘要及 `OBSERVED_VISIBLE_TEXT_SHA256`；
- `PROBE_INPUT_IDENTITY=MATCH|MISMATCH|MIXED_SOURCE|UNKNOWN`；
- 成对或梯度探针的 `PAIR_OR_LADDER_SOURCE_ID`。

任一成员为 `MISMATCH|UNKNOWN`，该成员不得参与因果解释；同一对照组或长度梯包含两个母文时，整组固定为 `INVALID_INPUT_IDENTITY / BLOCKED_FOR_CAUSAL_INTERPRETATION`。允许保留单份报告的描述性分值，但不得拿错标 A 与正确 B 计算因素效应。报告实载文本与另一探针重复时，登记 `DUPLICATE_INPUT_UNDER_DIFFERENT_LABEL`，不能把它算作新的独立样本。

同时改变两个因素的 A/B 只能登记 `CONFOUNDED_INTERACTION_ORDERING`。若需拆分标题、段落、容器或其他主效应，必须补齐正交 `2×2`；不得从对角线两点反推两个单独权重。

若报告公开逐段字符数、逐段分值与三档阈值，先机械重构总百分比，并登记 `AGGREGATION_RECONSTRUCTED=PASS|FAILED|UNRESOLVED`。某一检测器若满足下式，只能写成该批报告的可观察聚合规则，不能外推到其他检测器：

```text
HUMAN_SHARE = sum(segment_chars where score < 0.5) / report_total_chars
SUSPECTED_SHARE = sum(segment_chars where 0.5 <= score < 0.99) / report_total_chars
AI_SHARE = sum(segment_chars where score >= 0.99) / report_total_chars
```

若报告还声明连续的“加权平均 AIGC 值”，须把它与三档占比分开复算：

```text
WEIGHTED_SCORE = sum(segment_chars * segment_score) / report_total_chars
```

登记 `OBSERVED_WEIGHTED_SCORE`、三档占比和各自的 declared/computed 差值；不得用加权平均替代桶占比，也不得把某段跨越 0.99 后的整段换档误写成连续总分同幅变化。报告只显示四位小数时保留舍入不确定性。

这意味着整段跨阈值时，整段字符都会换档；总百分比不是逐段分值的简单平均。审计必须同时报告分段长度、分段边界和阈值类别，不能只报告总百分比。

机械重构命令：

```text
python scripts/reconstruct_detector_aggregation.py <report-segments.json> --strict
```

脚本只读取已人工登记的公开分段数字并复算加权总分与三档比例，不解析 PDF、不联网、不修改正文，也不模拟检测器。

若报告分段已经映射到检测器**实际接收的提交文本** UTF-8 左闭右开字节范围，可追加运行：

```text
python scripts/check_segment_semantic_boundaries.py <submission.txt> <segment-ranges.json>
```

输入使用`SEGMENT_BOUNDARY_SEMANTIC_CHECK_V2`语义，固定声明`boundary_unit=UTF8_BYTES`和`coverage_mode=FULL_DOCUMENT|PARTIAL_WINDOW`，每段提供`utf8_start/utf8_end`；有公开片段字数时同时提供`reported_chars`，脚本会要求它与该提交片段的解码字符数完全一致。分类固定为`DOCUMENT_EDGE / PARAGRAPH_OR_LINE_BOUNDARY / SENTENCE_WITHIN_PARAGRAPH_FLAG / MID_SENTENCE_FLAG / MID_DIALOGUE_FLAG`。句末虽完整但落在原段内部时不得再写成“干净段界”；ASCII直引号和中文弯引号中的截断都登记`MID_DIALOGUE_FLAG`。

原稿文件身份与提交文本身份必须分开绑定。直接复制粘贴不保证检测端保留空行和末尾换行；用户确认“逐字复制”时，也可能存在平台归一化。此时不能把报告判为另一母文，而应在`segment-ranges.json`中同时登记：

```json
{
  "source_path": "D:/absolute/original.md",
  "source_sha256": "<原稿SHA>",
  "source_bytes": 0,
  "submission_sha256": "<实际提交文本SHA>",
  "submission_bytes": 0,
  "normalization_transform": "<人类可读的转换说明>",
  "normalization_profile": "COLLAPSE_DOUBLE_LF_ONCE_TRIM_TRAILING_LF_UTF8",
  "boundary_unit": "UTF8_BYTES",
  "coverage_mode": "FULL_DOCUMENT",
  "segments": []
}
```

只有列出的已知`normalization_profile`会被脚本以绑定源文件重新执行并与提交字节逐字节核验；只有自由文本说明时固定为`DECLARED_NOT_MECHANICALLY_VERIFIED`。原稿／提交不同即使转换复核PASS，也保留身份复核提示，因为它只能证明当前转换重构，不证明检测平台的私有解析链。中途切句是检测器解析证据，不是正文缺陷，也不授权为了取得有利分段而修改生产提交。

完整批次身份与分段登记可先运行：

```text
python scripts/validate_detector_probe_batch.py <probe-results.json> --strict
```

该脚本复核报告文件 SHA／字节（文件可读时）、探针 ID 唯一性、片段字符合计、公开阈值分类及身份阻断项。`BLOCKED_FOR_CAUSAL_INTERPRETATION` 表示批次中存在错标、混母文或不可比较组，不等于检测器或正文失败。

## 3. 每个探针必须记录的字段

```yaml
probe_id: P2
probe_revision: DETECTOR_MECHANISM_PROBE_V1
source_path: <absolute path>
source_sha256: <sha256>
source_bytes: <bytes>
submission_path: <actual submitted text path or NOT_AVAILABLE>
submission_sha256: <actual submitted text sha256 or NOT_AVAILABLE>
submission_bytes: <bytes or UNKNOWN>
normalization_transform: <NONE or explicit source-to-submission transform>
normalization_profile: <known executable profile or NOT_AVAILABLE>
source_submission_identity_status: BYTE_IDENTICAL | SOURCE_SUBMISSION_DIFFERENT_DECLARED_TRANSFORM | SOURCE_SUBMISSION_DIFFERENT_UNEXPLAINED
probe_path: <shadow path or NOT_CREATED>
probe_sha256: <sha256 or NOT_CREATED>
transformation: <机械变换的完整说明>
visible_text_invariant: PASS|FAILED|UNKNOWN
semantic_invariant: PASS|FAILED|UNKNOWN
format_invariant: PASS|FAILED|UNKNOWN
detector_report_path: <path or NOT_AVAILABLE>
detector_report_sha256: <sha256 or NOT_AVAILABLE>
detected_at: <utc or NOT_AVAILABLE>
segment_count: <number or UNKNOWN>
reported_chars: <number or UNKNOWN>
score_delta: <observed only or NOT_COMPARABLE>
evidence_status: D0_NO_REPORT|D1_SINGLE_RUN|D2_REPEATED_SAME_INPUT|D3_CONTROLLED_AB|ORDERING_ONLY
interpretation: <one of the fixed classes below>
production_visible: false
```

## 4. 结果解释，不反推私有算法

- `FORMAT_OR_PARSER_SENSITIVITY`：P1 在可见文本不变时显著波动；只能说明提交格式／解析链值得复核。
- `SEGMENTATION_SENSITIVITY`：P2 只改边界却改变红段集中度；短红段不得直接成为删改范围。
- `PREFIX_SEGMENTATION_SENSITIVITY`：P2A 的正文主体逐字相同，但标题改变首段边界或后续分段；固定后续提交格式，禁止把加标题当成正文整改。
- `RUN_VARIANCE`：P0 同一输入重复结果不稳定；不得用一次升降判断整改成败。
- `LITERARY_MECHANISM_SUPPORTED`：P0—P3 基本稳定，且盲态冷读与 P4 独立命中同一叙事病灶；可登记并列文学处置与 `AIGC_COMPATIBILITY_TARGET`，但不能把单次变化外推为检测器私有因果。
- `SEMANTIC_REGISTER_BIAS_SUSPECTED`：多个内容不同样本呈现文学／氛围语域偏高、事务／设备语域偏低的聚类，但尚未由同源、等长、正交对照排除词汇、长度与分段混淆。它只用于解释假阳性和安排复核，不得把小说改写成事务说明文。
- `ORDERING_ONLY`：缺少提交字节、可见文本或分段映射；只允许排列人工复核优先级。
- `UNRESOLVED`：输入、报告、格式、分段或运行条件有任一不可比；保持正文不变。

“显著”不得由 Skill 自行硬编码成通用百分比。只能报告同一检测器、同一路径、同一格式下的可观察变化，并把阈值穿越、报告字符合计、分段数和版本未知分别登记。

语义／句法探针在单一场景产生大幅变化时登记 `SINGLE_SCENE_SIGNAL`，不能外推为普适规律；在用户明确的双目标任务中，它仍可作为该场景的候选 `AIGC_COMPATIBILITY_TARGET`，但不得复制成句式配额。相同方向至少在两个内容无关场景复现，并排除报告字符、分段、标题和阈值跨越混淆后，才可升级为 `REPLICATED_AUDIT_PRIORITY`，并进入受控文风卡的机制字段。方向相反或一组为空结果时必须保留，不得选择性丢弃。

跨语域聚类不能仅凭不同母文的高低分升级为 `REPLICATED_AUDIT_PRIORITY`。至少需要逐对绑定可见文本 SHA、提交剖面、字符数、分段和受控变量；否则保持 `SEMANTIC_REGISTER_BIAS_SUSPECTED / AUDIT_ONLY`。同一批次如出现 P4 与 S4 一类方向相反的“自然化”结果，固定禁止形成全局句式规则。

## 5. 固定回归样本的最小执行顺序

1. 先对原始基线和候选做盲态文学冷读、`audit_prose.py` 和结构统计；不先看红色分数。
2. 先通过 `PROBE_INPUT_IDENTITY_GATE`，再分别绑定原稿字节与检测器实际提交字节、二者转换、格式、报告字符合计和分段数；原稿与提交因已验证的平台归一化而不同不等于错标，但不得合并成一个SHA。任何关键项缺失都登记 `ORDERING_ONLY`，真正错标或混母文则阻断所属因果组。
3. 优先做 P0—P2A。若一次同时改变标题和段落，先补齐正交 `2×2`；只有 P0—P2A 可比且主病灶仍能由文学理由独立成立，才允许规划 P4。
4. 若候选同时出现句段碎片化、程序化自检回合、说明尾和群像／生活纹理压缩，登记 `COMPRESSION_INDUCED_EXPOSITIONAL_MONOCULTURE` 或 `DISTRIBUTED_VOICE`，不得用单个红段清洗冒充整改。
5. 只有 `LITERARY_REGRESSION=PASS` 且用户在同一检测条件下明确登记 `USER_DETECTOR_ACCEPTANCE=PASS`，候选才可进入用户指定的后续流程；该状态不是 Skill 对其他检测器的保证。

后续回归固定使用用户命名的 `DETECTOR_SUBMISSION_PROFILE`：源稿只含无标题正文主体、UTF-8、LF 换行、无 BOM；标题版只可作为影子对照。若用户实际使用粘贴文本或其他容器，必须另登记`SUBMISSION_SHA256`及`DETECTOR_SUBMISSION_NORMALIZATION`，不能假设原文件字节原样进入检测器。只要归一化转换与报告字符数机械闭合，可在同一报告内建立源稿到提交文本的映射；跨轮比较仍须保持同一提交方式和转换。

固定提交剖面的目的在于可比性，不是挑选更有利的分段。任何只改变标题、空行或段落边界的低分结果只能留在 P1/P2/P2A 影子证据层，不得作为生产正文或“合规降分”版本。

M4 缺标点／半角句点探针曾出现 `0.9999` 的解析假阳性。未来遇到无标点连排或异常标点文本，先登记 `PUNCTUATION_PARSER_FALSE_POSITIVE_SUSPECTED` 并恢复规范提交输入；禁止把剥离标点、混用标点或制造格式异常当成正文改写策略。

探针批次证据必须由使用者提供明确路径与 SHA；本包不内置任何项目证据。探针只把“分段／前缀／阈值交互”作为机械防错依据；句群节奏和视角先登记单场景信号。标点异常和混母文长度梯不得写入生产文风卡。

## 6. 禁止事项

- 不把检测器名称、分数、阈值、红色原文或探针变体写入正文生成提示。
- 不做随机同义替换、故意错别字、固定句长／段长、随机跳跃、无功能生活事件、标点噪声或跨模型拼接以“对抗”检测。
- 不因单次红段、单次总分或某个词命中直接逐句清洗；若用户已明确启用双目标，可把它登记为最小连续候选，但不得跳过文学／事实／结构门。
- 不把探针的分数下降写成“人类化成功”，也不把分数上升写成“文本必然更像 AI”；只能分别登记 `AIGC_COMPATIBILITY_OUTCOME` 与文学回归结果。

