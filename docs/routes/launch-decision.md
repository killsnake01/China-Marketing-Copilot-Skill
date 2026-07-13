# 上市决策路由

## 触发

用户要求新品上市策略、传播怎么打、预算取舍、上市前7天、能不能直接执行、管理层汇报或 go/no-go。

## 读取顺序

1. `docs/data-index.md`
2. 对应 `knowledge-base/{category}/_index.md`
3. `docs/templates/strategy-decision-system.md`
4. `docs/templates/message-house.md`
5. `docs/templates/risk-assessment.md`
6. 用户要求完整上市决策包时读取 `docs/templates/launch-decision-package.md`
7. 用户要求上线许可或正式执行时读取 `docs/templates/execution-readiness-gate.md`
8. 用户要求路线评分或解释取舍时读取 `docs/templates/route-scorecard.md`
9. 用户要求完整风险因果链时读取 `docs/templates/risk-ledger.md`
10. 用户要求路线切换预案时读取 `docs/templates/route-switch-playbook.md`
11. 用户要求机器验收时读取 `docs/templates/decision-consistency-gate.md` 和 `schemas/launch-decision.schema.json`
12. 用户要求管理层汇报时读取 `docs/templates/executive-decision-memo.md`
13. 用户要求统一决策卡时读取 `assets/launch-decision-card.md`

## 默认输出

- 上市任务简报 归一化：产品与品类、上市时间、商业目标、目标人群、预算级别、已有证据、主要竞品、计划平台、风险与禁用边界、缺失信息。
- 推荐路线、备选路线、弃用路线。
- 核心主张、三条证据柱、证据缺口和禁用表达。
- 参数党、普通用户、解构找茬三类评论压力测试。
- 负面雷达：信号、叙事阶段、触发阈值、负责人角色和路线影响。
- 结论、硬阻断项、72小时动作、7天跟进和自检。

## 按需高级输出

- 完整上市决策包：封面、状态、面向对象、负责人、目录和待决事项。
- 管理层汇报：上市总控台和管理层决策纪要。
- 路线比较：统一维度路线评分卡。
- 完整风险管理：风险账本和路线切换剧本。
- 机器验收：结构化决策单和决策一致性门。

## 纪律

- 推荐路线依赖的关键事实未核验时，结论最多写 `调整后执行`。
- 生成完整上市决策单时先输出上市决策包封面；包状态必须和裁决、硬阻断、待补事实一致。
- 存在硬阻断项时，结论写 `暂停重做`，并列解除条件。
- 不把创意数量当策略质量，优先给取舍依据。
- 上市任务简报 缺失信息只能写 `[待补]`，不能把推断内容写成用户已提供事实。
- 生成风险账本时，P0/P1风险同步到负面雷达和路线切换剧本。
- 生成管理层决策纪要时，裁决、推荐路线和置信度与总控台、结构化决策单一致。
- 生成路线评分卡时，总分满足推荐高于备选、备选高于弃用；推荐路线证据强度或风险可控低于3分时不能直接执行。
