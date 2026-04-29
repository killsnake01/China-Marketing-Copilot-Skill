#!/usr/bin/env python3
"""
3C营销策划 Skill — 数据预处理脚本
用法: python scripts/preprocess.py --input <文件> --type <评测|评论|规格|风险> --category <品类>
"""
import argparse
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
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text

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

def main():
    parser = argparse.ArgumentParser(description="3C数据预处理")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--type", choices=["评测", "评论", "规格", "风险"], help="数据类型（可省略，自动检测）")
    parser.add_argument("--category", required=True, choices=list(CORRECTION_DICTS.keys()), help="品类")
    parser.add_argument("--output", help="输出文件路径（默认打印到stdout）")
    args = parser.parse_args()

    text = load_file(args.input)
    text = apply_corrections(text, args.category)

    dtype = args.type or detect_type(text)

    print(f"品类: {args.category}")
    print(f"类型: {dtype}")
    print(f"原文长度: {len(text)} 字符")

    # 统计纠错次数（简单版本）
    corrections = CORRECTION_DICTS.get(args.category, {})
    correction_count = 0
    for wrong in corrections:
        # 这里无法精确统计（已经替换了），只是示意
        pass
    print(f"纠错字典: {len(corrections)} 条")

    print("\n--- 清洗后内容预览 ---")
    print(text[:500])

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"\n已保存到: {args.output}")

if __name__ == "__main__":
    main()
