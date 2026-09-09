# 项目机械命中逐项处置协议

适用范围：文学与证据方法可用于任何任务；文中“项目”“受控生产”“协调者”“正文负责人”和独立报告要求仅指显式启用的 CONTROLLED_PRODUCTION。普通单 Agent 模式保持 SELF_AUDIT_ONLY 与零命中放行，不伪造独立报告或签名。模式与完整执行顺序见 [production-workflow.md](production-workflow.md)。

本协议只适用于显式启用 CONTROLLED_PRODUCTION 的任务。它把`natural-prose-audit`与`check_human_writing`的机械提示转换为正文负责人必须执行的整改输入；机械命中不证明作者身份，也不替代文学冷读、章纲覆盖、科研或世界观审查。

## 1. 双独立子智能体前置审查

在受控生产模式下，每个完整正文候选在送审前必须并行建立两个不同、互不读取对方报告的子智能体：A只做章纲表达覆盖，B只做叙事闭环逐场审查。两者绑定同一章纲／正文SHA，但使用不同`task_id/context_id`；正文或章纲SHA变化后两份报告同时失效。正文负责人送审时必须同时绑定两份报告路径及真实SHA。完整schema、七维清单与模板见`project-dual-subagent-review-gate.md`。

报告B及所有章纲规划／审查子智能体和独立章纲咨询必须检查：

- 是否把一个非科研场景写成连续“提问—完整回答—复述—结论”；
- 是否要求教师、同伴与叙述者轮流把同一标准说清；
- 是否让每次尝试都完整执行“观察—解释—核验—收束”；
- 是否预设每个动作、停顿、物件变化和人物反应都必须由正文紧跟一句原因或唯一意义；
- 是否在段尾、场尾和章尾同时结清主题、证据、关系和接口。

报告B必须额外覆盖动作原因解释过满、自我纠错直达正确答案、`UNKNOWN`被盘成完整账目与计划、连续“设置—兑现—总结”的均匀完成度，以及外部打断是否具有真实后效而非公式化事故。逐场输出`LOGIC_CLOSURE_RISK=CLEAR|KEY_SCIENCE_ALLOWED|NON_SCIENCE_REVIEW_REQUIRED`及位置、功能和应保留的必要信息。`KEY_SCIENCE_ALLOWED`必须绑定章纲内重点科研论述、科研来源路径／SHA和本场科学功能。`NON_SCIENCE_REVIEW_REQUIRED`不是章纲硬阻断，不要求协调者为此改事件或结构；它作为风险卡交正文负责人，在正文候选上做反事实检查。

## 2. 正文负责人反事实检查

每个`NON_SCIENCE_REVIEW_REQUIRED`或机械识别出的逻辑闭环都必须回答：

1. 如果压缩、延迟、中断、行为化或取消一次复述，读者是否仍能理解谁做了什么、为什么发生、行动怎样传到下一拍及章末接口是什么？
2. 拆松是否会删除不可替代的因果、人物选择、知识进入、关系动作或必要任务说明？
3. 是否存在更小的安全修改，既保留叙事完整性又避免严密闭环？

正文没有义务解释每个动作和事情的原因。只有省略后会使关键因果、人物选择、知识进入或章末接口不可理解时，才保留最短必要原因。普通动作、生活反应、他人内心和非关键停顿可以只呈现第一人称可见结果，让读者形成可撤回推断；不得为了“闭合”替不可见人物补唯一动机。

不伤害叙事完整性时，固定`FIXED`并修改；修改后同一命中必须在最终审计消失。若风险只来自章纲表达覆盖子智能体，且同一文本范围没有机械`finding_id`，正文负责人主智能体可单方登记`OUTLINE_RISK_RETAIN_NARRATIVE_INTEGRITY`，但须绑定反事实改法、具体损害、保护功能和更小修法评估。一旦存在机械`finding_id`，该单方通道立即失效，必须启动第4节。

## 3. 重点科研例外

只有章纲表达覆盖子智能体提出风险、同一范围没有机械`finding_id`，且章纲明确承担关键方法、证据、机制、结果或安全边界的科研论述，才可登记`OUTLINE_KEY_SCIENCE_ALLOWED`。必须逐项绑定：

```yaml
scope: KEY_SCIENCE_NO_MECHANICAL_HIT
coverage_report_path: ""
coverage_report_sha256: ""
outline_source_path: ""
outline_source_sha256: ""
source_location: "章纲场景／科研依据位置"
scientific_function: "为何必须严密且完整"
```

普通课堂规则、生活讨论、关系解释、思想主题、人物自证和作者总结不属于科研例外。该通道只处理没有机械命中的覆盖报告项；若脚本产生`finding_id`，科研内容也须执行第4节，并额外取得领域审查者报告。

## 4. 四份独立报告＋协调者签名例外

任何机械命中若最终仍保留，必须取得：

1. 正文负责人主智能体一份独立报告；
2. 三个不同正文负责人子智能体各一份独立报告；
3. 协调者对四份报告独立裁决，并形成签名裁决实物。

四份报告分别绑定同一`finding_id`、独立`task_id`、报告路径／SHA，并分别评价：移除该命中后的叙事逻辑、文学不可替代性、反事实正文状态及`IRREPLACEABLE|REPLACEABLE|MIXED`结论。子智能体不得读取彼此报告后再写自己的报告。

送审前固定的报告A／报告B不计入这四份例外报告，也不能替代正文负责人主智能体或三个争议命中子智能体中的任何一份；它们的任务目的和证据schema不同。

协调者裁决必须写入`SIGNED_BY=CONTROLLER / DECISION=APPROVE_EXCEPTION`，绑定同一`finding_id`及四个报告SHA。正文负责人主报告或三个子报告的多数票不自动放行；没有协调者签名裁决时一律继续修改或保持`BLOCKED`。

若`science_involved=true`，还必须取得领域审查者独立出具的`SCIENCE_RIGOR_OVERRIDE_SUPPORTED`报告，说明删除／拆松该命中会怎样损害科学准确性、证据强度或安全边界。协调者裁决须同时绑定该科研报告SHA。科学严谨性高于机械消项，但科研报告不代替四份叙事／文学报告，也不自行批准最终例外。

处置台账使用`CONTROLLER_EXCEPTION_APPROVED`，schema升级为`natural_prose_project_finding_dispositions_v2`。本例外可以覆盖确有不可替代文学功能的机械命中；科研命中还须附领域审查者报告。`OUTLINE_KEY_SCIENCE_ALLOWED`和正文负责人单方保留都只能处理没有机械`finding_id`的覆盖子智能体报告项。

## 5. 其他机械提示

除四报告协调者例外外，`audit_prose.py`及`check_human_writing.py --strict-house-style`的所有提示都必须作为改稿依据，修改并复跑到消失。不得用`KEEP / REVIEW_FLAG / STYLE_FLAG / PRIMARY_FINDING_UNRESOLVED`或章纲科研豁免越过机械命中。

修改仍须服从事实、因果、人物知识、视角、关系阶段、科研语义、时间／空间、持有和章末接口。若单点无法安全修复，进入现行合法作者门；权限不足不等于提示已闭合。

## 6. 机械闭合

1. 保存初始`audit_prose.py --mode fiction --structure`输出与初始`check_human_writing.py --strict-house-style --json`输出。
2. 正文负责人建立逐项处置台账并形成候选。
3. 对候选重新运行`check_human_writing.py --strict-house-style --json`及完整`audit_prose.py`，保存最终两份JSON。
4. 冻结最终候选SHA后，并行取得报告A章纲表达覆盖与报告B叙事闭环；任一报告要求修改时，修改后两份均须对新SHA重做。
5. 在送审绑定中同时登记两份报告的路径、SHA、不同`task_id/context_id`及闭合状态。
6. 运行：

```bash
python scripts/validate_project_finding_dispositions.py initial-audit.json final-audit.json dispositions.json
```

处置台账schema为`natural_prose_project_finding_dispositions_v2`，绑定初始／最终`audit_prose`真实SHA，并以`initial_house_style_audit / final_house_style_audit`绑定两份严格house-style JSON的路径与真实SHA。`FIXED`项必须在最终审计中消失；最终仍存在的finding只能是合法的`CONTROLLER_EXCEPTION_APPROVED`。验证器会实读两类审计、四份报告、适用时的领域审查者报告与协调者裁决并核对SHA；`PASS`只证明逐项处置闭合，不证明外部检测通过、事实正确或专业双审PASS。
