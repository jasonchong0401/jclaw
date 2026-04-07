#!/usr/bin/env python3
"""
LLM论文摘要生成器
从arXiv网站获取最新LLM论文并生成摘要
"""

import json
import os
from datetime import datetime
import re

# 输出文件路径
OUTPUT_FILE = "/home/admin/.openclaw/workspace/data/llm_paper_digest.json"

# 最近几篇论文ID列表（从arXiv cs.CL页面获取）
RECENT_PAPERS = [
    "2604.02324",
    "2604.02319",
    "2604.02209",
    "2604.02200",
    "2604.02194",
    "2604.02178",
    "2604.02176",
    "2604.02171",
    "2604.02156",
    "2604.02155"
]

def parse_paper_details(html_text):
    """从HTML文本中解析论文详情"""
    # 提取标题
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_text, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
        # 移除 arXiv ID 前缀
        title = re.sub(r'^\[\d+\.\d+\]\s*', '', title)
    else:
        title = "Unknown Title"

    # 提取作者
    authors = []
    author_matches = re.findall(r'Authors:\s*(.*?)\s*(?=Subject|Abstract|$)', html_text, re.DOTALL | re.IGNORECASE)
    if author_matches:
        author_text = author_matches[0]
        author_links = re.findall(r'<a[^>]*>([^<]+)</a>', author_text)
        if author_links:
            authors = author_links[:5]  # 最多5个作者

    # 提取摘要
    abstract_match = re.search(r'Abstract:\s*(.*?)\s*(?:Subjects:|Cite as:|$)', html_text, re.DOTALL | re.IGNORECASE)
    if abstract_match:
        abstract = abstract_match.group(1).strip()
        # 移除HTML标签
        abstract = re.sub(r'<[^>]+>', '', abstract)
        abstract = abstract.replace('\n', ' ')
        abstract = ' '.join(abstract.split())
    else:
        abstract = "No abstract available"

    # 提取提交日期
    submitted_match = re.search(r'Submitted\s+(\d+ \w+ \d+)', html_text, re.IGNORECASE)
    if submitted_match:
        submitted_date = submitted_match.group(1)
    else:
        submitted_date = "Unknown"

    return {
        "title": title,
        "authors": authors,
        "published": submitted_date,
        "summary": abstract,
        "url": "",
        "pdf_url": ""
    }

def fetch_paper_from_file(arxiv_id):
    """从保存的HTML文件中获取论文信息"""
    file_path = f"/home/admin/.openclaw/workspace/data/arxiv_papers/{arxiv_id}.html"

    if not os.path.exists(file_path):
        print(f"  ⚠ 文件不存在: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        paper = parse_paper_details(html_content)
        paper["arxiv_id"] = arxiv_id
        paper["url"] = f"https://arxiv.org/abs/{arxiv_id}"
        paper["pdf_url"] = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        return paper
    except Exception as e:
        print(f"  ❌ 解析失败 {arxiv_id}: {e}")
        return None

def get_latest_llm_papers(limit=10):
    """获取最新的LLM论文"""
    print(f"正在获取最新LLM论文（最多{limit}篇）...")

    papers = []
    for arxiv_id in RECENT_PAPERS[:limit]:
        print(f"  获取论文 {arxiv_id}...")
        paper = fetch_paper_from_file(arxiv_id)
        if paper:
            papers.append(paper)
            print(f"    ✓ {paper['title'][:50]}...")

    return papers

def save_papers(papers):
    """保存论文数据到JSON文件"""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(papers),
        "papers": papers
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 已保存 {len(papers)} 篇论文到 {OUTPUT_FILE}")
    return data

def main():
    print("=" * 60)
    print("LLM 论文摘要生成器")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 创建目录
    os.makedirs("/home/admin/.openclaw/workspace/data/arxiv_papers", exist_ok=True)

    # 获取论文
    papers = get_latest_llm_papers(limit=5)

    if not papers:
        print("\n⚠ 未找到论文")
        save_papers([])
        return 0

    # 保存论文
    save_papers(papers)

    # 打印摘要
    print(f"\n📊 论文摘要 ({len(papers)}篇):")
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   作者: {', '.join(paper['authors'][:3])}{'等' if len(paper['authors']) > 3 else ''}")
        print(f"   日期: {paper['published']}")
        print(f"   链接: {paper['url']}")

    return 0

if __name__ == "__main__":
    exit(main())