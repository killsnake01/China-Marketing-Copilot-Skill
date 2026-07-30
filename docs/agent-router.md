# 智能体路由索引

> 用途：承接 `SKILL.md` 的细粒度路由和资源选择。运行时先选一个主任务路由，再按该路由读取模板、参考文件、知识库或脚本。

## 读取顺序

1. `docs/runtime-capabilities.json`：判断纯文档、脚本增强或联网增强模式。
2. `docs/templates/output-mode-policy.md`：判断快速版、标准版或深度版。
3. 交付物属于 PPT、Keynote、广告、发布会方案、导演阐述、KOL 合作方案或成片脚本时，读取 `docs/templates/audience-layering.md`。
4. 本文件：选择主任务路由和最小上下文。
5. `docs/data-index.md`：选择品类索引、来源状态、时效规则和深度数据文件。
6. 主任务路由文件：读取该路由指定的模板和参考文件。

## 主任务路由 选择

| 场景 | 主任务路由 | 最小配套资源 |
|------|----------|--------------|
| 上市路线、预算取舍、上线、调整或暂停判断 | `docs/routes/launch-decision.md` | 默认：`docs/templates/strategy-decision-system.md`; 对应品类索引。完整决策交付再读取决策包、管理层纪要、评分卡、风险账本和Schema |
| 定位、标语、AI话术、社媒文案 | `docs/routes/messaging-review.md` | `docs/templates/message-house.md`; `docs/templates/quality-check-tools.md` |
| 创意策划、传播方案、种草内容、短视频选题 | `docs/routes/creative-campaign.md` | `docs/templates/creative-output.md`; `docs/templates/strategy-decision-system.md`; `docs/ecosystem/industry-memes.md`; 对应品类索引 |
| KOL排期、平台分工、评测解禁 | `docs/routes/channel-kol.md` | `docs/templates/channel-kol-activation.md`; `docs/ecosystem/kols.md` |
| 竞品威胁、同源数据矩阵、站位判断 | `docs/routes/competitor-intelligence.md` | `docs/templates/insight-output.md`; 对应品类索引 |
| 翻车风险、负面苗头、评论区压力测试 | `docs/routes/risk-review.md` | `docs/ecosystem/negative-early-warning.md`; `docs/references/comment-personas.md` |
| 上线后反馈、战情复盘、撤稿或继续投 | `docs/routes/post-launch-war-room.md` | `docs/templates/post-launch-war-room.md`; `docs/templates/decision-learning-record.md`; `docs/templates/evidence-freshness-gate.md` |
| 评论、评测字幕、规格参数导入 | `docs/routes/data-import.md` | `docs/references/subagent-dataprocessor.md`; `docs/evals/negative-signal-samples.md`; `docs/templates/decision-learning-record.md` |
| 已成稿广告、PPT、商品页、KOL简报的审核或上线判断 | `docs/routes/material-audit.md` | `docs/references/subagent-factchecker.md`; `docs/templates/risk-assessment.md`; `docs/templates/audience-layering.md` |
| 输出评分、验收、交付前判断 | `docs/routes/output-quality.md` | `docs/evals/output-quality-rubric.json`; `docs/templates/quality-check-tools.md` |

## 路由冲突仲裁

同一请求命中多个场景时，按用户要完成的动作选择主路由：

1. 已经上线并提供评论、KOL或客服反馈：`post-launch-war-room`。
2. 提供完整成稿、PPT、商品页或KOL简报并询问能否发布：`material-audit`。
3. 要求按标准打分、验收或判断能否给管理层：`output-quality`。
4. 重点询问翻车、负面、争议或危机：`risk-review`。
5. 重点要求改写定位、标语、主张或口播：`messaging-review`。
6. 重点要求新创意、传播方案或内容方向：`creative-campaign`。
7. 提供原始评论、字幕、规格表或风险笔记并要求整理：`data-import`。
8. 涉及总路线、预算取舍或上线裁决：`launch-decision`。

从零制作老板创意提案、发布会方案、导演阐述或 KOL 合作方案时，按创作动作选择 `creative-campaign`、`channel-kol` 或 `messaging-review`。`material-audit` 只在后台辅助，不能接管前台结构。

纯购买咨询、维修排障和通用新闻摘要不触发本技能。

营销动作决定触发边界：

- “哪款耳机更适合种草”“竞品哪项卖点威胁我们”属于营销竞品洞察，触发本技能。
- “预算3000元给我推荐自用手机”属于个人购买咨询，不触发本技能。

## 旧术语映射

| 用户旧说法 | 当前资源 | 默认交付 |
|------------|----------|----------|
| 信息屋 | `docs/templates/message-house.md` | 核心主张、证据柱、反对意见、禁用表达 |
| 上市打法 | `docs/routes/launch-decision.md` | 推荐、备选、弃用路线、72小时动作、7天跟进 |
| KOL简报 | `docs/templates/channel-kol-activation.md` | 平台分工、KOL类型、交付件、必说与禁说 |
| 创意方案 | `docs/templates/creative-output.md` | 用户要求数量的创意、钩子、内容形式和风险 |
| 风险评分 | `docs/routes/risk-review.md` | 总体判断、风险点、模拟评论、替代表达 |
| 评论分析 | `docs/routes/data-import.md` | 原文、负面信号、正面发现、数值线索和入库建议 |

## 品类索引

| 品类 | 首选文件 |
|------|----------|
| 手机 | `knowledge-base/mobile/_index.md` |
| 耳机 | `knowledge-base/headphones/_index.md` |
| 笔记本 | `knowledge-base/laptops/_index.md` |
| 穿戴设备 | `knowledge-base/wearables/_index.md` |
| 智能家居 | `knowledge-base/smart-home/_index.md` |
| 其他3C | `knowledge-base/other/_index.md` |

## 机器校验入口

| 目标 | 脚本 |
|------|------|
| 负面信号样本 | `python3 -B scripts/evaluate_negative_signals.py` |
| 结构化负面批次 | `python3 -B scripts/analyze_signal_batch.py --input {comments.jsonl} --category {category}` |
| 负面传播样本 | `python3 -B scripts/evaluate_negative_propagation.py` |
| 证据时效样本 | `python3 -B scripts/evaluate_freshness_claims.py --check` |
| 证据主张样本 | `python3 -B scripts/evaluate_evidence_claims.py --check` |
| 上市决策包样本 | `python3 -B scripts/evaluate_decision_package.py --check` |
| 管理层决策纪要样本 | `python3 -B scripts/evaluate_executive_memo.py --check` |
| 路线评分卡样本 | `python3 -B scripts/evaluate_route_scorecard.py --check` |
| 风险账本样本 | `python3 -B scripts/evaluate_risk_ledger.py --check` |
| 路线切换样本 | `python3 -B scripts/evaluate_route_switches.py --check` |
| 上线后战情样本 | `python3 -B scripts/evaluate_post_launch_samples.py --check` |
| 决策学习样本 | `python3 -B scripts/evaluate_decision_learning.py --check` |
| 结构化决策单 | `python3 -B scripts/validate_decision_output.py --check` |
| 质量评分卡 | `python3 -B scripts/evaluate_quality_rubric.py --check` |
| 正式物料分层 | `python3 -B scripts/evaluate_audience_layering.py --check` |

## 路由纪律

- 一次任务只选一个主任务路由，其他路由只作为辅助。
- 先确定最终受众，再区分前台正式物料与后台审核；两层可以同轮交付，但不能混在同一画布。
- 同时使用演示文稿、文档或创意制作技能时，营销技能提供判断、证据和风险，输出技能决定最终受众可见的语言、标题与信息密度。
- 最终受众表达要求优先于内部审核模板的可见呈现要求；审核结果默认进入备注、内部附录或独立检查表。
- 禁止把风险评分、执行门、智能体工作指令和制作纪律原样复制到前台页面。
- 先用包内文件；外部搜索、微博、新闻和浏览器只作增强。
- 当前价格、排名、份额、新品参数、平台热度和KOL近期口碑先过证据时效门。
- 包内来源可追溯程度按 `docs/evidence-ledger.json` 判断；部分可追溯来源不能支撑当前高时效结论。
- 批量评论有时间、平台、账号和互动字段时优先运行结构化批次分析；单账号刷屏和高度重复内容不能直接推高叙事阶段。
- 用户明确要求管理层上市裁决、决策记录或路线取舍时，先输出上市任务简报、上市总控台和管理层决策纪要；仅说明“给老板看”时按物料用途选择。
- 用户明确要求完整上市决策包时，增加封面、包状态、包内目录、负责人角色和待决事项。
- 用户要求路线比较、统一评分或解释取舍时，增加路线评分卡。
- 用户要求路线切换预案时，把触发器展开成继续、缩窄、切换或暂停动作。
- 用户要求结构化决策单、JSON或机器验收时，才生成包含 `launch_brief`、`decision_package`、`executive_memo`、`route_scorecard` 和 `risk_ledger` 的验收对象。
- 明确的正式上线、排期、管理层决策记录和物料审核必须跑执行就绪门；创意提案制作在后台运行，并将可见内容改写为自然推进建议。
- 上线后反馈必须判断主张动作：继续放大、缩窄主张、切换路线或暂停扩散。
- 上线后复盘需要沉淀为路线保留、补证据、禁用话术、更新阈值或KOL记录。
