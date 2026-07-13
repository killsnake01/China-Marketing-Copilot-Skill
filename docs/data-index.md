# 数据索引与时效规则

本文件用于帮助智能体快速选择知识库文件，并判断哪些结论需要外部复核。

机器可读台账见 [`docs/data-sources.json`](data-sources.json)。当本文件和台账冲突时，以台账的 `data_cutoff`、`must_refresh` 和 `status` 字段作为发布前复核依据。

来源可追溯程度见 [`docs/evidence-ledger.json`](evidence-ledger.json)。品类时效状态说明“数据多旧”，来源台账说明“能否回到原始材料复核”；两道门都通过后，才可把高时效字段写成已核验事实。

## 总体原则

- 价格、排名、市场份额、新品规格、平台热搜、KOL近期口碑属于高时效信息；正式输出前应外部复核。
- 评测结论、传播风险、圈层黑话、平台机制属于中时效信息；超过 6 个月建议复核。
- 方法论、输出模板、评论区人群原型属于低时效信息；按使用反馈更新。
- 无法确认的数据必须标注 `[待验证]` 或 `知识库暂无此数据`。
- 产品对比、行业共识和绝对化话术先过证据主张纪律；缺同源、缺来源或缺知识库数据时先降级。

## 品类文件

| 品类 | 主文件 | 当前状态 | 时效判断 | 使用场景 |
|------|--------|----------|----------|----------|
| 手机 | `knowledge-base/mobile/_index.md` | 中高覆盖，数据截止 2026-04 | 价格/新品/排名需复核 | 影像、性能、续航、价位段、品牌竞争 |
| 耳机 | `knowledge-base/headphones/_index.md` | 中高覆盖，含耳夹式横评 | 单品价格和新品需复核 | 降噪、音质、佩戴、种草创意 |
| 笔记本 | `knowledge-base/laptops/_index.md` | 中高覆盖，含 2025 双11选购和负面案例 | 新平台/新品需复核 | 游戏本、轻薄本、选购、翻车风险 |
| 穿戴设备 | `knowledge-base/wearables/_index.md` | 中高覆盖，数据截止 2025-12，含 IDC 2025 历史份额 | 市占率、医疗合规和健康功能需复核 | 手表、手环、健康监测、运动 |
| 智能家居 | `knowledge-base/smart-home/_index.md` | 高覆盖，扫地机器人资料较多 | 新品和渠道价格需复核 | 扫地机、投影、全屋智能、生态联动 |
| 其他3C | `knowledge-base/other/_index.md` | 占位 | 需先导入数据 | 平板、键盘、运动相机、AR眼镜等 |

## 深度数据文件

| 文件 | 适用场景 | 备注 |
|------|----------|------|
| `knowledge-base/headphones/clip-earphones-comparison-2026.md` | 耳夹式耳机横评、种草、竞品对比 | 优先用于同源横评 |
| `knowledge-base/laptops/annual-negative-awards-2025.md` | 笔记本风险、避坑、评论区模拟 | 适合风险评估，不作永久品牌定性 |
| `knowledge-base/smart-home/robot-vacuum-comparison-2025.md` | 扫地机器人横评、功能对比 | 输出前检查具体型号是否仍在售 |

## 横向参考文件

| 文件 | 何时读取 |
|------|----------|
| `docs/runtime-capabilities.json` | 需要判断当前环境采用纯文档、脚本增强或联网增强模式 |
| `docs/agent-router.md` | 需要选择主路由、最小上下文或机器校验入口 |
| `docs/evidence-ledger.json` | 需要核对包内来源状态、允许用途和强制复核字段 |
| `docs/routes/launch-decision.md` | 需要上市策略、路线裁决、上市决策单或 上线、调整或暂停判断 |
| `docs/routes/messaging-review.md` | 需要定位、标语、话术、平台文案或AI主张审核 |
| `docs/routes/creative-campaign.md` | 需要创意策划、传播方案、小红书种草、短视频选题或内容栏目 |
| `docs/routes/channel-kol.md` | 需要KOL排期、平台分工、评测解禁或评论区动作 |
| `docs/routes/competitor-intelligence.md` | 需要竞品威胁、产品对比、同源数据矩阵或站位判断 |
| `docs/routes/risk-review.md` | 需要风险评估、负面预警或评论区压力测试 |
| `docs/routes/post-launch-war-room.md` | 需要上线后战情复盘、判断继续投放、缩窄主张、切换路线、暂停扩散或沉淀决策学习记录 |
| `docs/routes/data-import.md` | 需要处理评论、评测字幕、规格参数、风险笔记或上线后反馈入库 |
| `docs/routes/material-audit.md` | 需要审核正式广告、发布会PPT、商品页或KOL Brief |
| `docs/routes/output-quality.md` | 需要给方案打分、验收、判断能不能交付或列补救优先级 |
| `docs/templates/strategy-decision-system.md` | 需求模糊、需要传播策略、定位选择、上市路线、平台组合或预算取舍 |
| `docs/templates/message-house.md` | 需要定位、标语、主张体系、发布会话术、社媒文案、KOL口径或反驳口径 |
| `docs/templates/launch-decision-package.md` | 需要把完整上市决策收束成封面、目录、包状态、交接摘要和待决事项 |
| `docs/templates/executive-decision-memo.md` | 需要把上市决策压缩成管理层纪要、第一屏结论、暂停条件或下一负责人动作 |
| `docs/templates/route-scorecard.md` | 需要把推荐、备选、弃用路线放到同一评分体系里判断主线、备选和弃用理由 |
| `docs/templates/evidence-freshness-gate.md` | 需要判断价格、排名、份额、新品参数、KOL近期口碑或平台热度能否直接用于当前结论 |
| `docs/templates/risk-ledger.md` | 需要把风险判断转成证据锚点、压缩叙事、扩散路径、业务影响和反证条件 |
| `docs/templates/route-switch-playbook.md` | 需要把切换触发器转成继续、缩窄、切换、暂停动作时读取 |
| `docs/templates/decision-consistency-gate.md` | 需要检查总控台、决策结论、硬阻断、置信度和自检计数是否对齐时读取 |
| `docs/templates/channel-kol-activation.md` | 需要KOL简报、渠道排期、平台分工、内容交付、评论区动作或复盘指标 |
| `docs/templates/execution-readiness-gate.md` | 需要上线前判断、72小时动作、7天跟进、负责人、停投阈值或执行补齐清单 |
| `docs/templates/post-launch-war-room.md` | 需要上线后24/72小时反馈复盘、主张动作、暂停/切换条件或复盘入库 |
| `docs/templates/decision-learning-record.md` | 需要把复盘结论沉淀成路线保留、补证据、禁用话术、阈值调整或KOL记录 |
| `docs/templates/output-mode-policy.md` | 需要控制答案长度、区分快速版/标准版/深度版或降低输出负担 |
| `assets/launch-decision-card.md` | 需要统一的上市决策单、上市任务简报归一化、管理层汇报收口或最终上线判断 |
| `schemas/launch-decision.schema.json` | 需要生成或验收结构化上市决策单、上市任务简报字段和跨字段一致性时使用 |
| `docs/ecosystem/industry-memes.md` | 涉及营销话术、梗、黑话、评论区反噬 |
| `docs/ecosystem/kols.md` | 涉及 KOL 合作、平台背书、评测可信度 |
| `docs/ecosystem/market-signals-2026.md` | 涉及 2026 年节日情绪、KOL争议、AI硬件叙事、价格/补贴敏感期 |
| `docs/ecosystem/negative-early-warning.md` | 需要尽早识别评论区、评测、KOL、价格和价值观负面苗头 |
| `docs/ecosystem/negative-signal-rules.json` | 负面早期预警的机器可读关键词、等级和动作规则 |
| `docs/references/comment-personas.md` | 需要模拟评论区或判断翻车风险 |
| `docs/references/industry-ecosystem.md` | 需要做平台适配、传播路径、内容形式选择 |
| `docs/references/eco-integration.md` | 需要实时搜索、浏览器爬取、长文本总结 |
| `docs/evals/negative-signal-samples.md` | 维护负面规则时，用于校准误报和漏报 |
| `docs/evals/negative-propagation-samples.json` | 维护独立账号、速度、跨平台、权威放大、业务影响和重复噪声判断时读取 |
| `docs/evals/freshness-claim-samples.json` | 维护证据时效规则时，用于校准高时效主张识别和标注 |
| `docs/evals/evidence-claim-samples.json` | 维护证据主张纪律时，用于校准已核验、待验证、同源不足、无数据和禁用绝对化 |
| `docs/evals/decision-package-samples.json` | 维护上市决策包封面时，用于校准可评审、需补证据和暂停评审三种包状态 |
| `docs/evals/executive-memo-samples.json` | 维护管理层决策纪要时，用于校准直接执行、调整后执行和暂停重做判断 |
| `docs/evals/route-scorecard-samples.json` | 维护路线评分卡时，用于校准推荐、备选、弃用和总分阈值 |
| `docs/evals/risk-ledger-samples.json` | 维护风险账本时，用于校准P0/P1/P2/P3优先级和继续、缩窄、切换、暂停路线影响 |
| `docs/evals/route-switch-samples.json` | 维护路线切换剧本时，用于校准继续、缩窄、切换和暂停判断 |
| `docs/evals/execution-gate-samples.json` | 维护执行闸门时，用于校准直接执行、调整后执行和暂停重做判断 |
| `docs/evals/post-launch-samples.json` | 维护上线后战情复盘时，用于校准继续、缩窄、切换和暂停判断 |
| `docs/evals/decision-learning-samples.json` | 维护决策学习记录时，用于校准路线保留、补证据、禁用话术、更新阈值和更新KOL记录 |
| `docs/evals/launch-decision-card-samples.json` | 维护上市决策单统一字段时，用于校准结构完整性 |
| `docs/evals/output-quality-rubric.json` | 正式策略、上市决策单、物料审核或平台展示样例交付前，用于做100分输出质量评分 |
| `scripts/evaluate_quality_rubric.py` | 需要验证评分卡结构，或对候选输出做轻量评分时使用 |
| `scripts/evaluate_freshness_claims.py` | 需要验证时效样本，或扫描一条主张是否需要当前复核时使用 |
| `scripts/evaluate_evidence_claims.py` | 需要验证证据主张样本，或扫描一条营销主张是否该标注、降级或拦截时使用 |
| `scripts/evaluate_decision_package.py` | 需要验证上市决策包封面样本，或扫描一条交付状态应该可评审、需补证据还是暂停评审时使用 |
| `scripts/evaluate_executive_memo.py` | 需要验证管理层决策纪要样本，或扫描一条决策状态应该直接执行、调整后执行还是暂停重做时使用 |
| `scripts/evaluate_route_scorecard.py` | 需要验证路线评分卡样本，或扫描一条路线应该推荐、保留备选还是弃用时使用 |
| `scripts/evaluate_risk_ledger.py` | 需要验证风险账本样本，或扫描一条风险信号的优先级和路线影响时使用 |
| `scripts/evaluate_route_switches.py` | 需要验证路线切换样本，或扫描一个信号应该继续、缩窄、切换还是暂停时使用 |
| `scripts/evaluate_execution_gate.py` | 需要验证执行闸门样本，或扫描一条上市前执行状态时使用 |
| `scripts/evaluate_post_launch_samples.py` | 需要验证上线后战情样本，或扫描一条上线反馈时使用 |
| `scripts/evaluate_decision_learning.py` | 需要验证决策学习样本，或扫描一条复盘笔记应该沉淀成哪类学习动作时使用 |
| `scripts/analyze_signal_batch.py` | 需要分析带时间、平台、账号、角色、互动和业务影响字段的JSONL评论批次时使用 |
| `scripts/evaluate_negative_propagation.py` | 需要校准S0-S4传播阶段、刷屏降噪和业务影响门槛时使用 |
| `scripts/validate_decision_output.py` | 需要验证结构化上市决策单、上市任务简报字段完整性和跨字段一致性时使用 |

## 置信度规则

| 置信度 | 判定标准 |
|--------|----------|
| 高 | 关键数字、产品、来源均来自知识库或已外部复核；无未标注推测 |
| 中 | 少量结论基于合理推断，已标注 `[推测]`；不影响核心建议 |
| 低 | 关键数据缺失、时效性不足、来源冲突，或无法复核当前价格/新品信息 |

## 更新要求

- 新增或大改品类文件时，同时更新本索引。
- 新增或大改品类文件时，同时更新 `docs/data-sources.json`。
- 导入新数据时记录来源、平台、标题、采集日期、适用品类。
- 对明显过期的价格、排名、市场份额，不直接用于正式物料。
- 更新证据主张样本后，运行 `python3 -B scripts/evaluate_evidence_claims.py --check`。
- 更新上市决策包封面样本后，运行 `python3 -B scripts/evaluate_decision_package.py --check`。
- 更新管理层决策纪要样本后，运行 `python3 -B scripts/evaluate_executive_memo.py --check`。
- 更新路线评分卡样本后，运行 `python3 -B scripts/evaluate_route_scorecard.py --check`。
- 更新风险账本样本后，运行 `python3 -B scripts/evaluate_risk_ledger.py --check`。
- 更新路线切换样本后，运行 `python3 -B scripts/evaluate_route_switches.py --check`。
- 更新决策单 schema 或一致性规则后，运行 `python3 -B scripts/validate_decision_output.py --check`。
- 更新执行闸门规则后，运行 `python3 -B scripts/evaluate_execution_gate.py --check`。
- 更新决策学习记录样本后，运行 `python3 -B scripts/evaluate_decision_learning.py --check`。
