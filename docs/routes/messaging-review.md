# 信息架构与话术审核路由

## 触发

用户要求定位、标语、核心主张、平台文案、KOL口播、发布会话术、AI卖点改写或广告语风险。

## 读取顺序

1. `docs/templates/message-house.md`
2. `docs/templates/quality-check-tools.md`
3. `docs/ecosystem/industry-memes.md`
4. 需要上线判断时读 `docs/templates/execution-readiness-gate.md`
5. 涉及上市总路线时读 `docs/routes/launch-decision.md`

## 默认输出

- 直接回答原表达能否使用，并给出改写结果。
- 1-3个替代表达；用户指定数量或只要一句时按要求交付。
- 支撑改写的证据缺口、禁用表达和关键风险。
- 用户要求“信息屋”时，再展开核心主张、三组证据柱、反对意见和多平台口径。
- 用户要求压力测试或正式上线审核时，再展开三类评论压力测试。

## 纪律

- 高时效数字、排名、价格和新品参数未核验时标注 `[待验证]`。
- AI主张必须落到具体任务、结果和不可用边界。
- 绝对化表达缺少证据时降级为风险提示和替代表达。
