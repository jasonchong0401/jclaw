#!/usr/bin/env python3
"""
LLM 论文每日摘要
使用 Tavily API 获取过去2周最新的、影响力大的LLM论文，优先考虑头部AI大厂
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
import re

# 目标QQ openid
TARGET_QQ = "13E88D8A498827FBD0B939094DDCADFF"

# 头部AI大厂列表
TOP_COMPANIES = [
    "OpenAI", "Google", "DeepMind", "Anthropic", "Meta",
    "Microsoft Research", "Google DeepMind", "Google Research",
    "Microsoft", "FAIR", "AI21 Labs", "Mistral AI"
]

# Tavily 搜索关键词
PAPER_KEYWORDS = [
    "site:arxiv.org \"large language model\" recent",
    "site:arxiv.org \"foundation model\" 2025",
    "OpenAI research language model",
    "DeepMind publications AI",
    "Google Research \"language model\""
]

def search_with_tavily(query: str, max_results: int = 5) -> List[Dict]:
    """使用 Tavily API 搜索论文"""
    try:
        cmd = [
            "python3", "/home/admin/.openclaw/workspace/skills/tavily-search/skill/scripts/tavily_search.py",
            "--query", query,
            "--max-results", str(max_results),
            "--format", "brave"
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        output = result.stdout.decode('utf-8', errors='ignore')

        if result.returncode == 0 and output:
            # 尝试解析 JSON
            try:
                data = json.loads(output)
                results = data.get("results", [])
                return results if isinstance(results, list) else []
            except json.JSONDecodeError:
                print(f"Tavily returned invalid JSON: {output[:200]}")
                return []

        return []

    except subprocess.TimeoutExpired:
        print(f"Tavily search timeout: {query}")
        return []
    except Exception as e:
        print(f"Tavily search failed: {e}")
        return []

def parse_paper_from_result(result: Dict) -> Optional[Dict]:
    """从搜索结果解析论文信息"""
    if not result:
        return None

    title = result.get("title", "")
    url = result.get("url", "")
    snippet = result.get("snippet", "")

    # 优先选择 arxiv.org 和研究机构的链接
    if not any(domain in url.lower() for domain in ["arxiv.org", "openai.com", "deepmind.com", "research.google.com", "anthropic.com"]):
        return None

    # 检查是否为论文相关
    if not any(kw in title.lower() + snippet.lower() for kw in ["model", "language", "ai", "research", "paper", "learning"]):
        return None

    # 检查是否来自头部大厂
    title_snippet = f"{title} {snippet} {url}".lower()
    from_top_company = any(
        company.lower() in title_snippet
        for company in TOP_COMPANIES
    )

    return {
        "title": title,
        "url": url,
        "snippet": snippet,
        "from_top_company": from_top_company,
        "source": "tavily"
    }

def analyze_innovation(title: str, snippet: str) -> Dict[str, int]:
    """分析创新点"""
    text = f"{title} {snippet}".lower()

    innovation_keywords = {
        "efficiency": ["faster", "efficient", "speed", "latency", "optimization", "reduce", "optimize"],
        "accuracy": ["better", "improved", "state-of-the-art", "sota", "accuracy", "performance", "benchmark"],
        "scalability": ["scale", "large", "billion", "trillion", "parameters", "big", "scaling"],
        "reasoning": ["reasoning", "logic", "thinking", "chain-of-thought", "cot", "inference"],
        "multimodal": ["multimodal", "vision", "audio", "image", "video", "text-to"],
        "safety": ["safety", "alignment", "robust", "reliable", "secure", "harmful", "bias"],
        "cost": ["cheaper", "cost-effective", "reduce cost", "affordable", "inference", "training"]
    }

    innovations = {}
    for category, keywords in innovation_keywords.items():
        count = sum(1 for kw in keywords if kw in text)
        if count > 0:
            innovations[category] = count

    return innovations

def generate_paper_summary(paper: Dict) -> str:
    """生成论文摘要"""
    title = paper.get("title", "")
    url = paper.get("url", "")
    snippet = paper.get("snippet", "")

    # 分析创新点
    innovations = analyze_innovation(title, snippet)

    # 提取摘要要点 - 使用更智能的分割
    sentences = re.split(r'[。.!！]', snippet)
    summary_points = [s.strip() for s in sentences if s.strip()][:3]

    # 构建输出
    output = f"\n📄 **{title}**\n"
    output += f"🔗 链接: {url}\n\n"

    # 创新点
    if innovations:
        output += "💡 **主要创新方向:**\n"
        innovation_desc = {
            "efficiency": "效率提升",
            "accuracy": "精度提升",
            "scalability": "可扩展性",
            "reasoning": "推理能力",
            "multimodal": "多模态能力",
            "safety": "安全性",
            "cost": "成本优化"
        }
        sorted_innovations = sorted(innovations.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_innovations:
            output += f"   • {innovation_desc.get(category, category)}\n"
        output += "\n"

    # 摘要
    if summary_points:
        output += "📝 **摘要:**\n"
        for i, point in enumerate(summary_points, 1):
            output += f"   {i}. {point}\n"
        output += "\n"

    # 来源标识
    if paper.get("from_top_company"):
        output += "✨ **来自头部AI大厂**\n"

    return output

def main():
    """主函数"""
    print("="*80)
    print("LLM 论文每日摘要")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    all_papers = []

    # 使用 Tavily 搜索
    print("\n🔍 使用 Tavily 搜索论文...")
    for keyword in PAPER_KEYWORDS[:3]:
        print(f"  搜索关键词: {keyword}")
        results = search_with_tavily(keyword, max_results=5)

        for result in results:
            paper = parse_paper_from_result(result)
            if paper:
                all_papers.append(paper)

    print(f"  找到 {len(all_papers)} 篇候选论文")

    if not all_papers:
        print("  ⚠️ 未找到论文，尝试备用搜索...")
        # 备用搜索
        backup_query = "arXiv \"large language model\" 2025"
        print(f"  备用搜索: {backup_query}")
        results = search_with_tavily(backup_query, max_results=10)

        for result in results:
            paper = parse_paper_from_result(result)
            if paper:
                all_papers.append(paper)

        print(f"  备用搜索找到 {len(all_papers)} 篇")

    # 去重
    seen_titles = set()
    unique_papers = []
    for paper in all_papers:
        title = paper.get("title", "")
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_papers.append(paper)

    print(f"  去重后 {len(unique_papers)} 篇")

    # 优先选择头部大厂的论文
    top_company_papers = [p for p in unique_papers if p.get("from_top_company")]
    other_papers = [p for p in unique_papers if not p.get("from_top_company")]

    # 选择最多2篇论文
    selected_papers = []
    selected_papers.extend(top_company_papers[:2])
    if len(selected_papers) < 2 and other_papers:
        remaining = 2 - len(selected_papers)
        selected_papers.extend(other_papers[:remaining])

    print(f"  最终选择了 {len(selected_papers)} 篇论文")

    # 生成报告
    message = f"""🤖 LLM 论文每日摘要
━━━━━━━━━━━━━━━━━━
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📅 最新研究精选（最多2篇）
"""

    if selected_papers:
        for i, paper in enumerate(selected_papers, 1):
            message += f"\n【论文 {i}】"
            message += generate_paper_summary(paper)
            message += "\n" + "─"*60 + "\n"
    else:
        message += "\n⚠️ 未找到符合条件的论文\n"

    message += "\n💡 说明: 本报告优先收录头部AI大厂的最新研究"
    message += "\n📚 数据源: Tavily AI 搜索"
    message += "\n━━━━━━━━━━━━━━━━━━"

    # 确保数据目录存在
    import os
    data_dir = "/home/admin/.openclaw/workspace/data"
    os.makedirs(data_dir, exist_ok=True)

    # 保存报告
    report_file = os.path.join(data_dir, "llm_paper_daily_report.json")
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "papers": selected_papers,
        "message": message
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    # 保存QQ消息
    qq_notify_file = os.path.join(data_dir, "qq_llm_paper_notify.json")
    with open(qq_notify_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "target": TARGET_QQ
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 报告已生成")
    print(f"   报告文件: {report_file}")
    print(f"   QQ通知文件: {qq_notify_file}")

    # 打印预览
    print("\n📱 报告预览:")
    print("-"*80)
    print(message)
    print("-"*80)

    return message


if __name__ == "__main__":
    main()