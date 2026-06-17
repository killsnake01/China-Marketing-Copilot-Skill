# 负面信号识别样本集

> 用途：校准 `scripts/preprocess.py` 和 `docs/ecosystem/negative-signal-rules.json`，避免误报和漏报。
> 使用方式：人工或脚本把样本文本喂给 `preprocess.py`，对比期望信号。

## 评估原则

- 同一个关键词在不同内容模式下含义不同。`document` 模式应减少误报，`comments` 模式应提高敏感度。
- 优先识别能被截图传播、能被实测复现、能触发用户利益或价值观争议的负面。
- 不要求关键词命中越多越好；更重要的是“该不该提醒”和“优先处理顺序是否正确”。

## 样本表

| ID | 模式 | 品类 | 样本文本 | 期望识别 | 不应识别 |
|----|------|------|----------|----------|----------|
| C001 | comments | mobile | 首发买的真成首发冤种了，618要是跳水就背刺。续航说得太满了，实测呢？测试条件写清楚了吗？ | 价格背刺、数据打脸 | 价值观冒犯 |
| C002 | comments | mobile | 这条看起来太像软广，评论区还控评。AI功能感觉是PPT功能，实际场景没说清。 | 信任崩塌、AI空话 | 产品缺陷 |
| C003 | comments | headphones | 戴半小时夹耳，风噪压不住，漏音也明显。 | 耳机体验风险、产品缺陷 | 价格背刺 |
| C004 | comments | laptops | 这个本看着是满血，结果跑不满，风扇吵得像武装直升机。 | 笔记本配置/散热风险 | 价值观冒犯 |
| C005 | comments | smart-home | 自动上下水不适合我家，摄像头隐私也没说清楚。 | 智能家居体验/隐私风险 | KOL背叛 |
| C006 | comments | wearables | 血氧和心率飘得离谱，这能算医疗器械吗？ | 穿戴健康/续航风险 | 信任崩塌 |
| C007 | comments | mobile | 这个KOL以前骂用户，现在官方还给黑粉送钱？ | KOL背叛 | AI空话 |
| C008 | comments | mobile | 母亲节这种文案真的不尊重人，看着很不舒服。 | 价值观冒犯 | 价格背刺 |
| D001 | document | mobile | 本模板用于识别翻车、恰饭、控评等风险。 | 无 | 产品缺陷、信任崩塌 |
| D002 | document | mobile | 示例：用户可能说“实测呢？测试条件是什么？” | 无 | 数据打脸 |
| R001 | review | mobile | 长时间游戏后机身发热明显，出现降频和掉帧。 | 产品缺陷、手机性能/影像风险 | KOL背叛 |
| P001 | campaign | mobile | 主文案计划写“跑分第一，AI全面重塑体验”。 | 数据打脸、AI空话 | 产品缺陷 |

## 当前已知短板

- 关键词规则无法判断语气，有些反讽和引用需要人工复核。
- `document` 模式会跳过负面识别，适合说明文档；如果要扫描方案文本，应使用 `campaign`。
- 真实平台评论会有错别字、谐音和表情包，需要持续扩充规则。

## 推荐测试命令

```bash
python3 -B scripts/preprocess.py --input /path/to/comments.txt --category mobile --type 评论 --mode comments
python3 -B scripts/preprocess.py --input quickstart-example.md --category mobile --mode document
python3 -B scripts/evaluate_negative_signals.py
```
