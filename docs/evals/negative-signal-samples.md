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
| C009 | comments | mobile | 这相机说得神乎其神，结果夜景涂抹严重，鬼影也没解决。 | 手机性能/影像风险 | 价格背刺 |
| C010 | comments | mobile | 发布会说续航无敌，实际断流加杀后台，体验很割裂。 | 手机性能/影像风险 | KOL背叛 |
| C011 | comments | mobile | 又说跑分第一，数据哪来的，同源对比有没有？ | 数据打脸 | 价值观冒犯 |
| C012 | comments | mobile | 首发价刚买就国补叠券，晚买享折扣，老用户心态崩了。 | 价格背刺 | 产品缺陷 |
| C013 | comments | mobile | 这条评论区全是夸的，像水军刷出来，还删评。 | 信任崩塌 | AI空话 |
| C014 | comments | mobile | AI助手听起来很鸡肋，像套壳功能，没说清能少做哪一步。 | AI空话 | 产品缺陷 |
| C015 | comments | mobile | 这次价值观翻车吧，文案看着低俗，还带点歧视。 | 价值观冒犯 | 价格背刺 |
| C016 | comments | mobile | 官方找这种骂粉丝的KOL站台，核心用户真的会觉得被背叛。 | KOL背叛 | 数据打脸 |
| C017 | comments | headphones | 这耳机底噪明显，左右不同步，通勤风噪也压不住。 | 耳机体验风险 | 价格背刺 |
| C018 | comments | headphones | 音质闷又刺耳，低频糊成一团，还说自己调音旗舰。 | 耳机体验风险 | KOL背叛 |
| C019 | comments | headphones | 夹耳夹到疼，漏音旁边都能听见，办公室不敢戴。 | 耳机体验风险、产品缺陷 | 价值观冒犯 |
| C020 | comments | headphones | 首发价太硬了，等降价吧，反正耳机跳水很快。 | 价格背刺 | 耳机体验风险 |
| C021 | comments | headphones | 评测里只说优点，恰饭感太重，像硬广。 | 信任崩塌 | 产品缺陷 |
| C022 | comments | laptops | 说满功耗，结果功耗墙锁得死，降频后帧率掉得厉害。 | 笔记本配置/散热风险 | 价值观冒犯 |
| C023 | comments | laptops | 这个屏幕又是三低屏，硬盘还是QLC，配置表写得太绕。 | 笔记本配置/散热风险 | KOL背叛 |
| C024 | comments | laptops | 宣传跑分第一，实际插电和不插电差很多，测试条件呢？ | 数据打脸 | 价值观冒犯 |
| C025 | comments | laptops | 风扇吵、发热、卡顿全来了，这也能叫创作本？ | 产品缺陷、笔记本配置/散热风险 | 价格背刺 |
| C026 | comments | laptops | 刚买完就补贴加码，首发用户又成冤种。 | 价格背刺 | 产品缺陷 |
| C027 | comments | smart-home | 扫地机越拖越脏，毛发缠绕也没解决，别再说解放双手。 | 智能家居体验/隐私风险 | KOL背叛 |
| C028 | comments | smart-home | 自动上下水宣传得太轻松，我家根本没法装。 | 智能家居体验/隐私风险 | 价格背刺 |
| C029 | comments | smart-home | 摄像头隐私和地图数据怎么处理，页面里完全没讲。 | 智能家居体验/隐私风险 | AI空话 |
| C030 | comments | smart-home | 撞家具撞得很频繁，还说AI避障，感觉就是PPT功能。 | 智能家居体验/隐私风险、AI空话 | KOL背叛 |
| C031 | comments | smart-home | 全屋智能套餐涨价太多，国补口径也没说清楚。 | 价格背刺 | 产品缺陷 |
| C032 | comments | wearables | GPS飘得离谱，跑步轨迹都进河里了。 | 穿戴健康/续航风险 | 信任崩塌 |
| C033 | comments | wearables | 心率飘、血氧测不准，还暗示能守护健康，太误导。 | 穿戴健康/续航风险 | 价格背刺 |
| C034 | comments | wearables | 一天一充还说全天候，续航测试条件写清楚了吗？ | 穿戴健康/续航风险、数据打脸 | KOL背叛 |
| C035 | comments | wearables | 这文案拿健康焦虑做卖点，看着不舒服。 | 价值观冒犯 | 价格背刺 |
| C036 | comments | wearables | 手表涨价后功能没变化，等降价更稳。 | 价格背刺 | 产品缺陷 |
| C037 | comments | mobile | 说影像领先可以，别拍月亮又出争议，同源测试样张给全一点。 | 手机性能/影像风险、数据打脸 | 价值观冒犯 |
| C038 | comments | mobile | 充电功率写得很大，实际发热明显，后半程降速也没说，测试条件呢？ | 产品缺陷、数据打脸 | KOL背叛 |
| C039 | comments | headphones | 降噪说得很满，地铁风噪还是明显，实测呢？ | 耳机体验风险、数据打脸 | 价值观冒犯 |
| C040 | comments | laptops | 马甲U换个名字又来卖，宣传页还不写清楚架构，像硬广。 | 笔记本配置/散热风险、信任崩塌 | 价值观冒犯 |
| D001 | document | mobile | 本模板用于识别翻车、恰饭、控评等风险。 | 无 | 产品缺陷、信任崩塌 |
| D002 | document | mobile | 示例：用户可能说“实测呢？测试条件是什么？” | 无 | 数据打脸 |
| D003 | document | headphones | 本段说明夹耳、漏音、风噪等样本如何用于规则校准。 | 无 | 耳机体验风险、产品缺陷 |
| D004 | document | laptops | 本模板会提到功耗墙、三低屏、QLC等笔记本风险词。 | 无 | 笔记本配置/散热风险 |
| D005 | document | smart-home | 示例包含自动上下水、摄像头隐私、地图数据等词。 | 无 | 智能家居体验/隐私风险 |
| D006 | document | wearables | 本说明列举医疗器械、心率飘、一天一充等典型风险。 | 无 | 穿戴健康/续航风险 |
| R001 | review | mobile | 长时间游戏后机身发热明显，出现降频和掉帧。 | 产品缺陷、手机性能/影像风险 | KOL背叛 |
| R002 | review | headphones | 实测显示通勤场景风噪明显，佩戴久了有夹耳反馈。 | 耳机体验风险 | 价格背刺 |
| R003 | review | laptops | 高负载下出现功耗墙，风扇吵，键盘区域发热明显。 | 笔记本配置/散热风险、产品缺陷 | 价值观冒犯 |
| R004 | review | smart-home | 清洁测试中出现毛发缠绕和边角遗漏，避障偶尔撞家具。 | 智能家居体验/隐私风险 | KOL背叛 |
| R005 | review | wearables | 连续运动测试里GPS飘，心率飘，续航也低于标称。 | 穿戴健康/续航风险 | 信任崩塌 |
| R006 | review | mobile | 影像样张存在偏色和涂抹，游戏场景出现锁帧。 | 手机性能/影像风险 | 价格背刺 |
| P001 | campaign | mobile | 主文案计划写“跑分第一，AI全面重塑体验”。 | 数据打脸、AI空话 | 产品缺陷 |
| P002 | campaign | mobile | 预热视频准备绑定母亲节反差梗，标题里有一点冒犯式幽默。 | 价值观冒犯 | 价格背刺 |
| P003 | campaign | headphones | KOL口播准备写“全场景无漏音，通勤风噪全消失”，但没有测试条件。 | 耳机体验风险、数据打脸 | KOL背叛 |
| P004 | campaign | laptops | 海报准备写“跑分第一，唯一满血旗舰，所有游戏满帧”，但没讲功耗墙测试。 | 数据打脸、笔记本配置/散热风险 | 价值观冒犯 |
| P005 | campaign | smart-home | 传播主张准备写“买回家直接自动上下水，全屋都适用”。 | 智能家居体验/隐私风险 | KOL背叛 |
| P006 | campaign | wearables | 商品页准备写“全天候守护健康，血氧心率随时准确”，但没有测试条件，还容易被问算不算医疗器械。 | 穿戴健康/续航风险、数据打脸 | 信任崩塌 |

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
