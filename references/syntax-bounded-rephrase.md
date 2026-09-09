# 句式有界调整协议（SYNTAX_BOUNDED_REPHRASE_V1）

适用范围：文学与证据方法可用于任何任务；文中“项目”“受控生产”“协调者”“正文负责人”和独立报告要求仅指显式启用的 CONTROLLED_PRODUCTION。普通单 Agent 模式保持 SELF_AUDIT_ONLY 与零命中放行，不伪造独立报告或签名。模式与完整执行顺序见 [production-workflow.md](production-workflow.md)。

本协议用于在句式或句群形状被可比 AIGC 报告反复指向时，进行不改变原本叙事的句法调整。它是审计阶段的局部表达工具，不是全章统一润色器，也不规定固定句长、短句比例或句型配额。

## 1. 可冻结的目标

在事实、因果、视角、人物知识、关系阶段、时间／地点、物品持有、科研语义和章末接口全部冻结后，才可登记：

```yaml
syntax_revision:
  schema: SYNTAX_BOUNDED_REPHRASE_V1
  objective_mode: AIGC_LITERARY_DUAL | LITERARY_ONLY
  source_path: ""
  source_sha256: ""
  scope:
    scene: ""
    utf8_start: 0
    utf8_end: 0
    outside_bytes_sha256: ""
  target_mechanism:
    id: ""
    evidence_level: D1_SINGLE_RUN | D2_REPEATED_SAME_INPUT | D3_CONTROLLED_AB | ORDERING_ONLY
    alignment: PASS | PARTIAL | UNKNOWN
  pattern_observed:
    repeated_opening: false
    uniform_action_per_sentence: false
    repeated_cognitive_tail: false
    same_clause_landing: false
    dialogue_narration_signature: false
    other: ""
  operation: MERGE_ADJACENT_ACTIONS | SPLIT_AT_ATTENTION_SHIFT | CLAUSE_ORDER_REBALANCE | DEFER_EXPLANATION | DIALOGUE_ACTION_INTERLEAVE | CONCRETE_LANDING | REMOVE_REPEATED_SYNTACTIC_TAIL
  invariants: ["事件", "选择", "因果", "知识边界", "章末接口"]
  stop_conditions: []
```

`pattern_observed` 必须描述一个连续窗口内的成簇形状，而不是单个高分词或一条红线。单场景探针可以作为该窗口的候选目标；只有跨场景复现并排除输入／分段混淆，才可提升为可复用的文风卡机制。

## 2. 允许的句法操作

- `MERGE_ADJACENT_ACTIONS`：合并同一注意链中没有独立后果的相邻动作，保留真正的动作节点和人物议程。
- `SPLIT_AT_ATTENTION_SHIFT`：在视线、说话权、关系压力或行动目标真实改变处拆句，不为制造短句而拆。
- `CLAUSE_ORDER_REBALANCE`：调整已知信息与新信息的落点，不改变时间、因果和知识先后。
- `DEFER_EXPLANATION`：把不必当场结算的解释移到动作后效、对白回看或下一注意窗口；若会造成过度断言，撤销。
- `DIALOGUE_ACTION_INTERLEAVE`：在人物实际抢话、停顿、递物或做事处交替对白和动作，不强行提高对白比例。
- `CONCRETE_LANDING`：把抽象收束落回已经存在的物件、身体动作、关系回应或下一步任务。
- `REMOVE_REPEATED_SYNTACTIC_TAIL`：只删除重复承担同一功能的句尾；不得删除必要证据、限定语或人物口吻。

每个窗口默认只选一种主操作；若需要第二种操作，必须说明它是同一处接缝的必要承接，而不是扩张改写范围。

## 3. 不得做的事

- 不强制第三人称、全对白、程序化“第一步／第二步”或长句逗号链；它们只能在原有叙事任务本来需要时出现。
- 不设“每 N 句一个短句”“每段至少一次打断”“句长变异系数达到 X”等数值配额。
- 不用故意错字、病句、标点噪声、随机同义替换、无关生活事件或标题／版式伪装改变检测结果。
- 不把句法重排偷偷升级为新增事件、改换人物选择、重排场景、改变信息进入时间或改写章末接口。

## 4. 审计与验收

1. 先完成盲态全章冷读，记录 `PRIMARY_FINDING`、`VOICE_PROTECTION` 和 `LITERARY_REGRESSION` 基线。
2. 再绑定报告／探针的实际文本、SHA、分段和提交剖面，填写 `target_mechanism`；身份不闭合时只能 `ORDERING_ONLY`。
3. 在冻结窗口内生成候选，机械核对区外字节、正文 SHA、事实／结构差分和句式目标代理；候选不能只靠分数变化验收。
4. 冷读候选，确认人物声音、动作后效、对白议程和章末余音未退化；再按同一提交剖面完成用户检测验收。
5. 记录：

```yaml
syntax_outcome:
  semantic_equivalence: PASS | FAILED
  structure_delta: NONE | REVIEW_REQUIRED
  literary_regression: PASS | FAILED | PENDING
  aigc_compatibility_outcome: IMPROVED | UNCHANGED | FAILED | NOT_COMPARABLE
  action: KEEP | REVIEW_FLAG | SYNTAX_BOUNDED_REPHRASE | NEXT_AUTHOR_HANDOFF
```

任何硬状态或边界字段发生变化，立即关闭本协议，回到章纲／事实审查；任何分布式声线不能靠多个句式窗口拼成“局部修复”。
