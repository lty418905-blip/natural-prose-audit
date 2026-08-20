# AI 痕迹与检测报告审计

本流程用于用户提供 AIGC／AI 生成检测报告，或要求“降低 AI 味”“更像人”时。目标是修复真实的文学、结构和声线问题，不是优化检测器分数。

## 证据等级

- `NO_REPORT`：只有用户口述或截图摘要，不能定位。
- `ORDERING_ONLY`：报告身份可核，但缺少逐段到源稿字节映射或同稿波动基线；只可排列冷读顺序。
- `MAPPED_SINGLE_RUN`：逐段文字、分值和源稿字节已绑定，但只有一次检测；可帮助定位，不能证明因果。
- `MAPPED_REPEATABILITY_BOUNDED`：同一冻结稿重复检测并记录波动；仍只能作为外部信号，不能证明作者身份或整改效果。

任何等级都不得生成“通过检测”“不可检测”或目标百分比。检测器名称、阈值、分段分值和逆向猜测只留在审计链，绝不能进入正文生成提示。

## 红色／高风险标注片段优先审计

检测报告中的红色片段（通常代表报告自己的高疑似区间）可以提高冷读优先级，但不能直接等同于文学缺陷。对每个标注片段先建立 `RED_HIGHLIGHT_REVIEW`：

```yaml
segment_id: ""
detector_source:
  path: ""
  sha256: ""
  page_or_locator: ""
  reported_value: "ORDERING_ONLY"
manuscript_source:
  path: ""
  sha256: ""
  utf8_byte_range: {unit: "UTF8_BYTE", start: 0, end: 0}
context_window: "标注片段前后各取足以判断场景功能的上下文"
cold_read_finding:
  class: "DISTRIBUTED_VOICE | EXPLANATION | DIALOGUE_CLOSURE | ASSEMBLY_SEAM | UNKNOWN"
  mechanism: ""
  detector_independent_reason: ""
  action: "REVIEW_FLAG | KEEP | BOUNDED_REPHRASE"
voice_protection: []
```

审计顺序固定为：完整通读 → 红色片段及上下文冷读 → 与同章非红色片段作功能对照 → 再查看报告数值。重点检查动作后的唯一释义、精确问答链、抽象意图替人物说尽、段落出口过度整齐、分段接缝和物件功能过载。红色片段若只是短片段、段界截断、教学／规则说明或必要事实陈述，应保留并登记 `KEEP`。不得按红色片段数量、颜色面积或阈值做改写配额，也不得把红色原文直接交给正文模型；第二稿只能接收抽象功能、问题机制、保护项和绑定身份。

PDF、截图和可视化报告属于检测证据层，不属于方法蒸馏输入或事实源。若报告没有可复核的页码／分段到源稿 UTF-8 字节映射，标注片段的证据等级最高仍是 `ORDERING_ONLY`。

## 冷读顺序门

读取检测分数和高风险位置前，先完整阅读正文并建立 `NATURAL_PROSE_AI_TRACE_RECORD_V1`。记录至少绑定（字段名与验证器一致，不能改写成另一套扁平格式）：

```json
{
  "schema": "NATURAL_PROSE_AI_TRACE_RECORD_V1",
  "mode": "PRE_REVISION",
  "source": {"path": "稿件.md", "sha256": "..."},
  "detector_evidence_status": "ORDERING_ONLY",
  "cold_read_locked_before_detector": true,
  "primary_finding": {
    "id": "PF-01",
    "class": "DISTRIBUTED_VOICE",
    "scope": "MULTI_SCENE",
    "evidence_ranges": [{"unit": "UTF8_BYTE", "start": 120, "end": 460}],
    "voice_protection": ["人物稳定声口", "必要事实说明"],
    "action": "REVIEW_FLAG"
  },
  "revision_authorization": {
    "status": "NOT_AUTHORIZED",
    "target_finding_id": "PF-01",
    "allowed_ranges": []
  },
  "detector_independent_reason": "即使不看检测报告，也会依据动作、关系和段落功能作出该判断。",
  "unresolved": []
}
```

`source.path` 可以是相对记录文件的路径；`source.sha256` 必须由验证器重新读取源稿实算。范围统一使用左闭右开的 UTF-8 字节区间，`end` 不得越过源稿实读字节数。实际主病灶必须有至少一个字节范围；确实没有主病灶时，使用 `id=NONE_WITH_REASON / class=NONE / scope=NONE / action=NO_CHANGE` 并提供 `reason`，不要伪造命中。`primary_finding.voice_protection` 至少保留一项，`revision_authorization.target_finding_id` 必须与主病灶 ID 完全一致。`NOT_AUTHORIZED` 必须保持空范围；`AUTHORIZED` 必须给出非空范围，而且每个范围都要包含在主病灶证据范围内。记录验证通过只代表记录、顺序声明和源稿身份完整，不代表文学质量、作者身份或检测结果。

### 高等级检测证据绑定

`MAPPED_SINGLE_RUN` 和 `MAPPED_REPEATABILITY_BOUNDED` 不能只写枚举值，必须绑定真实文件：

```json
{
  "detector_evidence": {
    "runs": [
      {
        "source_sha256": "与 source.sha256 相同",
        "report": {"path": "run-1-report.pdf", "sha256": "..."}
      }
    ],
    "segment_map": {"path": "segment-map.json", "sha256": "..."}
  }
}
```

`MAPPED_SINGLE_RUN` 至少绑定一份报告；`MAPPED_REPEATABILITY_BOUNDED` 至少绑定两份路径和 SHA 均不同的报告。段落映射文件固定使用：

```json
{
  "schema": "NATURAL_PROSE_DETECTOR_SEGMENT_MAP_V1",
  "source_sha256": "...",
  "segments": [
    {
      "source_range": {"unit": "UTF8_BYTE", "start": 0, "end": 120},
      "report_locator": "page:1/segment:1"
    }
  ]
}
```

验证器会实读报告和映射文件、复算 SHA，并验证映射不越过冻结源稿。它不解释检测器分值，也不证明重复运行统计可靠。`ORDERING_ONLY` 可以绑定已知报告，但不要求映射；即使材料足以升级，保守登记较低等级也合法。

`cold_read_locked_before_detector=true` 是流程声明，不是时间旅行证明；它必须在读取报告前落盘并绑定源稿 SHA。若顺序已经倒置，就如实写 `false`，不能补签。

没有 `PRIMARY_FINDING` 时只可审计。后续修改未命中其范围或机制时，只能登记 `LOCAL_CHANGE_ONLY / PRIMARY_FINDING_UNRESOLVED`。主病灶为跨场景声线、装配结构或完整叙事引擎时，不得用多处词级替换冒充闭合。

## 冷读项目

除了词语和句长，至少检查：

- 对象层的分类／规则是否被复制到全部叙述层；
- 动作以后是否总有一句替读者锁定唯一意义；
- 同一认知增量是否在多个段尾重复结算；
- 对白是否长期形成“问—准确回答—确认收到”的逐题闭合；
- 背景事件是否只为前景停顿打拍子，从不改变下一动作；
- 不同人物、章节和文体是否共享同一套总结句法；
- 装配边界是否重开场、复述前情、重复动作或丢失指涉；
- 物件是否在短窗口承担过多象征、推进、关系与收束功能；
- 压缩是否只删掉生活纹理，留下更密的解释骨架。

这些项目只产生 `REVIEW_FLAG`。教学、审讯、规则说明、科研限制和人物稳定声口都可能形成合法反例，必须保留保护项。

## 跨文档比较

跨章比较用于找流水线复现，不用于找“禁词”。只比较功能：解释尾、结算节拍、对话闭合、句法签名、场景退出方式和跨人物作者词。候选必须经人工区分：

- `CHARACTER_VOICE_KEEP`：人物稳定声口；
- `AUTHOR_VOICE_KEEP`：作品有意统一的叙述声口；
- `DISTRIBUTED_VOICE_REVIEW`：不同人物／场景被同一解释程序覆盖；
- `UNKNOWN`：证据不足。

不得把比较产生的词表或短语表发给正文模型要求替换。

## 允许的整改

- 删除动作后的重复解释，前提是因果仍清楚；
- 把抽象结算还给人物可见动作、选择、代价或关系后果；
- 修复装配接缝、重复开场和指涉错位；
- 在授权范围内恢复被压缩掉的必要生活后效；
- 让对白完成当前人物任务，而不是替作者逐题交卷。

这些都必须有检测器无关的文学理由。不得为了“更像人”故意错字、病句、随机跳跃、固定句长、随机同义替换、无关生活事件或配额化打断。

## 停止条件

- 检测分数成为主要修订目标；
- 保护项、事实、因果、人物知识、关系、专业语义或结尾功能受损；
- 分布式问题被多点局部清洗冒充解决；
- 脚本命中未经人工复核直接触发正文修改；
- 可观察参数被翻译成“每 N 段一次”的配额；
- 来源 SHA、装配边界或冷读记录发生漂移。
