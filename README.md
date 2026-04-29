# China 3C Marketing Copilot

面向中国市场的消费电子营销策划知识库。覆盖手机、笔记本、耳机、穿戴设备、智能家居等3C品类。

> 本知识库可作为 AI Agent 的上下文资料使用，也可独立阅读作为行业参考。
> 数据来自公开评测和行业报告，使用时请确认时效性。

## 能力一览

| 能力 | 触发场景 | 文档 |
|------|---------|------|
| 创意策划 | 帮我想几个创意 / 做个传播方案 | [docs/templates/creative-output.md](docs/templates/creative-output.md) |
| 竞品分析 | XX发布了，对我们有什么威胁 | [docs/templates/insight-output.md](docs/templates/insight-output.md) |
| 数据洞察 | 目前XX品类哪款最均衡 | [docs/templates/insight-output.md](docs/templates/insight-output.md) |
| 风险评估 | 有没有负面 / 风险点在哪 / 会不会翻车 | [docs/templates/risk-assessment.md](docs/templates/risk-assessment.md) |
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
├── LICENSE                            # MIT License
├── CONTRIBUTING.md                      # 贡献指南
├── quickstart-example.md              # 中英文完整使用示例
│
├── docs/                               # 文档层（方法论+模板+参考）
│   ├── templates/                      # 输出模板
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
│   │   ├── subagent-dataprocessor.md   # 数据预处理子Agent指令
│   │   └── subagent-factchecker.md     # 事实核查子Agent指令
│   └── ecosystem/                      # 行业生态
│       ├── kols.md                     # 3C核心KOL名录
│       └── industry-memes.md           # 行业黑话/梗字典+避雷指南
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
    └── preprocess.py                   # 数据预处理脚本
```

## 核心规则

### 数据纪律（铁律）

1. **禁止编造数字** — 没有就说"知识库暂无此数据"
2. **禁止混淆来源** — 每个数据点标注出处（KOL名+平台 / 评测标题）
3. **推测必须标注** — 写"[推测]"或"基于XX数据推断"
4. **竞品对比必须同源** — 两个产品的数据来源必须一致

详细自检流程：[docs/templates/quality-check-tools.md](docs/templates/quality-check-tools.md)

### 去AI化

- 禁止"不是A而是B""首先其次最后""值得注意的是""我们可以发现"
- 禁止企业通稿腔（空洞战略动词堆砌）
- 创意文案允许口语化和夸张，但不能是通稿和创意的混合体

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

创意去重：对照 [docs/templates/used-ideas.md](docs/templates/used-ideas.md) + 同次生成的核心hook不能重复

## 风险评估

评估维度和判定标准由用户定义，本知识库提供通用模板。
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

## 子Agent

| Agent | 触发 | 功能 |
|-------|------|------|
| DataProcessor | "处理新数据" | 纠错→判断类型→清洗→提取→更新索引 |
| FactChecker | "帮我检查""审核" | 对抗性审计：数据核验/遗漏检测/幻觉扫描 |

详细指令：[docs/references/subagent-dataprocessor.md](docs/references/subagent-dataprocessor.md) / [docs/references/subagent-factchecker.md](docs/references/subagent-factchecker.md)

## 快速开始

完整示例见 [quickstart-example.md](quickstart-example.md)。

简版：
1. 设置工作目录 — 告诉我路径，自动创建知识库结构
2. 配置用户信息（可选）— 服务品牌/品类/偏好/竞品/平台
3. 导入数据（可选但推荐）— 评测字幕/评论区/规格参数，自动预处理

## 免责声明

- 本知识库数据来自公开评测和行业报告，仅供参考，不构成营销建议
- 品牌表现和市场份额会随新品发布变化，使用前请确认数据时效性
- 翻车案例为行业典型模式描述，不构成对任何品牌的永久性评价

## License

MIT License — 详见 [LICENSE](LICENSE)
