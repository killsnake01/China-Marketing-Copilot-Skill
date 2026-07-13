# 风险账本

用于把评论区压力、负面雷达和路线切换前的风险判断整理成统一因果链。适用于上市决策、正式物料审核、上线后战情复盘和用户要求“为什么会翻车”“最危险点在哪里”。

## 字段定义

| 字段 | 填写要求 |
|------|----------|
| risk_id | `R001` 这类稳定编号 |
| priority | P0/P1/P2/P3，P0 代表高损害且需立即处理 |
| evidence_anchor | 输入里的原句、截图位置或用户提供材料 |
| fact_status | `known`、`inferred` 或 `needs_verification` |
| trigger | 风险触发材料或动作 |
| actor | 最可能入场者：参数党、KOL、媒体、客服、竞品、普通用户等 |
| compressed_narrative | 最可能被压缩成的短标题、梗或质疑句式 |
| platform_path | 扩散路径：评论区、高赞截图、KOL二创、搜索词、客服话术等 |
| business_impact | 对路线、转化、信任、退货、渠道或上市节奏的影响 |
| early_signal | 可监测先兆 |
| route_impact | 继续、缩窄、切换或暂停 |
| recommended_action | 最小可逆动作 |
| side_effect | 动作副作用 |
| disconfirming_evidence | 什么证据会降低当前判断 |
| confidence | 高/中/低 |

## 输出模板

```markdown
## 风险账本

| ID | 优先级 | 证据锚点 | 事实状态 | 压缩叙事 | 扩散路径 | 业务影响 | 路线影响 | 建议动作 |
|----|--------|----------|----------|----------|----------|----------|----------|----------|
| R001 | P1 | {原句/位置} | known/inferred/needs_verification | {短标题或质疑} | {平台路径} | {影响} | 继续/缩窄/切换/暂停 | {动作} |

反证条件:
- R001: {什么证据会降低判断}
```

## 使用纪律

- P0/P1 风险必须有证据锚点、传播路径、业务影响、早期信号和动作。
- `inferred` 和 `needs_verification` 不能改写成已知事实。
- P0 风险必须进入上市总控台的第一风险或硬阻断说明。
- P1 及以上风险必须映射到负面雷达和路线切换剧本。
- 缺少传播路径或业务影响时，降级为待验证风险，不直接扩大判断。

## 机器维护

- 样本：`docs/evals/risk-ledger-samples.json`
- 脚本：`scripts/evaluate_risk_ledger.py --check`
