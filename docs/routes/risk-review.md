# 风险与负面预警路由

## 触发

用户要求会不会翻车、负面苗头、评论区压力测试、KOL争议、价格背刺、AI空话、上线前风险或危机预案。

## 读取顺序

1. `docs/templates/risk-assessment.md`
2. `docs/ecosystem/negative-early-warning.md`
3. `docs/references/comment-personas.md`
4. `docs/ecosystem/industry-memes.md`
5. 涉及节日、价格、AI硬件或KOL争议时读 `docs/ecosystem/market-signals-2026.md`
6. 需要上线判断时读 `docs/templates/execution-readiness-gate.md`
7. 用户提供结构化评论批次时运行 `scripts/analyze_signal_batch.py`

## 默认输出

- 总体判定和主要风险。
- 1-3条代表性模拟评论。
- 替代表达或立即动作。
- 用户要求完整预警时，增加负面信号类型、叙事阶段、严重度、触发阈值和负责人角色。
- 用户要求上市路线判断时，增加暂停/切换阈值和对推荐路线的影响。
- 有结构化批次时补充独立账号、平台、速度、重复噪声、权威放大和业务影响证据。

## 纪律

- 不把批评自动归为黑粉。
- 价值观、隐私、安全、健康和绝对化表达优先按硬阻断项处理。
- 叙事进入 S2 及以上时，必须判断是否影响主路线。
