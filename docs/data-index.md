# 数据索引与时效规则

本文件用于帮助智能体快速选择知识库文件，并判断哪些结论需要外部复核。

机器可读台账见 [`docs/data-sources.json`](data-sources.json)。当本文件和台账冲突时，以台账的 `data_cutoff`、`must_refresh` 和 `status` 字段作为发布前复核依据。

## 总体原则

- 价格、排名、市场份额、新品规格、平台热搜、KOL近期口碑属于高时效信息；正式输出前应外部复核。
- 评测结论、传播风险、圈层黑话、平台机制属于中时效信息；超过 6 个月建议复核。
- 方法论、输出模板、评论区人群原型属于低时效信息；按使用反馈更新。
- 无法确认的数据必须标注 `[待验证]` 或 `知识库暂无此数据`。

## 品类文件

| 品类 | 主文件 | 当前状态 | 时效判断 | 使用场景 |
|------|--------|----------|----------|----------|
| 手机 | `knowledge-base/mobile/_index.md` | 中高覆盖，数据截止 2026-04 | 价格/新品/排名需复核 | 影像、性能、续航、价位段、品牌竞争 |
| 耳机 | `knowledge-base/headphones/_index.md` | 中高覆盖，含耳夹式横评 | 单品价格和新品需复核 | 降噪、音质、佩戴、种草创意 |
| 笔记本 | `knowledge-base/laptops/_index.md` | 中高覆盖，含 2025 双11选购和负面案例 | 新平台/新品需复核 | 游戏本、轻薄本、选购、翻车风险 |
| 穿戴设备 | `knowledge-base/wearables/_index.md` | 中高覆盖，含 IDC 2025 市场份额 | 市占率和健康功能需复核 | 手表、手环、健康监测、运动 |
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
| `docs/templates/strategy-decision-system.md` | 需求模糊、需要传播策略、定位选择、上市路线、平台组合或预算取舍 |
| `docs/templates/message-house.md` | 需要定位、标语、主张体系、发布会话术、社媒文案、KOL口径或反驳口径 |
| `docs/templates/channel-kol-activation.md` | 需要KOL简报、渠道排期、平台分工、内容交付、评论区动作或复盘指标 |
| `docs/ecosystem/industry-memes.md` | 涉及营销话术、梗、黑话、评论区反噬 |
| `docs/ecosystem/kols.md` | 涉及 KOL 合作、平台背书、评测可信度 |
| `docs/ecosystem/market-signals-2026.md` | 涉及 2026 年节日情绪、KOL争议、AI硬件叙事、价格/补贴敏感期 |
| `docs/ecosystem/negative-early-warning.md` | 需要尽早识别评论区、评测、KOL、价格和价值观负面苗头 |
| `docs/ecosystem/negative-signal-rules.json` | 负面早期预警的机器可读关键词、等级和动作规则 |
| `docs/references/comment-personas.md` | 需要模拟评论区或判断翻车风险 |
| `docs/references/industry-ecosystem.md` | 需要做平台适配、传播路径、内容形式选择 |
| `docs/references/eco-integration.md` | 需要实时搜索、浏览器爬取、长文本总结 |
| `docs/evals/negative-signal-samples.md` | 维护负面规则时，用于校准误报和漏报 |
| `docs/evals/marketing-task-samples.md` | 维护任务级输出质量时，用于校准路由、事实纪律、策略判断、风险识别和可执行性 |

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
