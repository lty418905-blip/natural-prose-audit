# Generic Finding Disposition

本文件适用于单 agent 的通用机械审计，不授予任何项目权限，也不替代事实、专业或用户批准。

## 处置字段

每个命中都建立独立记录：

```json
{
  "finding_id": "F-001",
  "source": "checker-name",
  "location": {"start": 0, "end": 0},
  "mechanism": "FUNCTIONAL_MICRO_LOOP",
  "literary_function": "",
  "protected_invariants": [],
  "action": "FIXED",
  "reason": "",
  "rerun_status": "PASS"
}
```

`action` 可为 `FIXED`、`BOUNDED_REPHRASE`、`KEEP`、`REVIEW_FLAG` 或 `NOT_RELEASED`。公开版机械放行只接受所有命中最终为 `FIXED` 或明确没有命中；`KEEP`、`REVIEW_FLAG`、未知项和缺少复跑证据都保持 `NOT_RELEASED`，不提供隐藏豁免。

## 决策顺序

1. 先核对命中是否真实映射到源文本，而不是来自错配文件、标题、空行或混母文探针。
2. 再判断它是否触及事实、因果、视角、人物知识、专业准确性、关系或结尾功能。
3. 能在单一连续窗口内语义等价修复时，执行最小改写并复跑。
4. 不能安全修复时停止交付，而不是通过随机换词、标点扰动、错别字或无功能事件掩盖命中。

### 叙事闭合证据

叙事闭合不是“每个动作都解释原因”。对每场必须保存`entry_state`、`immediate_task`、`resistance`、`visible_change`、`exit_state`、`next_action_dependency`、`unresolved_or_unknown`和`closure_level`。对每个闭环风险必须保存精确位置、保留功能、拆松形式、拆松后的叙事损害和下一动作可理解性。缺少任一项只能标记`NOT_RELEASED`。

机械检查器只报告形状；完整阅读决定文学取舍。单 agent 的两次读取不是独立审查证据。
