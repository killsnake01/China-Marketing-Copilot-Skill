# 输出质量评分路由

## 触发

用户要求判断方案够不够好、打分、验收、能不能交付、能不能给老板看、哪里需要补，或要求按标准审一版上市方案、传播方案、KOL Brief、物料审核结果。

## 读取顺序

1. `docs/evals/output-quality-rubric.json`
2. `docs/templates/quality-check-tools.md`
3. 按用户方案类型读取对应主路由：
   - 上市策略：`docs/routes/launch-decision.md`
   - 文案话术：`docs/routes/messaging-review.md`
   - 渠道KOL：`docs/routes/channel-kol.md`
   - 风险评估：`docs/routes/risk-review.md`
   - 正式物料：`docs/routes/material-audit.md`
4. 涉及上市或正式上线时，读取 `docs/templates/execution-readiness-gate.md` 和 `assets/launch-decision-card.md`

## 必备输出

- 硬阻断项：如编造事实、当前信息未核验、缺负面预警、缺执行门、密钥落库风险。
- 8维评分：路由与上下文、事实纪律、证据台账、路线裁决、负面早期预警、执行就绪、中国3C表达、平台兼容。
- 总分和结论：可直接交付、可用但需复核、需要重写局部或重做。
- 扣分原因：逐项说明缺口，不能只给数字。
- 补救优先级：先补会影响上线判断的事实、证据、风险和执行责任。
- 重写指令：给出可直接交给智能体继续修改的具体动作。

## 评分纪律

- 出现全局硬阻断项时，总分最高 59。
- 关键事实未核验时，执行就绪维度不能满分。
- 缺少负面早期预警时，正式上市、正式物料或KOL方案不能判为可直接交付。
- 评分要服务决策，不能为了鼓励用户而抬分。
- 如用户只给了片段，明确评分范围和无法评分的部分。
