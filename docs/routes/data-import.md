# 数据导入与负面分析路由

## 触发

用户提供评论、评测字幕、规格表、风险笔记、竞品资料、客服反馈或要求“处理新数据”。

## 读取顺序

1. `docs/references/subagent-dataprocessor.md`
2. `docs/ecosystem/negative-early-warning.md`
3. `docs/evals/negative-signal-samples.md`
4. 上线后复盘或要求入库学习时读取 `docs/templates/decision-learning-record.md`
5. 对应品类索引
6. 本地文件处理时运行 `scripts/preprocess.py`
7. 评论文件可直接使用 JSONL、CSV、TSV 或逐行文本运行 `scripts/analyze_signal_batch.py`；CSV/TSV 支持常见中英文字段名，结构化结果仍以 `schemas/negative-signal-batch.schema.json` 为准

## 必备输出

- 数据类型和来源标签。
- 原文样本，优先保留负面原话。
- 负面信号、叙事阶段和触发阈值。
- 结构化批次补充独立账号、平台分布、2小时传播速度、趋势标签、重复传播噪声、权威角色和业务影响。
- 可传播卖点和证据缺口。
- 入库建议和需要复核的字段。
- 上线后复盘或用户要求学习记录时，增加补证据、禁用话术、阈值调整或KOL记录。

## 纪律

- 先抽取负面，再总结正面。
- 用户明确“只找负面、只提取数字、只整理规格”时，只完成指定动作，不追加完整营销方案。
- 不改写用户原话为更好看的营销句。
- 更新负面规则后运行 `python3 -B scripts/evaluate_negative_signals.py`。
- 更新传播阶段规则后运行 `python3 -B scripts/evaluate_negative_propagation.py`。
- 原始表格缺少时区时按中国标准时间 `+08:00` 处理，并在数据质量提醒中公开数量。
- 导入上线后反馈或复盘材料时，同步判断需不需要更新 `docs/evals/decision-learning-samples.json`。
