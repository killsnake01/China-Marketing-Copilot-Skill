# 中国3C营销助手

面向中国市场的消费电子营销技能包。覆盖手机、笔记本、耳机、穿戴设备、智能家居等3C品类，适合做上市策略、信息架构、KOL渠道、创意策划、竞品洞察、评论区风险和负面早期预警。

一句话：给数码营销人一个能打方案、能审话术、能提前发现负面的随身策略台。

> 本仓库包含 `SKILL.md`，可作为 AI 智能体技能包使用，也可独立阅读作为行业参考。
> 数据来自公开评测和行业报告，涉及价格、销量、份额、新品参数时，请按当前日期重新核验。

## 适合谁

| 角色 | 典型痛点 | 这个技能包能做什么 |
|------|----------|--------------------|
| 品牌市场 | 上市前方向太多，难判断主路线 | 拆出推荐路线、备选路线、弃用路线和首轮动作 |
| 社媒运营 | 文案容易像通稿，评论区容易被拆 | 改成数码圈能接受的话术，并模拟负面评论 |
| KOL/渠道 | KOL排期、口播点、评论区动作难统一 | 输出KOL简报、平台分工、交付件和复盘指标 |
| 产品/销售 | 竞品发布后需要快速判断威胁 | 做同源数据矩阵、人群视角和行动建议 |
| 创业团队 | 没有完整营销团队，也要做新品上市 | 用离线知识库和模板快速搭出可执行方案 |

## 下载后马上能试

```text
帮我判断这台影像旗舰上市前7天怎么打，预算有限。
这句“AI全面重塑体验”会不会翻车？帮我改成数码圈能接受的话术。
竞品刚发新品，对我们手机的威胁在哪里？给我推荐路线和弃用路线。
评测解禁当天，KOL排期和评论区动作怎么安排？
我导入了一批耳机评论，先找负面苗头，再总结可用卖点。
```

## 核心吸引力

| 能力 | 下载价值 |
|------|----------|
| 中国3C语境 | 内置参数党、评测KOL、数码黑话、价格背刺、控评质疑、AI空话等高频场景 |
| 负面早期预警 | 58条校准样本覆盖数据打脸、产品缺陷、价格背刺、信任崩塌、价值观冒犯和KOL背叛 |
| 可执行策略链路 | 从策略诊断到信息屋、渠道KOL、创意、风险评估和数据导入都有模板 |
| 离线可用 | OpenClaw / Hermes 缺少浏览器能力时，仍能依靠包内知识库完成基础判断 |
| 可验证维护 | 16个真实营销任务样本、数据时效台账和发布前验证脚本，方便持续升级 |

## 版本和发布平台

- 当前版本：`v1.3.7`
- 更新日期：`2026-06-17`
- 版本源文件：[`VERSION`](VERSION)
- 技能标识：`china-marketing-copilot`

| 平台 | 当前版本 | 使用入口 | 发布口径 |
|------|----------|----------|----------|
| GitHub | `v1.3.7` | 仓库源码 | 源码、README、验证脚本以本仓库为准 |
| ClawHub | `v1.3.7` | `SKILL.md` | 上传或同步时版本号填 `1.3.7` |
| SkillHub | `v1.3.7` | zip 包上传 | 后台版本号填 `1.3.7`；如平台占用 slug，只调整平台 slug，不改内容版本 |
| Codex / OpenAI 技能 | `v1.3.7` | `$china-marketing-copilot` | 使用 `SKILL.md` 和 `agents/openai.yaml` |
| OpenClaw / Hermes | `v1.3.7` | `SKILL.md` + `docs/` | 默认离线可用，不依赖 browser-use、微博、新闻或实时网页能力 |

发布前运行：

```bash
python3 -B scripts/validate_skill_pack.py
```

## 能力一览

| 能力 | 触发场景 | 文档 |
|------|---------|------|
| 策略诊断 | 怎么打 / 传播架构 / 上市路线 | [docs/templates/strategy-decision-system.md](docs/templates/strategy-decision-system.md) |
| 信息架构 | 定位 / 标语 / 主张体系 / 话术 | [docs/templates/message-house.md](docs/templates/message-house.md) |
| 渠道KOL | KOL简报 / 平台排期 / 种草计划 | [docs/templates/channel-kol-activation.md](docs/templates/channel-kol-activation.md) |
| 创意策划 | 帮我想几个创意 / 做个传播方案 | [docs/templates/creative-output.md](docs/templates/creative-output.md) |
| 竞品分析 | XX发布了，对我们有什么威胁 | [docs/templates/insight-output.md](docs/templates/insight-output.md) |
| 数据洞察 | 目前XX品类哪款最均衡 | [docs/templates/insight-output.md](docs/templates/insight-output.md) |
| 风险评估 | 有没有负面 / 风险点在哪 / 会不会翻车 | [docs/templates/risk-assessment.md](docs/templates/risk-assessment.md) |
| 负面预警 | 评论区有负面苗头 / 评测解禁会不会发酵 | [docs/ecosystem/negative-early-warning.md](docs/ecosystem/negative-early-warning.md) |
| 横评对比 | XX价档哪款最值得买 | [docs/templates/insight-output.md](docs/templates/insight-output.md) |
| 数据导入 | 处理新数据 / 我导入了新文件 | [docs/references/subagent-dataprocessor.md](docs/references/subagent-dataprocessor.md) |
| 新品类破局 | 怎么传播新品类 / 市场教育成本高 | [docs/templates/new-category-playbook.md](docs/templates/new-category-playbook.md) |

## 知识库数据状态

| 品类 | 完备度 | 说明 |
|------|--------|------|
| 手机 | ⭐⭐⭐ 中高 | 16品牌矩阵、价位段格局、芯片阵营、KOL生态、传播风险 |
| 耳机 | ⭐⭐⭐ 中高 | 12款耳夹式横评数据（爱否科技）、品牌矩阵、品类结论 |
| 笔记本 | ⭐⭐⭐ 中高 | 笔吧2025双11选购指南，16品牌、8价位段、年度翻车案例 |
| 穿戴设备 | ⭐⭐⭐ 中高 | 品牌矩阵+市场份额（IDC 2025）+价位段+功能阵营+风险标注 |
| 智能家居 | ⭐⭐⭐⭐ 高 | 扫地机器人深度横评（4份评测交叉验证）+翻车案例+品牌矩阵+大疆ROMO+投影仪+全屋智能 |
| 其他3C | ⭐ 占位 | 平板/机械键盘/运动相机/AR眼镜等品类待补充 |

## 目录结构

```
.
├── README.md                          # 本文件
├── SKILL.md                           # 技能主入口
├── agents/openai.yaml                 # 智能体界面元数据
├── LICENSE                            # MIT 许可证
├── VERSION                            # 当前发布版本
├── CONTRIBUTING.md                     # 贡献指南
├── quickstart-example.md              # 中文完整使用示例
│
├── docs/                               # 文档层（方法论+模板+参考）
│   ├── data-index.md                   # 数据覆盖和时效索引
│   ├── data-sources.json               # 机器可读数据源和时效台账
│   ├── templates/                      # 输出模板
│   │   ├── strategy-decision-system.md # 策略诊断和传播架构
│   │   ├── message-house.md            # 信息屋和主张体系
│   │   ├── channel-kol-activation.md   # 渠道和KOL执行简报
│   │   ├── creative-output.md          # 创意策划输出规范
│   │   ├── insight-output.md           # 洞察/分析输出规范
│   │   ├── risk-assessment.md          # 风险评估模板
│   │   ├── new-category-playbook.md    # 新品类破局方法论
│   │   ├── quality-check-tools.md      # 去AI化+事实核查清单
│   │   ├── knowledge-base-structure.md # 知识库结构说明
│   │   └── used-ideas.md               # 已用创意记录（去重）
│   ├── references/                     # 参考文档
│   │   ├── comment-personas.md         # 评论区5大人群原型
│   │   ├── industry-ecosystem.md       # 平台传播规律
│   │   ├── eco-integration.md          # 外部工具集成协议
│   │   ├── subagent-dataprocessor.md   # 数据预处理子智能体指令
│   │   └── subagent-factchecker.md     # 事实核查子智能体指令
│   ├── ecosystem/                      # 行业生态
│   │   ├── kols.md                     # 3C核心KOL名录
│   │   ├── market-signals-2026.md      # 2026市场舆情信号库
│   │   ├── negative-early-warning.md   # 负面早期预警库
│   │   ├── negative-signal-rules.json  # 负面预警机器可读规则
│   │   └── industry-memes.md           # 行业黑话/梗字典+避雷指南
│   └── evals/
│       ├── marketing-task-samples.md   # 真实营销任务评测集
│       └── negative-signal-samples.md  # 负面识别样本集
│
├── knowledge-base/                     # 知识库数据层（可扩展）
│   ├── mobile/_index.md                # 手机品牌矩阵
│   ├── headphones/_index.md            # 耳机品牌矩阵+耳夹式横评
│   ├── laptops/_index.md               # 笔记本品牌矩阵+选购指南
│   ├── wearables/_index.md             # 穿戴设备品牌矩阵
│   ├── smart-home/_index.md            # 智能家居品牌矩阵+扫地机器人横评
│   └── other/_index.md                 # 其他3C占位
│
└── scripts/
    ├── preprocess.py                   # 数据预处理脚本
    ├── evaluate_negative_signals.py    # 负面规则校准脚本
    └── validate_skill_pack.py          # 技能包验证脚本
```

## 核心规则

### 数据纪律

1. 禁止编造数字：没有就写 `知识库暂无此数据`
2. 禁止混淆来源：每个数据点标注出处，如 KOL 名、平台或评测标题
3. 推测必须标注：写 `[推测]` 或 `基于XX数据推断`
4. 竞品对比必须同源：两个产品的数据来源必须一致

详细自检流程：[docs/templates/quality-check-tools.md](docs/templates/quality-check-tools.md)

### 去AI化

- 避免套话：`首先其次最后`、`值得注意的是`、`我们可以发现`
- 避免企业通稿腔：空洞战略动词堆砌、没有证据的宏大判断
- 创意文案可以口语化、可以有记忆点，但事实边界必须稳

详细替换规则：[docs/templates/quality-check-tools.md](docs/templates/quality-check-tools.md)

### 技术事实审核

技术类比必须经得起专业博主检验。不确定就改用"实测数据"替代"推导类比"。

## 创意生成

创意角度来自知识库数据驱动，不预设固定角度池：
- 评测数据中找可量化优势点
- 评论区中找用户自发惊喜点
- 竞品对比中找差异化空位
- 使用场景中找共鸣点
- 行业热点中找借势机会

创意去重：对照 [docs/templates/used-ideas.md](docs/templates/used-ideas.md) + 同次生成的核心钩子不能重复

## 风险评估

默认按技术事实、竞品反击、行业黑话、平台合规、评论区翻车、KOL合作风险评分；用户也可以自定义维度。
详见 [docs/templates/risk-assessment.md](docs/templates/risk-assessment.md)

评论区模拟：必须模拟负面反应和解构找茬人群。
详见 [docs/references/comment-personas.md](docs/references/comment-personas.md)

## 新品类破局

内置5大可复用破局方法论：

1. **认知刷新法** — 找到人类极限/常识标准 → 用产品刷新它 → 数据可视化
2. **感知价值锚定法** — 推超高价锚定产品 → 专业背书 → 话术重构价值
3. **尝鲜者探索法** — 招募极客尝鲜者 → 开放使用 → 收集数据 → 让需求浮现
4. **先锋创作者法** — 找先锋创作者 → 探索"可能性" → 电影级制作
5. **专业信任纪录片法** — 真实专业用户 → 6个月实地测试 → 克制美学纪录片

详见 [docs/templates/new-category-playbook.md](docs/templates/new-category-playbook.md)

## 平台兼容

本技能包的默认路径按离线知识库设计：

- 优先读取包内 `docs/` 和 `knowledge-base/`
- 外部搜索、浏览器、微博、新闻能力均为可选增强
- OpenClaw / Hermes 环境缺少 browser-use 时，仍可用静态市场信号库和负面规则完成判断
- 更新平台版本时，外部后台统一填写 `1.3.7`

## 子智能体指令

| 子智能体 | 触发 | 功能 |
|-------|------|------|
| 数据处理 | `处理新数据` | 纠错、判断类型、清洗、提取、更新索引 |
| 事实核查 | `帮我检查` / `审核` | 对抗性审计：数据核验、遗漏检测、幻觉扫描 |

详细指令：[docs/references/subagent-dataprocessor.md](docs/references/subagent-dataprocessor.md) / [docs/references/subagent-factchecker.md](docs/references/subagent-factchecker.md)

## 快速开始

完整示例见 [quickstart-example.md](quickstart-example.md)。

简版：
1. 安装或引用本仓库作为技能包 — 入口文件为 [SKILL.md](SKILL.md)
2. 设置工作目录 — 告诉智能体服务品牌、品类、偏好、竞品和平台
3. 导入数据（可选但推荐）— 评测字幕/评论区/规格参数，使用 `scripts/preprocess.py` 预处理；评论区用 `--mode comments`，知识库文档用 `--mode document`
4. 做策略判断 — 对照 [docs/templates/strategy-decision-system.md](docs/templates/strategy-decision-system.md) 先确定主路线、备选路线和弃用路线
5. 搭信息屋 — 对照 [docs/templates/message-house.md](docs/templates/message-house.md) 明确核心主张、证据柱、反对意见和平台文案
6. 拆执行 — 对照 [docs/templates/channel-kol-activation.md](docs/templates/channel-kol-activation.md) 输出渠道、KOL、评论区和复盘指标
7. 更新数据源后 — 同步维护 [docs/data-sources.json](docs/data-sources.json)
8. 更新负面规则后 — 运行 `python3 -B scripts/evaluate_negative_signals.py` 校准样本集
9. 提交或发布前 — 运行 `python3 -B scripts/validate_skill_pack.py`
10. 正式输出前 — 按 [docs/templates/quality-check-tools.md](docs/templates/quality-check-tools.md) 做事实和话术自检

## 免责声明

- 本知识库数据来自公开评测和行业报告，仅供参考，不构成营销建议
- 品牌表现和市场份额会随新品发布变化，使用前请确认数据时效性
- 翻车案例为行业典型模式描述，不构成对任何品牌的永久性评价

## 许可证

MIT 许可证，详见 [LICENSE](LICENSE)
