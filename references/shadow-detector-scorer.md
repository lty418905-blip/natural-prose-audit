# 影子检测评分器（证据约束）

适用范围：文学与证据方法可用于任何任务；文中“项目”“受控生产”“协调者”“正文负责人”和独立报告要求仅指显式启用的 CONTROLLED_PRODUCTION。普通单 Agent 模式保持 SELF_AUDIT_ONLY 与零命中放行，不伪造独立报告或签名。模式与完整执行顺序见 [production-workflow.md](production-workflow.md)。

当用户要求“逆向一个类似评分器”或希望用本地模型估计报告分值时，使用项目脚本 `scripts/shadow_detector_scorer.py`。它是透明的离线代理，不是朱雀私有算法的复原，也不判断作者身份，不保证通过或规避任何检测器。

## 使用边界

- 只读取已登记的探针文本与报告数据；不 OCR、不联网、不调用模型、不写正文。
- 先排除 `MISMATCH`、`MIXED_SOURCE`、双因素对角线和字符数不匹配记录，再校准。
- 必须同时报告训练误差、按探针组留一交叉验证误差和均值基线；不能只报训练拟合。
- 交叉验证误差高于可接受范围时，状态为 `SHADOW_SURROGATE_INSUFFICIENT`，不得进入正文门或生成提示。
- 影子模型的特征只用于解释已有报告的可观察差异，不得转化为句长配额、标点配方、视角配方或随机改写规则。

## 任意回归对象的校准命令

```text
python -B scripts/shadow_detector_scorer.py \
  --reports probe-results.json \
  --text-map probe-texts.json \
  --out shadow-calibration.json
```

运行依赖 Python 3 与 NumPy（其他脚本仅用标准库）。`probe-texts.json` 是 probe ID 到 `{ "path": "probe.txt", "sha256": "实际文件SHA", "group": "同母文或同因果组", "prefix_kind": null }` 的对象映射；相对路径相对于映射文件。实读字节核验，不要求指定段落数或固定文章。报告格式为 `{ "reports": [{ "probe_id": "probe-1", "reported_chars": 120, "segments": [{ "chars": 120, "score": 0.4 }], "input_identity": "MATCH", "comparability": "SAME_SOURCE" }] }`；数字只是格式示例，不是检测结果。所有分值须使用 0—1 量纲，先用探针批次验证器校验报告。

旧 `--source-v1/v2/v3` 三文件入口仍保留，适用于此前的固定标题探针包，不是新任务的默认输入；不能和 `--text-map` 混用。分组须按真实母文／因果组登记，不得为改善交叉验证而拆组。

校准输出必须保留：模型系数、特征标准化参数、排除清单、每个探针的观察值／预测值／偏差、组留一结果和基线结果。缺少完整组留一结果、MAE 不优于均值基线或 RMSE 变差时，脚本返回 `SHADOW_SURROGATE_INSUFFICIENT`；其余也只是代理结果，仍须按任务的容许误差人工判断。对单独文本使用 `--score-text` 时，输出标明 `SHADOW_PREDICTED_SCORE`，不能写成检测器分数。

## 解释门

- 训练 MAE 低、组留一 MAE 高：过拟合或样本身份不足，登记 `SHADOW_SURROGATE_INSUFFICIENT`。
- 影子模型只改善 MAE 但恶化 RMSE：它可能抓到中间分值排序，却不能预测阈值两端的极端片段；不得用于放行。
- 影子模型与报告方向相反：保留为反证，不通过加权或删样本修饰。
- 只有在新增、同源、跨场景报告后仍稳定，才可把某机制提升为 `REPLICATED_AUDIT_PRIORITY`；它仍是审计排序，不是写作规则。
