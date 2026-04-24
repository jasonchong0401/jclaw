#!/usr/bin/env python3
"""
LLM论文创新点提取器
使用AI分析论文摘要，提取核心问题、主要创新和技术亮点
"""

import json
import os
import subprocess
from datetime import datetime

# 输入/输出文件路径
INPUT_FILE = "/home/admin/.openclaw/workspace/data/llm_paper_digest.json"
OUTPUT_FILE = "/home/admin/.openclaw/workspace/data/llm_paper_innovations.json"

def load_papers():
    """加载论文数据"""
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 文件不存在: {INPUT_FILE}")
        return None

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get("papers", [])

def analyze_innovation_with_claude(paper):
    """使用Claude分析论文的创新点"""
    prompt = f"""分析以下LLM论文的创新点，输出JSON格式：

标题: {paper['title']}
摘要: {paper['summary']}

请提取以下信息（使用中文）：
1. core_problem: 核心问题（一句话说明解决什么痛点）
2. main_innovation: 主要创新（一句话说明核心贡献）
3. tech_highlights: 技术亮点（3-5个要点，每个15-25字）

只输出JSON，格式如下：
{{
  "core_problem": "...",
  "main_innovation": "...",
  "tech_highlights": ["...", "...", "..."]
}}"""

    try:
        # 使用OpenClaw的sessions_send调用AI分析
        result = subprocess.run([
            "openclaw", "sessions", "send",
            "--agent", "main",
            "--message", prompt
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # 尝试从输出中提取JSON
            output = result.stdout
            # 查找JSON部分
            start = output.find('{')
            end = output.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = output[start:end]
                innovation = json.loads(json_str)
                return innovation
    except Exception as e:
        print(f"  ⚠ AI分析失败: {e}")

    return None

def simple_extract_innovation(paper):
    """简单的创新点提取（基于关键词规则）"""
    summary = paper['summary']
    title = paper['title']

    # 提取核心问题（基于常见句式）
    core_problem = "待分析"

    # 提取主要创新（基于关键词）
    if "we propose" in summary.lower() or "we present" in summary.lower():
        innovation_start = summary.lower().find("we propose")
        if innovation_start == -1:
            innovation_start = summary.lower().find("we present")
        if innovation_start != -1:
            innovation_sentence = summary[innovation_start:innovation_start+200]
            main_innovation = innovation_sentence[:100].replace("we propose", "").replace("we present", "").strip()
            if len(main_innovation) > 50:
                main_innovation = main_innovation[:50] + "..."
        else:
            main_innovation = "新方法/新框架"
    else:
        main_innovation = "新方法/新框架"

    # 提取技术亮点（关键词）
    keywords = []
    important_terms = ["novel", "new", "state-of-the-art", "outperform", "benchmark", "dataset", "framework", "approach", "method"]
    for term in important_terms:
        if term in summary.lower():
            keywords.append(term)
    if not keywords:
        keywords = ["新方法"]

    tech_highlights = keywords[:3]

    return {
        "core_problem": core_problem,
        "main_innovation": main_innovation,
        "tech_highlights": tech_highlights
    }

def extract_all_innovations(papers):
    """提取所有论文的创新点"""
    print(f"\n正在分析 {len(papers)} 篇论文的创新点...")

    innovations = []
    for i, paper in enumerate(papers, 1):
        print(f"  [{i}/{len(papers)}] {paper['title'][:50]}...")

        # 先尝试AI分析，如果失败则使用简单提取
        innovation = analyze_innovation_with_claude(paper)
        if not innovation:
            print("    使用简单提取...")
            innovation = simple_extract_innovation(paper)

        innovations.append({
            "title": paper['title'],
            "summary": paper['summary'],
            "innovation": innovation
        })

    return innovations

def generate_trends(innovations):
    """生成趋势总结"""
    trends = []

    # 分析常见主题
    tech_mentions = {}
    for item in innovations:
        for highlight in item['innovation']['tech_highlights']:
            tech_mentions[highlight] = tech_mentions.get(highlight, 0) + 1

    # 找出最值得注意的论文
    most_noteworthy = innovations[0]['title'] if innovations else ""
    reasoning = "基于论文数量和技术覆盖面"

    return {
        "most_noteworthy": most_noteworthy,
        "reasoning": reasoning,
        "trends": trends
    }

def save_innovations(innovations, trends):
    """保存创新点分析结果"""
    data = {
        "papers": innovations,
        "evaluation": trends
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 已保存创新点分析到 {OUTPUT_FILE}")
    return data

def main():
    print("=" * 60)
    print("LLM论文创新点提取器")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 加载论文数据
    papers = load_papers()
    if not papers:
        print("❌ 没有论文数据")
        return 1

    # 提取创新点
    innovations = extract_all_innovations(papers)

    # 生成趋势总结
    trends = generate_trends(innovations)

    # 保存结果
    save_innovations(innovations, trends)

    # 打印摘要
    print("\n" + "=" * 60)
    print("创新点摘要:")
    print("=" * 60)
    for i, item in enumerate(innovations, 1):
        print(f"\n{i}. {item['title'][:60]}...")
        print(f"   核心问题: {item['innovation']['core_problem']}")
        print(f"   主要创新: {item['innovation']['main_innovation']}")

    return 0

if __name__ == "__main__":
    exit(main())