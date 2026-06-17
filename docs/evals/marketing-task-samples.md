# 营销任务评测集

> 用途：校准本技能包在真实中国3C营销任务中的执行质量。评测时把“用户输入”作为任务，把“应读取”作为最低上下文要求，把“必备输出”和“通过标准”作为人工或脚本评分依据。

## 评分规则

每个样本按 0-2 分评分，总分 10 分。

| 维度 | 0分 | 1分 | 2分 |
|------|-----|-----|-----|
| 路由准确 | 路由偏离任务 | 读取了部分相关文件 | 读取了应读取文件并解释用途 |
| 事实纪律 | 编造或无标注 | 有少量未标注推断 | 数字、来源、缺口均有标注 |
| 策略判断 | 只有泛泛建议 | 有结论但取舍较弱 | 有推荐路线、备选路线和弃用路线 |
| 风险识别 | 漏掉主要风险 | 识别风险但动作不清 | 给出负面早期信号、严重度和动作 |
| 可执行性 | 输出难落地 | 有行动但粒度不足 | 给出 72 小时动作、7 天跟进或明确交付物 |

通过线：
- 8 分及以上：通过。
- 6-7 分：需人工复核后使用。
- 5 分及以下：需要重做。

## 样本表

| ID | 任务类型 | 品类 | 用户输入 | 应读取 | 必备输出 | 主要风险 | 通过标准 |
|----|----------|------|----------|--------|----------|----------|----------|
| M001 | 策略诊断 | mobile | 我们有一台影像旗舰，预算有限，上市前7天怎么打？ | docs/templates/strategy-decision-system.md; docs/data-index.md; knowledge-base/mobile/_index.md | 推荐路线、备选路线、弃用路线、72小时动作、7天跟进 | 参数党拆解、竞品影像反击 | 有清晰路线取舍，所有影像主张标注来源或待验证 |
| M002 | 信息架构 | mobile | 把“AI影像旗舰”改成更像中国数码圈能接受的话术。 | docs/templates/message-house.md; docs/templates/quality-check-tools.md; docs/ecosystem/industry-memes.md | 核心主张、三条证据柱、禁用表达、平台文案 | AI空话、通稿腔 | 话术落到具体场景，并提示需补证据字段 |
| M003 | 渠道KOL | mobile | 新机评测解禁当天，KOL和评论区怎么排？ | docs/templates/channel-kol-activation.md; docs/ecosystem/kols.md; docs/references/industry-ecosystem.md | 平台分工、KOL类型、交付件、评论区动作、复盘指标 | KOL可信度、控评质疑 | 区分爆料、横评、体验向角色，并给评论区预案 |
| M004 | 风险评估 | mobile | 文案想写“跑分第一，AI全面重塑体验”，会翻车吗？ | docs/templates/risk-assessment.md; docs/ecosystem/negative-early-warning.md; docs/templates/quality-check-tools.md | 风险评分、模拟评论、替代表达、动作建议 | 数据打脸、AI空话 | 识别绝对化和AI空话，给出更稳表达 |
| M005 | 竞品洞察 | headphones | 两款耳夹式耳机都说佩戴舒服，应该怎么判断谁更适合种草？ | docs/templates/insight-output.md; knowledge-base/headphones/_index.md; knowledge-base/headphones/clip-earphones-comparison-2026.md | 一句话结论、同源数据矩阵、人群拆分、种草建议 | 主观听感泛化 | 明确同源横评优先，并区分佩戴、漏音、风噪 |
| M006 | 创意策划 | headphones | 帮开放式耳机想3个小红书创意，别像广告。 | docs/templates/creative-output.md; docs/templates/message-house.md; docs/references/comment-personas.md; knowledge-base/headphones/_index.md | 3个创意、核心钩子、平台表达、评论区模拟 | 佩戴争议、漏音质疑 | 创意来自真实痛点，并附负面反应 |
| M007 | 风险评估 | laptops | 游戏本新品想打“满血性能”，评论区会怎么拆？ | docs/templates/risk-assessment.md; knowledge-base/laptops/_index.md; knowledge-base/laptops/annual-negative-awards-2025.md | 风险维度、参数党评论、补证据清单 | 功耗墙、散热、三低屏 | 输出功耗、散热、屏幕和测试条件检查项 |
| M008 | 信息架构 | laptops | 轻薄本怎么讲“办公效率”，别空泛。 | docs/templates/message-house.md; docs/templates/strategy-decision-system.md; knowledge-base/laptops/_index.md | 核心主张、证据柱、场景话术、禁用表达 | 生产力空话 | 场景具体到会议、续航、接口、重量或屏幕 |
| M009 | 新品类破局 | wearables | 健康手表新品用户觉得测不准，传播怎么破？ | docs/templates/new-category-playbook.md; docs/templates/risk-assessment.md; knowledge-base/wearables/_index.md | 品类认知诊断、破局方法、风险边界、验证动作 | 医疗器械误导、健康焦虑 | 明确健康监测边界，并避免医疗承诺 |
| M010 | 风险评估 | wearables | 想写“全天候守护健康”，有什么问题？ | docs/templates/risk-assessment.md; docs/ecosystem/negative-early-warning.md; knowledge-base/wearables/_index.md | 风险等级、改写建议、评论区模拟 | 健康误导、续航质疑 | 输出限制条件和更稳表达 |
| M011 | 竞品洞察 | smart-home | 扫地机器人新品强调自动上下水，哪些家庭会反感？ | docs/templates/insight-output.md; knowledge-base/smart-home/_index.md; knowledge-base/smart-home/robot-vacuum-comparison-2025.md | 人群拆分、限制条件、传播建议 | 安装门槛、隐私、维护 | 明确户型和安装条件，避免无门槛承诺 |
| M012 | 创意策划 | smart-home | 智能家居全屋方案怎么讲，用户才不觉得是在卖套餐？ | docs/templates/creative-output.md; docs/templates/strategy-decision-system.md; knowledge-base/smart-home/_index.md | 创意方向、用户障碍、场景脚本、风险提示 | 生态锁定、价格门槛 | 输出从生活场景进入的创意，并标注成本边界 |
| M013 | 负面预警 | mobile | 评论区开始说“首发冤种、晚买享折扣”，怎么处理？ | docs/ecosystem/negative-early-warning.md; docs/templates/risk-assessment.md; docs/ecosystem/market-signals-2026.md | 信号等级、即时动作、客服口径、7天观察指标 | 价格背刺 | 给出渠道、日期、补贴条件和首发权益处理 |
| M014 | 正式审核 | mobile | 发布会PPT里有“唯一、第一、遥遥领先”，帮我审核。 | docs/references/subagent-factchecker.md; docs/templates/quality-check-tools.md; docs/templates/risk-assessment.md | 问题项、未验证项、替代表达、结论 | 绝对化、广告合规 | 逐条标出高风险词，并要求证据或改写 |
| M015 | 数据导入 | headphones | 我导入了一批耳机评论，先找负面苗头再总结卖点。 | docs/references/subagent-dataprocessor.md; docs/ecosystem/negative-early-warning.md; docs/evals/negative-signal-samples.md | 负面信号、原文样本、正面发现、入库建议 | 夹耳、漏音、风噪 | 先负面后正面，保留原话和来源标签 |
| M016 | 平台兼容 | other | OpenClaw没有浏览器能力，还能做新品类策略吗？ | SKILL.md; docs/data-index.md; docs/references/eco-integration.md; docs/templates/new-category-playbook.md | 离线路径、缺口标注、需用户补充材料 | 外部实时数据缺失 | 说明可离线使用，并列出要用户补充的材料 |
