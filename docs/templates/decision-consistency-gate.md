# 决策一致性门

用于检查上市总控台、结构化决策单和自检字段之间有没有互相打架。适用于深度版上市决策单、管理层汇报、上线闸门和正式发布前校验。

## 必查关系

| 字段关系 | 通过标准 |
|----------|----------|
| 决策包状态 vs 决策结论 | `decision_package.package_status` 与 `decision` 对齐：直接执行对应可评审，暂停重做对应暂停评审 |
| 总控台裁决 vs 决策结论 | `control_summary.verdict` 与 `decision` 完全一致 |
| 决策纪要裁决 vs 决策结论 | `executive_memo.verdict` 与 `decision` 完全一致 |
| 总控台置信度 vs 自检置信度 | `control_summary.confidence` 与 `self_check.confidence` 完全一致 |
| 决策纪要置信度 vs 总控台置信度 | `executive_memo.confidence` 与 `control_summary.confidence` 完全一致 |
| 总控台推荐路线 vs 路线裁决 | `control_summary.recommended_route` 与推荐路线名一致 |
| 决策纪要推荐路线 vs 路线裁决 | `executive_memo.recommended_route` 与推荐路线名一致 |
| 路线评分卡 vs 路线裁决 | 推荐、备选、弃用三行路线名和 `route_verdict` 完全一致，且推荐总分高于备选，备选高于弃用 |
| 硬阻断 vs 裁决 | 存在硬阻断时，结论必须降为 `暂停重做` |
| 直接执行 vs 缺口 | `直接执行` 不能同时有待验证事实、推测、待补项或高风险 |
| 自检计数 vs 列表 | 已核、待验证、推测、硬阻断计数必须和对应列表一致 |
| 负面雷达 vs 切换剧本 | 雷达里出现缩窄、切换或暂停，切换剧本必须有对应动作 |

## 输出要求

```text
决策一致性门

| 检查项 | 结论 | 问题 | 修正动作 |
|--------|------|------|----------|
| 包状态一致 | 通过/不通过 | {问题} | {动作} |
| 裁决一致 | 通过/不通过 | {问题} | {动作} |
| 硬阻断一致 | 通过/不通过 | {问题} | {动作} |
| 计数一致 | 通过/不通过 | {问题} | {动作} |
| 纪要一致 | 通过/不通过 | {问题} | {动作} |
| 评分一致 | 通过/不通过 | {问题} | {动作} |
| 雷达-剧本一致 | 通过/不通过 | {问题} | {动作} |
```

## 机器校验

运行：

```bash
python3 -B scripts/validate_decision_output.py --input decision.json
python3 -B scripts/validate_decision_output.py --check
```
