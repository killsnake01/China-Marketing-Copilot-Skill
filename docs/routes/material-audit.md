# 正式物料审核路由

## 触发

用户提供广告、发布会PPT、官网/电商详情页、KOL Brief、微博文案、口播稿、商品页标题或要求“帮我审核”。

## 读取顺序

1. `docs/references/subagent-factchecker.md`
2. `docs/templates/quality-check-tools.md`
3. `docs/templates/risk-assessment.md`
4. `docs/templates/message-house.md`
5. 涉及评论区或上线判断时读 `docs/templates/execution-readiness-gate.md`

## 必备输出

- 问题项、风险等级、依据和替代表达。
- 未验证事实清单。
- 绝对化、对比、价格、权益、KOL合作和AI主张检查。
- 评论区压力测试。
- 上线结论：直接执行、调整后执行或暂停重做。

## 纪律

- 无法证明的主张直接标注，不替用户抹平。
- 对外物料涉及高风险词时给替代表达。
- 未核验关键事实时，结论不能写 `直接执行`。
