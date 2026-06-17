#!/usr/bin/env python3
"""
3C营销策划 Skill — 数据预处理脚本
用法: python scripts/preprocess.py --input <文件> --type <评测|评论|规格|风险> --category <品类>
"""
import argparse
import json
import re
import sys
from pathlib import Path

# 品类专属纠错字典（key与目录名一致）
CORRECTION_DICTS = {
    "mobile": {
        "晓龙": "骁龙", "发哥": "联发科/天玑", "蓝厂": "vivo", "绿厂": "OPPO",
        "粗粮": "小米", "冰龙": "散热好的骁龙", "火龙": "发热严重的骁龙",
        "果子": "苹果", "海军": "华为粉丝", "降维打击": "跨价位竞争",
        "挤牙膏": "小幅升级", "机圈肖战": "争议极大的品牌/人物",
    },
    "laptops": {
        "满血": "满功耗", "残血": "低功耗版", "核显": "集成显卡",
        "独显直连": "显卡直连", "PD充电": "USB-PD充电",
        "三低屏": "低色域+低刷+低亮度", "武装直升机": "噪音极大的游戏本",
        "马甲U": "架构不变的换名CPU", "液金": "液态金属散热",
    },
    "headphones": {
        "听个响": "音质一般", "底噪": "背景噪声", "听感": "主观音质评价",
        "三频": "低频/中频/高频", "声场": "声音空间感",
        "木耳": "听不出音质区别", "金耳朵": "能听出细微差异",
        "白开水": "调音平淡均衡", "动次打次": "低频过量",
    },
    "wearables": {
        "全天候显示": "AOD", "血氧": "血氧饱和度", "ECG": "心电图",
        "测血压": "血压趋势估算（非医疗器械）", "测血糖": "无创血糖监测（争议大）",
    },
    "smart-home": {
        "全家桶": "同品牌全系列产品", "联动": "设备间自动协作",
        "Matter": "智能家居统一协议", "前装": "装修时预装",
        "后装": "已入住后加装",
    },
}

LEVEL_ORDER = {"低": 1, "中": 2, "高": 3}
RULES_PATH = Path(__file__).resolve().parent.parent / "docs" / "ecosystem" / "negative-signal-rules.json"
DOCUMENT_PATH_MARKERS = (
    "README.md",
    "quickstart-example.md",
    "docs/templates/",
    "docs/references/",
    "docs/ecosystem/",
)

def load_file(filepath):
    """读取原始数据文件"""
    p = Path(filepath)
    if not p.exists():
        print(f"错误: 文件不存在 {filepath}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")

def apply_corrections(text, category):
    """应用纠错字典"""
    corrections = CORRECTION_DICTS.get(category, {})
    correction_count = sum(text.count(wrong) for wrong in corrections)
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text, correction_count

def detect_type(text):
    """自动检测数据类型"""
    signals = {
        "评测": ["测评", "评测", "上手", "体验", "测试", "拆解"],
        "评论": ["评论", "弹幕", "吐槽", "评价", "用户说"],
        "规格": ["参数", "规格", "配置", "跑分", "处理器"],
        "风险": ["翻车", "负面", "问题", "缺陷", "最差"],
    }
    scores = {}
    for dtype, keywords in signals.items():
        scores[dtype] = sum(1 for kw in keywords if kw in text)
    if max(scores.values()) == 0:
        return "评测"  # 默认
    return max(scores, key=scores.get)

def infer_mode(args, dtype):
    """推断内容类型，降低把知识库文档误判成评论负面的概率。"""
    if args.mode != "auto":
        return args.mode
    rel = str(Path(args.input)).replace("\\", "/")
    if any(marker in rel for marker in DOCUMENT_PATH_MARKERS):
        return "document"
    if dtype == "评论":
        return "comments"
    if dtype == "风险":
        return "campaign"
    return "review"

def clean_text(text):
    """清理字幕时间戳、连续空行和首尾空白，保留原始表达。"""
    text = re.sub(r"\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}\s*-->\s*\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}", "", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_numbers(text):
    """提取常见数值线索，供人工复核。"""
    pattern = r"\d+(?:\.\d+)?\s*(?:元|万|亿|%|Hz|W|mAh|dB|小时|分钟|GB|TB|英寸|克|kg|fps|分)"
    return sorted(set(re.findall(pattern, text)))

def split_segments(text):
    """切分文本片段，保留足够上下文用于负面样本。"""
    return [part.strip() for part in re.split(r"[。！？!?；;\n]+", text) if part.strip()]

def markdown_cell(text):
    """转义 Markdown 表格单元格。"""
    return text.replace("|", "\\|").replace("\n", " ").strip()

def load_negative_signal_rules(category):
    """读取机器可维护的负面信号规则库。"""
    try:
        raw = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"警告: 无法读取负面规则库 {RULES_PATH}: {exc}", file=sys.stderr)
        return []

    rules = []
    for rule in raw.get("global", []):
        if rule.get("name") and rule.get("keywords"):
            rules.append(rule)
    for rule in raw.get("categories", {}).get(category, []):
        if rule.get("name") and rule.get("keywords"):
            rules.append(rule)
    return rules

def detect_negative_signals(text, category, mode):
    """根据离线规则识别负面早期信号。"""
    if mode == "document":
        return []
    rules = load_negative_signal_rules(category)
    segments = split_segments(text)
    results = []
    for rule in rules:
        name = rule["name"]
        keywords = rule.get("keywords", [])
        hits = []
        total = 0
        for keyword in keywords:
            count = text.count(keyword)
            if count == 0:
                continue
            total += count
            for segment in segments:
                if keyword in segment:
                    sample = segment[:120]
                    if sample not in hits:
                        hits.append(sample)
                    break
        if total == 0:
            continue
        level = rule.get("base_level", "中")
        boost_count = int(rule.get("boost_count_gte", 3))
        if total >= boost_count and LEVEL_ORDER[level] < LEVEL_ORDER["高"]:
            level = "高"
        results.append({
            "name": name,
            "level": level,
            "count": total,
            "samples": hits[:3],
            "action": rule.get("action", "人工复核该负面信号。"),
        })

    return sorted(
        results,
        key=lambda item: (-LEVEL_ORDER[item["level"]], -item["count"], item["name"]),
    )

def render_markdown(args, dtype, text, correction_count):
    mode = infer_mode(args, dtype)
    numbers = extract_numbers(text)
    negative_signals = detect_negative_signals(text, args.category, mode)
    title = args.title or Path(args.input).stem
    source = args.source or "未标注"

    lines = [
        f"# {title}",
        "",
        f"> 品类: {args.category}",
        f"> 数据类型: {dtype}",
        f"> 内容模式: {mode}",
        f"> 来源: {source}",
        "> 状态: [待复核]",
        "",
        "## 处理摘要",
        "",
        f"- 原文长度: {len(text)} 字符",
        f"- 纠错命中: {correction_count} 处",
        f"- 数值线索: {len(numbers)} 个",
        f"- 负面早期信号: {len(negative_signals)} 类",
        "",
        "## 数值线索",
        "",
    ]
    if numbers:
        lines.extend(f"- {item} — 来源: [{source}] — 状态: [待验证]" for item in numbers[:80])
    else:
        lines.append("- 未发现明显数值线索")

    lines.extend([
        "",
        "## 负面早期预警",
        "",
    ])
    if negative_signals:
        lines.extend([
            "| 信号 | 等级 | 命中 | 样本 | 建议动作 |",
            "|------|------|------|------|----------|",
        ])
        for signal in negative_signals:
            sample = " / ".join(signal["samples"]) if signal["samples"] else "需人工复核"
            lines.append(
                f"| {markdown_cell(signal['name'])} | {signal['level']} | {signal['count']} | {markdown_cell(sample)} | {markdown_cell(signal['action'])} |"
            )
        lines.extend([
            "",
            "### 优先处理",
            "",
        ])
        for signal in negative_signals[:3]:
            lines.append(f"- {signal['name']}: {signal['action']}")
    else:
        if mode == "document":
            lines.append("- 当前内容模式为 document，已跳过关键词式负面预警，避免把说明文档误判为真实评论。")
        else:
            lines.append("- 未发现明显负面早期信号；仍需人工复核高风险话术和关键数据。")

    lines.extend([
        "",
        "## 清洗后原文",
        "",
        text,
        "",
    ])
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="3C数据预处理")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--type", choices=["评测", "评论", "规格", "风险"], help="数据类型（可省略，自动检测）")
    parser.add_argument("--category", required=True, choices=list(CORRECTION_DICTS.keys()), help="品类")
    parser.add_argument("--output", help="输出文件路径（默认打印到stdout）")
    parser.add_argument("--source", help="来源标注，例如 KOL|平台|标题")
    parser.add_argument("--title", help="输出文档标题")
    parser.add_argument("--mode", choices=["auto", "comments", "review", "campaign", "document"], default="auto", help="内容模式，默认自动判断")
    args = parser.parse_args()

    text = load_file(args.input)
    text = clean_text(text)
    text, correction_count = apply_corrections(text, args.category)

    dtype = args.type or detect_type(text)

    output = render_markdown(args, dtype, text, correction_count)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"已保存到: {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
