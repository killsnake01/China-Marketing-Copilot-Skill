# 知识库结构

## 目录规范

```
{工作目录}/
├── SKILL.md                     # Skill 主入口
├── quickstart-example.md        # 快速开始示例
├── mobile/                      # 手机品类
│   └── _index.md               # 品牌矩阵+价位段+芯片阵营+传播风险
├── headphones/                  # 耳机品类
│   ├── _index.md               # 品牌矩阵+横评结论+传播风险
│   └── *.md                    # 深度数据文件（横评档案等）
├── laptops/                     # 笔记本品类
│   ├── _index.md               # 品牌矩阵+价位段+平台阵营+传播风险
│   └── *.md                    # 深度数据文件（年度翻车案例等）
├── wearables/                   # 穿戴设备
│   └── _index.md               # 品牌矩阵+价位段+功能阵营+传播风险
├── smart-home/                  # 智能家居
│   └── _index.md               # 品牌矩阵+价位段+品类核心结论
├── other/                       # 其他3C品类
│   └── _index.md               # 品类优先级+覆盖计划
├── ecosystem/                   # 行业生态
│   ├── kols.md                  # KOL/UP主名单（按品类和平台）
│   └── industry-memes.md        # 行业黑话/梗字典+慎用清单
├── references/                  # 参考文档（Agent指令+框架）
│   ├── comment-personas.md      # 评论区人群原型+模拟规则
│   ├── industry-ecosystem.md    # 5平台传播规律+品类适配
│   ├── eco-integration.md       # 外部工具集成协议
│   ├── subagent-dataprocessor.md # DataProcessor 指令
│   └── subagent-factchecker.md  # FactChecker 指令
├── templates/                   # 输出模板
│   ├── creative-output.md       # 创意策划模板
│   ├── insight-output.md        # 洞察/竞品/横评模板
│   ├── risk-assessment.md       # 风险评估模板
│   ├── new-category-playbook.md # 新品类破局模板
│   ├── quality-check-tools.md   # 去AI化+事实核查+自检
│   ├── used-ideas.md            # 已使用创意去重记录（运行时维护）
│   └── knowledge-base-structure.md # 本文件
└── scripts/
    └── preprocess.py            # 数据预处理脚本
```

## 品类 _index.md 标准结构

每个品类的 `_index.md` 必须包含以下5个板块：

```markdown
# {品类名}品类品牌矩阵

> 数据来源：{评测机构/视频标题（年份）}
> 覆盖范围：{N}个品牌，{N}份评测数据

## 品牌矩阵
| 品牌 | 核心定位 | 代表系列 | 价位段 | 技术标签 |

## 价位段格局
### ¥{范围}（{定位}）
- **特点**: ...
- **代表**: ...
- **关键卖点/参数**: ...

## 核心{芯片/平台/功能}阵营
| 芯片/平台 | 定位 | 代表机型 | 特点 |

## 品类核心结论
1. ...
2. ...

## 传播风险提示
- **"{风险话术}"**: {为什么危险，怎么改}
```

## 品类扩展规范

当某个品类数据增长后，在品类目录下创建子文件：

```
{品类}/
├── _index.md                    # 品类总览（必须）
├── {细分数据文件}.md            # 如横评、年度总结等深度数据
└── brand-{品牌名}/              # 当品牌数据足够多时
    ├── spec.md                  # 规格参数
    ├── reviews.md               # 评测摘要
    ├── comments.md              # 评论区精华
    └── risks.md                 # 风险/负面点
```

**何时创建品牌子目录**：当一个品牌有3+款产品、且有2+个评测来源时。

## 横向文件规范

### ecosystem/kols.md
按品类分组，每个KOL标注：平台、粉丝量级、风格标签、恰饭风险、注意事项。

### ecosystem/industry-memes.md
按品类分组，每个梗标注：含义、来源/用法、风险提示/可用性。

### references/comment-personas.md
通用人群原型框架，各品类可在自己的知识库数据中提炼具体变体。

## 更新纪律

- 数据导入后更新对应品类的 `_index.md`
- 新增KOL/梗后更新 `ecosystem/` 对应文件
- 每次更新在文件顶部更新记录中标注日期和来源
- 版本号仅在 `SKILL.md` front matter 维护（`metadata.openclaw.version`），子文件不重复声明
